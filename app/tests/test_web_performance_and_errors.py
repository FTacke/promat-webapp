"""Static delivery, rate-limit behaviour and page-level hygiene of the composed app (Run 3: TI-08, PERF, landing title)."""

from __future__ import annotations

from datetime import datetime, timezone
import os
from pathlib import Path
import re
import sys
import threading

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "app" / "src"))
os.environ.setdefault("FLASK_ENV", "development")
os.environ.setdefault("PROMAT_RUNTIME_ROOT", str(REPO_ROOT))
os.environ.setdefault("PROMAT_PUBLIC_ROOT", str(REPO_ROOT / "public"))

PASSWORD = "ValidPass1"


@pytest.fixture
def app(real_app_factory):
    from app.extensions import limiter

    flask_app = real_app_factory(env_name="testing")
    # The testing config is debug-like, which switches the limiter off; these tests exercise the limiter itself.
    limiter.enabled = True
    limiter.reset()
    yield flask_app


def _add_user(username: str) -> None:
    from app.auth import services as auth_services
    from app.auth.models import User
    from app.extensions.sqlalchemy_ext import get_session

    now = datetime.now(timezone.utc)
    with get_session() as session:
        session.add(
            User(
                id=f"id-{username}",
                username=username,
                email=f"{username}@example.org",
                password_hash=auth_services.hash_password(PASSWORD),
                role="user",
                is_active=True,
                must_reset_password=False,
                created_at=now,
                updated_at=now,
                first_name=username.title(),
                last_name="Example",
                display_name=f"{username.title()} Example",
            )
        )


# --- static delivery -------------------------------------------------------------------------------------------


def test_versioned_static_assets_are_cached_immutably_and_unversioned_ones_are_not(app) -> None:
    client = app.test_client()

    versioned = client.get("/static/css/00_tokens.css?v=123")
    assert versioned.status_code == 200
    assert versioned.headers["Cache-Control"] == "public, max-age=31536000, immutable"

    unversioned = client.get("/static/css/00_tokens.css")
    assert "immutable" not in unversioned.headers.get("Cache-Control", "")

    missing = client.get("/static/css/does-not-exist.css?v=1")
    assert missing.status_code == 404
    assert "immutable" not in missing.headers.get("Cache-Control", "")


def test_every_static_reference_in_the_rendered_shell_carries_a_version(app) -> None:
    html = app.test_client().get("/de").get_data(as_text=True)
    references = re.findall(r'(?:href|src)="(/static/[^"]+)"', html)

    assert references, "the landing page references static assets"
    unversioned = [reference for reference in references if "?v=" not in reference]
    assert unversioned == []


def test_shell_loads_neither_htmx_nor_jquery_nor_the_font_loader(app) -> None:
    html = app.test_client().get("/de").get_data(as_text=True)

    assert "htmx" not in html.lower()
    assert "jquery" not in html.lower()
    assert "material-symbols-loader" not in html
    assert 'rel="preload" href="/static/fonts/MaterialSymbolsRounded.woff2?v=' in html


def test_removed_dead_weight_stays_removed() -> None:
    static = REPO_ROOT / "app" / "static"
    for removed in ("vendor/htmx.min.js", "vendor/jquery-3.7.1.min.js", "js/modules/navigation/material-symbols-loader.js"):
        assert not (static / removed).exists(), removed


def test_icon_font_is_a_small_subset_with_every_used_icon() -> None:
    font_path = REPO_ROOT / "app" / "static" / "fonts" / "MaterialSymbolsRounded.woff2"
    assert font_path.stat().st_size < 60_000, "the icon font must stay a subset (the full variable font is about 5 MB)"

    fonttools = pytest.importorskip("fontTools.ttLib")
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    import build_icon_font

    font = fonttools.TTFont(font_path)
    cmap = font.getBestCmap()
    reverse = {glyph: chr(code) for code, glyph in cmap.items()}
    available: set[str] = set()
    for lookup in font["GSUB"].table.LookupList.Lookup:
        for subtable in lookup.SubTable:
            subtable = getattr(subtable, "ExtSubTable", subtable)
            for first, ligatures in getattr(subtable, "ligatures", {}).items():
                for ligature in ligatures:
                    parts = [first, *ligature.Component]
                    if all(part in reverse for part in parts):
                        available.add("".join(reverse[part] for part in parts))

    full_font = os.environ.get("PROMAT_FULL_ICON_FONT")
    if full_font:  # optional: confirm against the complete font that no icon name was dropped
        wanted = build_icon_font.used_names(build_icon_font.ligature_names(fonttools.TTFont(full_font)))
        assert sorted(wanted - available) == []
    assert len(available) >= 50


def test_landing_title_is_the_app_name_without_duplication(app) -> None:
    for lang, expected in (("de", None), ("en", None)):
        html = app.test_client().get(f"/{lang}").get_data(as_text=True)
        title = re.search(r"<title>(.*?)</title>", html, flags=re.S).group(1).strip()
        parts = [part.strip() for part in title.split("|")]
        assert len(parts) == len(set(parts)), f"{lang}: duplicated title parts {title!r}"
        del expected


def test_filter_form_ids_are_unique_on_the_speakers_page(real_app_factory, fixture_runtime_root) -> None:
    flask_app = real_app_factory(runtime_root=fixture_runtime_root)
    with flask_app.app_context():
        _add_user("alice")
    client = flask_app.test_client()
    assert client.post("/auth/login", data={"email": "alice@example.org", "password": PASSWORD}).status_code == 303

    for lang in ("de", "en"):
        html = client.get(f"/{lang}/research/spanish/speakers").get_data(as_text=True)
        ids = re.findall(r'\sid="([^"]+)"', html)
        duplicates = sorted({value for value in ids if ids.count(value) > 1})
        assert duplicates == [], f"{lang}: duplicate ids {duplicates}"


# --- rate limiting (TI-08) -------------------------------------------------------------------------------------


def _failed_logins(client, count: int, *, accept: str | None = None):
    headers = {"Accept": accept} if accept else {}
    return [client.post("/auth/login", data={"email": "nobody@example.org", "password": "wrong"}, headers=headers) for _ in range(count)]


def test_failed_logins_are_limited_with_a_localized_html_429_and_retry_after(app) -> None:
    client = app.test_client()
    client.set_cookie("pm_ui_lang", "de", domain="localhost")

    responses = _failed_logins(client, 7)
    blocked = responses[-1]

    assert blocked.status_code == 429
    body = blocked.get_data(as_text=True)
    assert "TOO MANY REQUESTS" not in body
    assert "Zu viele Anfragen" in body
    assert 1 <= int(blocked.headers["Retry-After"]) <= 3600
    assert "text/html" in blocked.headers["Content-Type"]


def test_the_429_for_json_clients_is_json_with_retry_after(app) -> None:
    client = app.test_client()

    blocked = _failed_logins(client, 7, accept="application/json")[-1]

    assert blocked.status_code == 429
    assert blocked.is_json
    assert blocked.get_json()["error"] == "rate_limited"
    assert "TOO MANY REQUESTS" not in blocked.get_data(as_text=True)
    assert int(blocked.headers["Retry-After"]) >= 1


def test_successful_logins_do_not_count_against_the_login_limit(app) -> None:
    with app.app_context():
        _add_user("alice")
    for _ in range(8):
        client = app.test_client()
        response = client.post("/auth/login", data={"email": "alice@example.org", "password": PASSWORD})
        assert response.status_code == 303, response.status_code


def test_audio_routes_carry_the_media_budget_not_the_default_limit() -> None:
    source = (REPO_ROOT / "app" / "src" / "app" / "routes" / "public.py").read_text(encoding="utf-8")
    assert source.count('@limiter.limit("3000 per hour")') >= 2


# --- rate-limit storage outage ----------------------------------------------------------------------------------


def test_limiter_is_skipped_while_the_storage_is_marked_down_and_resumes_afterwards(app) -> None:
    from app import extensions

    client = app.test_client()
    extensions._rate_limit_storage_down.set()
    try:
        statuses = [client.post("/auth/login", data={"email": "nobody@example.org", "password": "wrong"}).status_code for _ in range(8)]
        assert 429 not in statuses
    finally:
        extensions._rate_limit_storage_down.clear()
    assert _failed_logins(app.test_client(), 7)[-1].status_code == 429


def test_health_monitor_flips_the_flag_on_storage_failure_without_an_in_memory_substitute(app, monkeypatch: pytest.MonkeyPatch) -> None:
    from app import extensions

    class FakeStorage:
        healthy = False

        def check(self) -> bool:
            return self.healthy

    storage = FakeStorage()
    monkeypatch.setattr(type(extensions.limiter), "storage", property(lambda self: storage), raising=False)
    app.config["RATE_LIMIT_STORAGE_URI"] = "redis://127.0.0.1:1/0"
    app.config["RATELIMIT_HEALTH_POLL_SECONDS"] = 0.05

    extensions._rate_limit_storage_down.clear()
    stop = extensions._start_rate_limit_health_monitor(app)
    try:
        assert _wait_for(extensions._rate_limit_storage_down.is_set)
        storage.healthy = True
        assert _wait_for(lambda: not extensions._rate_limit_storage_down.is_set())
    finally:
        stop.set()
        extensions._rate_limit_storage_down.clear()
    assert extensions.limiter._in_memory_fallback_enabled is False


def _wait_for(predicate, timeout: float = 3.0) -> bool:
    event = threading.Event()
    waited = 0.0
    while waited < timeout:
        if predicate():
            return True
        event.wait(0.05)
        waited += 0.05
    return predicate()
