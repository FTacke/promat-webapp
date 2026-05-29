from __future__ import annotations

import json
import os
import sys
from contextlib import contextmanager
from datetime import date, datetime, timezone
from pathlib import Path
from types import SimpleNamespace

import flask
import pytest
from sqlalchemy.exc import IntegrityError


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

TEST_REPO_ROOT = Path(__file__).resolve().parents[2]
os.environ.setdefault("FLASK_ENV", "development")
os.environ.setdefault("PROMAT_RUNTIME_ROOT", str(TEST_REPO_ROOT))
os.environ.setdefault("PROMAT_PUBLIC_ROOT", str(TEST_REPO_ROOT / "public"))

from app import analytics


class _FakeScalarResult:
    def __init__(self, value):
        self._value = value

    def first(self):
        return self._value


class _FakeExecuteResult:
    def __init__(self, value):
        self._value = value

    def scalars(self):
        return _FakeScalarResult(self._value)


class _FakeSession:
    def __init__(self, *, flush_error: IntegrityError | None = None):
        self.flush_error = flush_error
        self.flush_calls = 0
        self.added = []

    def execute(self, _statement):
        return _FakeExecuteResult(None)

    def add(self, obj) -> None:
        self.added.append(obj)

    def flush(self) -> None:
        self.flush_calls += 1
        if self.flush_error is not None:
            raise self.flush_error


def _build_get_session(sessions: list[_FakeSession]):
    @contextmanager
    def _fake_get_session():
        session = sessions.pop(0)
        yield session

    return _fake_get_session


def test_is_retryable_analytics_integrity_error_is_narrow() -> None:
    retryable = IntegrityError(
        "insert",
        {},
        Exception('duplicate key value violates unique constraint "analytics_language_area_daily_pkey"'),
    )
    unrelated = IntegrityError(
        "insert",
        {},
        Exception('duplicate key value violates unique constraint "some_other_constraint"'),
    )

    assert analytics._is_retryable_analytics_integrity_error(retryable) is True
    assert analytics._is_retryable_analytics_integrity_error(unrelated) is False


def test_bump_analytics_counters_retries_once_for_known_duplicate_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    first_session = _FakeSession(
        flush_error=IntegrityError(
            "insert",
            {},
            Exception('duplicate key value violates unique constraint "analytics_language_area_daily_pkey"'),
        )
    )
    second_session = _FakeSession()
    sessions = [first_session, second_session]

    monkeypatch.setattr(analytics, "get_session", _build_get_session(sessions))
    monkeypatch.setattr(analytics, "_today_utc", lambda: date(2026, 5, 11))
    monkeypatch.setattr(
        analytics,
        "_now_utc",
        lambda: datetime(2026, 5, 11, 9, 0, 0, tzinfo=timezone.utc),
    )

    analytics._bump_analytics_counters(
        {"section": "teaching", "corpus_language": "spanish"},
        {"all", "teaching:spanish"},
    )

    assert first_session.flush_calls == 1
    assert second_session.flush_calls == 1
    assert sessions == []


def test_bump_analytics_counters_reraises_unrelated_integrity_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = _FakeSession(
        flush_error=IntegrityError(
            "insert",
            {},
            Exception('duplicate key value violates unique constraint "some_other_constraint"'),
        )
    )

    monkeypatch.setattr(analytics, "get_session", _build_get_session([session]))
    monkeypatch.setattr(analytics, "_today_utc", lambda: date(2026, 5, 11))
    monkeypatch.setattr(
        analytics,
        "_now_utc",
        lambda: datetime(2026, 5, 11, 9, 0, 0, tzinfo=timezone.utc),
    )

    with pytest.raises(IntegrityError):
        analytics._bump_analytics_counters(
            {"section": "teaching", "corpus_language": "spanish"},
            {"all", "teaching:spanish"},
        )

    assert session.flush_calls == 1


# ---------------------------------------------------------------------------
# Helpers for request-context tests
# ---------------------------------------------------------------------------

_test_app = flask.Flask(__name__)
_test_app.config.update({"TESTING": True, "SESSION_COOKIE_SECURE": False})


def _html_response(status: int = 200) -> flask.Response:
    return flask.Response("<html>", status=status, content_type="text/html")


def _ctx(path: str, *, ua: str = "Mozilla/5.0", cookie: str | None = None):
    environ: dict = {}
    if cookie is not None:
        environ["HTTP_COOKIE"] = f"{analytics.ANALYTICS_COOKIE_NAME}={cookie}"
    return _test_app.test_request_context(
        path,
        method="GET",
        headers={"User-Agent": ua},
        environ_base=environ or None,
    )


def _build_summary_get_session(daily_rows, area_rows):
    class _Scalars:
        def __init__(self, rows):
            self._rows = rows

        def all(self):
            return self._rows

    class _Result:
        def __init__(self, rows):
            self._rows = rows

        def scalars(self):
            return _Scalars(self._rows)

    @contextmanager
    def _fake():
        calls = [0]

        class _Session:
            def execute(self, _stmt):
                calls[0] += 1
                return _Result(daily_rows if calls[0] == 1 else area_rows)

        yield _Session()

    return _fake


# ---------------------------------------------------------------------------
# _is_trackable_response: bot UA filtering
# ---------------------------------------------------------------------------


def test_is_trackable_rejects_googlebot():
    with _ctx("/de/research/spanish", ua="Googlebot/2.1 (+http://www.google.com/bot.html)"):
        assert analytics._is_trackable_response() is False


def test_is_trackable_rejects_generic_crawler():
    with _ctx("/de/research/spanish", ua="AcmeWebCrawler/1.0"):
        assert analytics._is_trackable_response() is False


def test_is_trackable_rejects_spider():
    with _ctx("/de/research/spanish", ua="SomeSpider/2.0"):
        assert analytics._is_trackable_response() is False


def test_is_trackable_rejects_python_requests():
    with _ctx("/de/research/spanish", ua="python-requests/2.28.0"):
        assert analytics._is_trackable_response() is False


def test_is_trackable_rejects_curl():
    with _ctx("/de/research/spanish", ua="curl/7.88.1"):
        assert analytics._is_trackable_response() is False


def test_is_trackable_accepts_real_browser():
    with _ctx("/de/research/spanish", ua="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"):
        assert analytics._is_trackable_response() is True


# ---------------------------------------------------------------------------
# _is_trackable_response: excluded routes
# ---------------------------------------------------------------------------


def test_is_trackable_rejects_admin():
    with _ctx("/admin/analytics"):
        assert analytics._is_trackable_response() is False


def test_is_trackable_rejects_auth():
    with _ctx("/auth/login"):
        assert analytics._is_trackable_response() is False


def test_is_trackable_rejects_api():
    with _ctx("/api/corpora"):
        assert analytics._is_trackable_response() is False


def test_is_trackable_rejects_health():
    with _ctx("/health"):
        assert analytics._is_trackable_response() is False


def test_is_trackable_rejects_robots_txt():
    with _ctx("/robots.txt"):
        assert analytics._is_trackable_response() is False


def test_is_trackable_accepts_content_path():
    with _ctx("/de/project"):
        assert analytics._is_trackable_response() is True


# ---------------------------------------------------------------------------
# track_page_response: unique-visitor counting
# ---------------------------------------------------------------------------


def test_first_visit_increments_global_unique(monkeypatch: pytest.MonkeyPatch):
    """No cookie → 'all' must be in new_unique_keys → unique visitor counted."""
    bumped: list[frozenset] = []
    monkeypatch.setattr(analytics, "_bump_analytics_counters", lambda d, u: bumped.append(frozenset(u)))
    monkeypatch.setattr(analytics, "_today_utc", lambda: date(2026, 5, 29))

    with _ctx("/de/project"):
        analytics.track_page_response(_html_response())

    assert len(bumped) == 1
    assert "all" in bumped[0]


def test_second_page_same_day_no_additional_global_unique(monkeypatch: pytest.MonkeyPatch):
    """Cookie with 'all' already set today → second page must not add another unique."""
    bumped: list[frozenset] = []
    monkeypatch.setattr(analytics, "_bump_analytics_counters", lambda d, u: bumped.append(frozenset(u)))
    monkeypatch.setattr(analytics, "_today_utc", lambda: date(2026, 5, 29))

    state = json.dumps({"days": {"2026-05-29": ["all"]}}, separators=(",", ":"))

    with _ctx("/de/project", cookie=state):
        analytics.track_page_response(_html_response())

    assert len(bumped) == 1
    assert "all" not in bumped[0], "Returning visitor on same day must not re-increment global unique"


def test_visitor_multiple_language_areas_one_global_unique(monkeypatch: pytest.MonkeyPatch):
    """Already globally counted today → area visit adds area unique but NOT global unique."""
    bumped: list[frozenset] = []
    monkeypatch.setattr(analytics, "_bump_analytics_counters", lambda d, u: bumped.append(frozenset(u)))
    monkeypatch.setattr(analytics, "_today_utc", lambda: date(2026, 5, 29))

    state = json.dumps({"days": {"2026-05-29": ["all"]}}, separators=(",", ":"))

    with _ctx("/de/research/spanish", cookie=state):
        analytics.track_page_response(_html_response())

    assert len(bumped) == 1
    assert "all" not in bumped[0], "Global unique must not increment again"
    assert "research:spanish" in bumped[0], "New area unique must be counted"


def test_same_visitor_two_days_counted_once_per_day(monkeypatch: pytest.MonkeyPatch):
    """Returning visitor on day 2 increments per-day unique again (visitor_day_sum += 1 each day).
    This is the intended behaviour and is correctly labelled as a daily sum, not a period unique.
    """
    day1_bumped: list[frozenset] = []
    monkeypatch.setattr(analytics, "_bump_analytics_counters", lambda d, u: day1_bumped.append(frozenset(u)))
    monkeypatch.setattr(analytics, "_today_utc", lambda: date(2026, 5, 28))

    with _ctx("/de/project"):
        analytics.track_page_response(_html_response())

    assert "all" in day1_bumped[0], "Day 1: must count as unique"

    # Day 2: cookie carries previous day's state but today has no 'all' key yet
    day2_bumped: list[frozenset] = []
    monkeypatch.setattr(analytics, "_bump_analytics_counters", lambda d, u: day2_bumped.append(frozenset(u)))
    monkeypatch.setattr(analytics, "_today_utc", lambda: date(2026, 5, 29))

    state = json.dumps({"days": {"2026-05-28": ["all"]}}, separators=(",", ":"))
    with _ctx("/de/project", cookie=state):
        analytics.track_page_response(_html_response())

    assert "all" in day2_bumped[0], "Day 2: must count as daily unique (visitor_day_sum += 1, correctly labelled)"


def test_bot_ua_not_tracked(monkeypatch: pytest.MonkeyPatch):
    """Bot UA must never reach _bump_analytics_counters."""
    bumped: list = []
    monkeypatch.setattr(analytics, "_bump_analytics_counters", lambda d, u: bumped.append(u))

    with _ctx("/de/research/spanish", ua="Googlebot/2.1 (+http://www.google.com/bot.html)"):
        analytics.track_page_response(_html_response())

    assert bumped == []


def test_admin_route_not_tracked(monkeypatch: pytest.MonkeyPatch):
    bumped: list = []
    monkeypatch.setattr(analytics, "_bump_analytics_counters", lambda d, u: bumped.append(u))

    with _ctx("/admin/analytics"):
        analytics.track_page_response(_html_response())

    assert bumped == []


def test_auth_route_not_tracked(monkeypatch: pytest.MonkeyPatch):
    bumped: list = []
    monkeypatch.setattr(analytics, "_bump_analytics_counters", lambda d, u: bumped.append(u))

    with _ctx("/auth/login"):
        analytics.track_page_response(_html_response())

    assert bumped == []


def test_api_route_not_tracked(monkeypatch: pytest.MonkeyPatch):
    bumped: list = []
    monkeypatch.setattr(analytics, "_bump_analytics_counters", lambda d, u: bumped.append(u))

    with _ctx("/api/corpora"):
        analytics.track_page_response(_html_response())

    assert bumped == []


# ---------------------------------------------------------------------------
# summarize_analytics: visitor_day_sum key
# ---------------------------------------------------------------------------


def test_summarize_analytics_returns_visitor_day_sum_not_unique_visitors(monkeypatch: pytest.MonkeyPatch):
    """totals must expose visitor_day_sum and must NOT expose unique_visitors."""
    daily = SimpleNamespace(unique_visitors=7, page_views=20, activity_date=date(2026, 5, 29))

    monkeypatch.setattr(analytics, "get_session", _build_summary_get_session([daily], []))
    monkeypatch.setattr(analytics, "_today_utc", lambda: date(2026, 5, 29))

    result = analytics.summarize_analytics("all")

    assert "visitor_day_sum" in result["totals"], "totals must have visitor_day_sum key"
    assert "unique_visitors" not in result["totals"], "totals must not have misleading unique_visitors key"
    assert result["totals"]["visitor_day_sum"] == 7
    assert result["totals"]["page_views"] == 20
    assert result["totals"]["days_with_activity"] == 1
