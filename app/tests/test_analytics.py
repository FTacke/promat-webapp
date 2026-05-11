from __future__ import annotations

import os
import sys
from contextlib import contextmanager
from datetime import date, datetime, timezone
from pathlib import Path

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
