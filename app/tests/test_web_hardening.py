"""Regression tests for the production/security repair run (TI-02/03/05/07/09/10/21/26, CONTENT-01, METADATA-01, CITE-01).

Most tests run against the composed application from ``create_app`` (see ``real_app_factory`` in conftest.py),
because the invariants live in its security headers, error handlers and blueprint wiring.
"""

from __future__ import annotations

from datetime import datetime, timezone
import os
from pathlib import Path
import re
import sys
from urllib.parse import urlparse

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
os.environ.setdefault("FLASK_ENV", "development")
os.environ.setdefault("PROMAT_RUNTIME_ROOT", str(Path(__file__).resolve().parents[2]))
os.environ.setdefault("PROMAT_PUBLIC_ROOT", str(Path(__file__).resolve().parents[2] / "public"))

TESTS_ROOT = Path(__file__).resolve().parent
REPO_ROOT = TESTS_ROOT.parents[1]
STATIC_JS_ROOT = REPO_ROOT / "app" / "static" / "js"
TEACHING_ROOT = REPO_ROOT / "content" / "teaching"

PROD_ENV = {
    "AUTH_ACCESS_REQUEST_EMAIL": "ops@promat.test",
    "AUTH_ACCESS_REQUEST_FROM_EMAIL": "noreply@promat.test",
    "AUTH_ACCESS_REQUEST_SMTP_HOST": "smtp.promat.test",
    "RATE_LIMIT_STORAGE_URI": "redis://127.0.0.1:1/0",
    "FLASK_SESSION_SECURE": "false",
}


def _production_app_without_limiter(real_app_factory, extra_env: dict[str, str] | None = None):
    """Production composition (non-debug) with the limiter off: its Redis is a dead address and a refused connection is slow on Windows."""
    from app.extensions import limiter

    flask_app = real_app_factory(env_name="production", env=PROD_ENV | (extra_env or {}))
    limiter.enabled = False
    return flask_app


def _add_user(*, user_id: str = "user-1", username: str = "alice", role: str = "user") -> None:
    from app.auth import services as auth_services
    from app.auth.models import User
    from app.extensions.sqlalchemy_ext import get_session

    now = datetime.now(timezone.utc)
    with get_session() as session:
        session.add(
            User(
                id=user_id,
                username=username,
                email=f"{username}@example.org",
                password_hash=auth_services.hash_password("ValidPass1"),
                role=role,
                is_active=True,
                must_reset_password=False,
                created_at=now,
                updated_at=now,
                first_name="Alice",
                last_name="Example",
                display_name="Alice Example",
            )
        )


def _logged_in_client(flask_app, *, user_id: str = "user-1", username: str = "alice", role: str = "user"):
    with flask_app.app_context():
        _add_user(user_id=user_id, username=username, role=role)
    client = flask_app.test_client()
    response = client.post("/auth/login", data={"email": f"{username}@example.org", "password": "ValidPass1"})
    assert response.status_code == 303
    return client


# --- TI-02: no profiling hook ---------------------------------------------------------------------------------


def test_player_route_never_registers_engine_listeners(real_app_factory) -> None:
    from app.extensions.sqlalchemy_ext import get_engine

    flask_app = real_app_factory()
    client = flask_app.test_client()
    engine = get_engine()
    before = (len(engine.dispatch.before_cursor_execute), len(engine.dispatch.after_cursor_execute))

    paths = (
        "/xx/research/spanish/player/a/b?_profile=1",
        "/de/research/nolang/player/a/b?_profile=1",
        "/de/research/spanish/player/a/wordlist?_profile=1",
    )
    for _ in range(40):
        for path in paths:
            client.get(path, headers={"X-Promat-Profile": "1"})

    after = (len(engine.dispatch.before_cursor_execute), len(engine.dispatch.after_cursor_execute))
    assert after == before


def test_profiling_hook_is_gone_from_production_code() -> None:
    source = (REPO_ROOT / "app" / "src" / "app" / "routes" / "public.py").read_text(encoding="utf-8")

    assert "_profile=" not in source and "\"_profile\"" not in source
    assert "player_profile" not in source
    assert "X-Promat-Profile" not in source
    assert "event.listen" not in source


# --- TI-03: return targets ------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "raw",
    [
        "////evil.example",
        "////evil.example/pwn",
        "///evil.example",
        "//evil.example",
        "/%2F%2Fevil.example",
        "/%2F%2F%2Fevil.example",
        "/%2F/evil.example",
        "/%252F%252Fevil.example",
        "/%25252F%25252Fevil.example",
        "%2F%2Fevil.example",
        "/\\evil.example",
        "\\\\evil.example",
        "/%5Cevil.example",
        "/%255Cevil.example",
        "https://evil.example/x",
        "http://evil.example",
        "javascript:alert(1)",
        "data:text/html,x",
        "/de/ok\r\nSet-Cookie: x=1",
        "/de/ok%0d%0aSet-Cookie:x=1",
        "/de/ok\tx",
        "/login",
        "/auth/logout",
        "/access-request",
        "relative/path",
        "",
        None,
    ],
)
def test_return_target_rejects_unsafe_values(raw) -> None:
    from app.return_targets import safe_return_target

    assert safe_return_target(raw, host="promat.test") is None


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("/de/research/spanish/speakers", "/de/research/spanish/speakers"),
        ("/de/research/spanish/player/ES-L-0001-2026-S01/wordlist?source=speakers&set_id=abc", "/de/research/spanish/player/ES-L-0001-2026-S01/wordlist?source=speakers&set_id=abc"),
        ("/en/research/spanish/comparison?preset_id=x", "/en/research/spanish/comparison?preset_id=x"),
        ("https://promat.test/de/teaching", "/de/teaching"),
        ("/de/teaching/spanish/which-pronunciation", "/de/teaching/spanish/which-pronunciation"),
        ("/%2Fde/teaching", None),
    ],
)
def test_return_target_keeps_legitimate_internal_targets(raw, expected) -> None:
    from app.return_targets import safe_return_target

    assert safe_return_target(raw, host="promat.test") == expected


def test_both_login_entry_points_share_the_single_validator() -> None:
    auth_source = (REPO_ROOT / "app" / "src" / "app" / "routes" / "auth.py").read_text(encoding="utf-8")
    public_source = (REPO_ROOT / "app" / "src" / "app" / "routes" / "public.py").read_text(encoding="utf-8")

    for source in (auth_source, public_source):
        assert "safe_return_target" in source
        assert "urlparse(unquote(raw" not in source


@pytest.mark.parametrize("payload", ["////evil.example/pwn", "/%2F%2F%2Fevil.example", "/%2F/evil.example", "/\\evil.example"])
def test_authenticated_redirects_never_leave_the_site(real_app_factory, payload: str) -> None:
    flask_app = real_app_factory()
    client = _logged_in_client(flask_app)

    for path in (f"/login?next={payload}", f"/access-request?next={payload}"):
        response = client.get(path)
        assert response.status_code == 303
        location = response.headers["Location"]
        assert location.startswith("/") and not location.startswith("//"), (path, location)
        assert "evil.example" not in location

    fresh = flask_app.test_client()
    login = fresh.post("/auth/login", data={"email": "alice@example.org", "password": "ValidPass1", "next": payload})
    assert login.status_code == 303
    assert not login.headers["Location"].startswith("//")
    assert "evil.example" not in login.headers["Location"]


def test_login_keeps_a_legitimate_next_target(real_app_factory) -> None:
    flask_app = real_app_factory()
    with flask_app.app_context():
        _add_user()
    client = flask_app.test_client()

    login = client.post(
        "/auth/login",
        data={"email": "alice@example.org", "password": "ValidPass1", "next": "/de/research/spanish/speakers?x=1"},
    )

    assert login.headers["Location"] == "/de/research/spanish/speakers?x=1"


# --- TI-05: cache rules for protected responses ---------------------------------------------------------------


def test_protected_html_and_json_are_private_no_store(real_app_factory) -> None:
    flask_app = real_app_factory()
    client = _logged_in_client(flask_app)

    html = client.get("/de/research/spanish/speakers")
    assert html.status_code == 200
    assert html.headers["Cache-Control"] == "private, no-store"
    assert "Cookie" in html.headers["Vary"]

    api = client.get("/api/research/sets?corpus_language=spanish")
    assert api.status_code == 200
    assert api.headers["Cache-Control"] == "private, no-store"
    assert "Cookie" in api.headers["Vary"]

    assert client.get("/auth/account").headers["Cache-Control"] == "private, no-store"


def test_protected_audio_is_private_not_publicly_cacheable(tmp_path: Path, real_app_factory) -> None:
    flask_app = real_app_factory()
    from flask import Response

    @flask_app.get("/__audio-probe")
    def _audio_probe() -> Response:
        from flask import g

        g.promat_protected_response = True
        return Response(b"ID3", mimetype="audio/mpeg")

    response = flask_app.test_client().get("/__audio-probe")

    assert response.headers["Cache-Control"] == "private, no-cache"
    assert "Cookie" in response.headers["Vary"]
    assert "no-store" not in response.headers["Cache-Control"]


def test_public_pages_and_static_assets_are_not_forced_to_no_store(real_app_factory) -> None:
    flask_app = real_app_factory()
    client = flask_app.test_client()

    for path in ("/de", "/de/teaching", "/de/research/spanish/design", "/static/js/logout.js"):
        response = client.get(path)
        assert response.status_code == 200, path
        assert "no-store" not in response.headers.get("Cache-Control", ""), path


def test_logout_makes_the_protected_page_unreachable_and_the_response_uncacheable(real_app_factory) -> None:
    flask_app = real_app_factory()
    client = _logged_in_client(flask_app)

    protected = client.get("/de/research/spanish/speakers")
    assert "no-store" in protected.headers["Cache-Control"]
    assert client.post("/auth/logout").status_code == 303

    after = client.get("/de/research/spanish/speakers")
    assert after.status_code == 302
    assert after.headers["Location"].startswith("/login")


# --- TI-26: logout --------------------------------------------------------------------------------------------


def test_logout_is_post_only(real_app_factory) -> None:
    flask_app = real_app_factory()
    client = _logged_in_client(flask_app)

    assert client.get("/auth/logout").status_code == 405
    assert client.get("/auth/logout_any").status_code == 405
    # A GET must not have signed the user out.
    assert client.get("/auth/session").get_json()["authenticated"] is True

    response = client.post("/auth/logout")
    assert response.status_code == 303
    assert "access_token_cookie=;" in "\n".join(response.headers.getlist("Set-Cookie"))
    assert client.get("/auth/session").get_json()["authenticated"] is False


def test_logout_requires_the_csrf_token_when_a_session_cookie_is_present(real_app_factory) -> None:
    flask_app = _production_app_without_limiter(real_app_factory)
    with flask_app.app_context():
        _add_user()
    client = flask_app.test_client()
    login = client.post("/auth/login", data={"email": "alice@example.org", "password": "ValidPass1"}, base_url="https://promat.test")
    assert login.status_code == 303
    csrf_cookie = next(cookie.value for cookie in client._cookies.values() if cookie.key == "csrf_access_token")

    forged = client.post("/auth/logout", base_url="https://promat.test")
    assert forged.status_code == 403

    legit = client.post("/auth/logout", headers={"X-CSRF-TOKEN": csrf_cookie}, base_url="https://promat.test")
    assert legit.status_code == 303


def test_logout_clears_an_expired_or_garbage_cookie_without_error(real_app_factory) -> None:
    flask_app = real_app_factory()
    client = flask_app.test_client()
    client.set_cookie("access_token_cookie", "not-a-jwt")

    assert client.post("/auth/logout").status_code == 303


def test_frontend_logout_uses_post_and_has_no_get_fallback() -> None:
    script = (STATIC_JS_ROOT / "logout.js").read_text(encoding="utf-8")

    assert "method = 'POST'" in script
    assert "window.location.href = url" not in script
    for template in ("_top_app_bar.html", "_navigation_drawer.html"):
        source = (REPO_ROOT / "app" / "templates" / "partials" / template).read_text(encoding="utf-8")
        assert 'data-logout-method="POST"' in source
        assert "href=\"{{ url_for('auth.logout_any'" not in source


# --- TI-07: analytics only on public pages --------------------------------------------------------------------

GOATCOUNTER_ENV = {"VITE_GOATCOUNTER_URL": "https://pronunciation-matters.goatcounter.com/count"}


@pytest.fixture
def analytics_app(real_app_factory):
    return _production_app_without_limiter(real_app_factory, GOATCOUNTER_ENV)


@pytest.mark.parametrize(
    "path",
    [
        "/de",
        "/en",
        "/de/project",
        "/de/teaching",
        "/en/teaching/spanish/which-pronunciation",
        "/de/research",
        "/de/research/spanish",
        "/de/research/spanish/design",
        "/en/research/french/design",
        "/de/impressum",
        "/en/privacy",
    ],
)
def test_goatcounter_loads_on_public_pages(analytics_app, path: str) -> None:
    response = analytics_app.test_client().get(path)

    assert response.status_code == 200, path
    assert "gc.zgo.at/count.js" in response.get_data(as_text=True), path
    assert "https://gc.zgo.at" in response.headers["Content-Security-Policy"]


@pytest.mark.parametrize(
    "path",
    [
        "/de/research/spanish/speakers",
        "/de/research/spanish/speakers/ES-L-0001",
        "/de/research/spanish/player/ES-L-0001-2026-S01/wordlist",
        "/de/research/spanish/comparison",
        "/de/research/spanish/phenomena",
        "/de/research/french/speakers",
        "/en/research/english/comparison",
        "/auth/account",
        "/login",
    ],
)
def test_goatcounter_is_never_loaded_on_protected_or_account_pages(analytics_app, path: str) -> None:
    client = _logged_in_client(analytics_app)
    for response in (client.get(path), analytics_app.test_client().get(path)):
        body = response.get_data(as_text=True)
        assert "gc.zgo.at" not in body, path
        assert "goatcounter" not in body.lower(), path
        assert "gc.zgo.at" not in response.headers["Content-Security-Policy"], path
        assert "goatcounter" not in response.headers["Content-Security-Policy"].lower(), path


def test_csp_is_closed_when_analytics_is_not_configured(real_app_factory) -> None:
    csp = real_app_factory().test_client().get("/de").headers["Content-Security-Policy"]

    assert "gc.zgo.at" not in csp
    assert "goatcounter" not in csp
    assert "script-src 'self';" in csp


# --- TI-09: set API error handling ----------------------------------------------------------------------------


@pytest.fixture
def set_client(real_app_factory, fixture_runtime_root):
    flask_app = real_app_factory(runtime_root=fixture_runtime_root)
    client = _logged_in_client(flask_app)
    created = client.post("/api/research/sets", json={"corpus_language": "spanish", "label": "Mein Set"})
    assert created.status_code == 201, created.get_data(as_text=True)
    return client, created.get_json()["set"]["set_id"], flask_app


def test_unknown_task_in_set_items_is_400_not_500(set_client) -> None:
    client, set_id, _ = set_client

    response = client.put(f"/api/research/sets/{set_id}/items", json={"items": [{"task": "bogus", "item_id": "wl_059"}]})

    assert response.status_code == 400
    assert "bogus" in response.get_json()["error"]


@pytest.mark.parametrize(
    "kwargs",
    [
        {"json": {}},
        {"json": {"sessions": []}},
        {"json": {"items": "nope"}},
        {"json": {"items": None}},
        {"data": "not json", "content_type": "text/plain"},
        {"data": "{broken", "content_type": "application/json"},
        {"json": []},
    ],
)
def test_set_items_requires_an_explicit_items_array_and_never_clears_silently(set_client, kwargs) -> None:
    client, set_id, _ = set_client
    seeded = client.put(f"/api/research/sets/{set_id}/items", json={"items": [{"task": "wordlist", "item_id": "wl_059"}]})
    assert seeded.status_code == 200, seeded.get_data(as_text=True)
    items_before = seeded.get_json()["set"]["items"]
    assert items_before

    response = client.put(f"/api/research/sets/{set_id}/items", **kwargs)

    assert response.status_code == 400, kwargs
    assert client.get(f"/api/research/sets/{set_id}").get_json()["set"]["items"] == items_before


def test_set_sessions_requires_an_explicit_sessions_array(set_client) -> None:
    client, set_id, _ = set_client

    assert client.put(f"/api/research/sets/{set_id}/sessions", json={}).status_code == 400
    assert client.put(f"/api/research/sets/{set_id}/sessions", json={"sessions": []}).status_code == 200


def test_an_explicit_empty_items_array_is_still_a_valid_clear(set_client) -> None:
    client, set_id, _ = set_client

    response = client.put(f"/api/research/sets/{set_id}/items", json={"items": []})

    assert response.status_code == 200
    assert response.get_json()["set"]["items"] == []


def test_set_label_and_note_have_length_limits(set_client) -> None:
    client, set_id, _ = set_client

    assert client.patch(f"/api/research/sets/{set_id}", json={"label": "x" * 201}).status_code == 400
    assert client.patch(f"/api/research/sets/{set_id}", json={"note": "n" * 4001}).status_code == 400
    assert client.post("/api/research/sets", json={"corpus_language": "spanish", "label": "x" * 5000}).status_code == 400
    ok = client.patch(f"/api/research/sets/{set_id}", json={"label": "x" * 200, "note": "n" * 4000})
    assert ok.status_code == 200


def test_oversized_body_gets_a_clean_413_json_and_html(real_app_factory) -> None:
    flask_app = real_app_factory(env={"MAX_CONTENT_LENGTH": "2048"})
    assert flask_app.config["MAX_CONTENT_LENGTH"] == 2048
    client = _logged_in_client(flask_app)

    api = client.post("/api/research/sets", json={"corpus_language": "spanish", "label": "ok", "note": "x" * 5000})
    assert api.status_code == 413
    assert api.get_json()["error"]

    form = flask_app.test_client().post("/access-request", data={"purpose": "x" * 5000}, headers={"Accept": "text/html"})
    assert form.status_code == 413
    assert "413" in form.get_data(as_text=True)
    assert "Traceback" not in form.get_data(as_text=True)


def test_default_request_body_limit_is_set(real_app_factory) -> None:
    assert real_app_factory().config["MAX_CONTENT_LENGTH"] == 1024 * 1024


# --- TI-10/TI-23: Redis outage and /ready ---------------------------------------------------------------------


def test_redis_outage_keeps_pages_up_and_ready_reports_not_ready(real_app_factory) -> None:
    flask_app = real_app_factory(env_name="production", env=PROD_ENV)
    client = flask_app.test_client()

    for path in ("/de", "/de/teaching", "/de/research/spanish/design", "/health"):
        assert client.get(path).status_code == 200, path
    login = client.post("/auth/login", data={"email": "nobody@example.org", "password": "x"})
    assert login.status_code == 401

    # The outage must be visible in the production app log (not only in a captured test logger).
    for handler in flask_app.logger.handlers:
        handler.flush()
    log_text = (Path(flask_app.config["LOGS_DIR"]) / "promat-web.log").read_text(encoding="utf-8")
    # Either the limiter swallowed the storage error itself, or the health monitor had already noticed the outage.
    assert "Failed to rate limit. Swallowing error" in log_text or "Rate-limit storage is unavailable" in log_text

    ready = client.get("/ready")
    assert ready.status_code == 503
    payload = ready.get_json()
    assert payload["status"] == "not_ready"
    assert payload["checks"]["rate_limit_backend"]["ok"] is False
    assert payload["checks"]["auth_db"]["ok"] is True


def test_ready_response_never_contains_exception_or_host_details(real_app_factory) -> None:
    flask_app = real_app_factory(env_name="production", env=PROD_ENV)

    body = flask_app.test_client().get("/ready").get_data(as_text=True)

    for leaked in ("127.0.0.1", "Connection refused", "Error", "sqlite", "Traceback", str(Path(flask_app.config["LOGS_DIR"]))):
        assert leaked not in body, leaked


def test_ready_does_not_write_a_probe_file(real_app_factory) -> None:
    flask_app = real_app_factory()
    logs_dir = Path(flask_app.config["LOGS_DIR"])
    before = sorted(path.name for path in logs_dir.iterdir())

    flask_app.test_client().get("/ready")

    assert sorted(path.name for path in logs_dir.iterdir()) == before
    assert not (logs_dir / ".promat-ready-probe").exists()


def test_ready_is_ready_with_a_healthy_backend(real_app_factory) -> None:
    response = real_app_factory().test_client().get("/ready")

    assert response.status_code == 200
    assert response.get_json()["status"] == "ready"


# --- TI-21: teaching media route ------------------------------------------------------------------------------


def _public_media_file() -> tuple[str, str, str, str] | None:
    for media_file in sorted(TEACHING_ROOT.glob("*/*/media/*/**/*")):
        teaching_lang, topic_slug, _, media_type, *rest = media_file.relative_to(TEACHING_ROOT).parts
        if media_file.is_file() and media_type in {"audio", "downloads", "images", "video"}:
            return teaching_lang, topic_slug, media_type, "/".join(rest)
    return None


def test_public_teaching_media_is_still_served(real_app_factory) -> None:
    media = _public_media_file()
    assert media is not None, "the content tree is expected to contain at least one released media file"
    teaching_lang, topic_slug, media_type, filename = media
    from app.teaching_content import topic_has_public_edition

    assert topic_has_public_edition(teaching_lang, topic_slug)
    response = real_app_factory().test_client().get(f"/teaching-media/{teaching_lang}/{topic_slug}/{media_type}/{filename}")

    assert response.status_code == 200
    assert len(response.data) > 0


@pytest.mark.parametrize(
    "path",
    [
        "/teaching-media/../private/audio/x.mp3",
        "/teaching-media/spanish/../french/liaison/audio/x.mp3",
        "/teaching-media/spanish/which-pronunciation/../r/audio/x.mp3",
        "/teaching-media/spanish/which-pronunciation/audio/../../../r/de.yaml",
        "/teaching-media/spanish/which-pronunciation/audio/..%2f..%2f..%2fr%2fde.yaml",
        "/teaching-media/spanish/which-pronunciation/audio/%2e%2e/%2e%2e/de.yaml",
        "/teaching-media/Spanish/which-pronunciation/audio/x.mp3",
        "/teaching-media/spanish%2f..%2ffrench/liaison/audio/x.mp3",
        "/teaching-media/spanish/WHICH_pronunciation/audio/x.mp3",
        "/teaching-media/spanish/.hidden/audio/x.mp3",
        "/teaching-media/spanish/which-pronunciation/media/audio/x.mp3",
        "/teaching-media/nonexistent/which-pronunciation/audio/x.mp3",
    ],
)
def test_teaching_media_route_rejects_traversal_and_unknown_identifiers(real_app_factory, path: str) -> None:
    assert real_app_factory().test_client().get(path).status_code == 404


def test_teaching_media_resolver_validates_identifiers_before_touching_the_filesystem() -> None:
    from app.teaching_content import resolve_teaching_topic_media_artifact

    for lang, slug in (("../spanish", "which-pronunciation"), ("spanish", "../french"), ("spanish/", "x"), ("", "x"), ("spanish", ""), ("Spanish", "x")):
        assert resolve_teaching_topic_media_artifact(lang, slug, "audio", "x.mp3") is None, (lang, slug)


def test_media_of_unfinished_topics_is_not_served_publicly(real_app_factory, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import app.teaching_content as teaching

    root = tmp_path / "teaching"
    topic_dir = root / "spanish" / "scaffold-topic"
    (topic_dir / "media" / "audio").mkdir(parents=True)
    (topic_dir / "media" / "audio" / "x.mp3").write_bytes(b"ID3")
    (root / "spanish" / "teaching.yaml").write_text("teaching_lang: spanish\ndefault_ui_lang: de\navailable_ui_langs: [de]\n", encoding="utf-8")
    (topic_dir / "de.yaml").write_text("title: Entwurf\nstatus: draft\nmetadata:\n  authors: [NN]\n", encoding="utf-8")
    monkeypatch.setattr(teaching, "TEACHING_CONTENT_ROOT", root)
    teaching.clear_teaching_content_caches()
    try:
        response = real_app_factory().test_client().get("/teaching-media/spanish/scaffold-topic/audio/x.mp3")
        assert response.status_code == 404
    finally:
        teaching.clear_teaching_content_caches()


# --- CONTENT-01: draft / placeholder topics are not public ----------------------------------------------------

PLACEHOLDER_MARKERS = (
    "Hier kann später",
    "Hier können später",
    "noch nicht hinterlegt",
    "can be added here later",
    "can later be summarized",
    "have not yet been added",
    "has not yet been added",
)


def _topic_editions() -> list[tuple[str, str, str, dict]]:
    editions = []
    for path in sorted(TEACHING_ROOT.glob("*/*/??.yaml")):
        teaching_lang, topic_slug, ui_file = path.relative_to(TEACHING_ROOT).parts
        if topic_slug == "hubs":
            continue
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        editions.append((teaching_lang, topic_slug, ui_file.removesuffix(".yaml"), data))
    return editions


def _is_marked_unfinished(topic: dict) -> bool:
    hub = topic.get("hub") if isinstance(topic.get("hub"), dict) else {}
    metadata = topic.get("metadata") if isinstance(topic.get("metadata"), dict) else {}
    authors = [str(author).strip().lower() for author in (metadata.get("authors") or [])]
    return (
        str(topic.get("status", "")).lower() == "draft"
        or str(hub.get("status", "")).lower() == "draft"
        or topic.get("is_public") is False
        or (bool(authors) and set(authors) <= {"nn"})
    )


def test_the_content_tree_contains_both_finished_and_unfinished_topics() -> None:
    editions = _topic_editions()

    assert any(_is_marked_unfinished(topic) for *_, topic in editions)
    assert any(not _is_marked_unfinished(topic) for *_, topic in editions)


def test_unfinished_topics_are_neither_linked_nor_served_and_finished_ones_are(real_app_factory) -> None:
    from app.teaching_content import topic_is_public

    client = real_app_factory().test_client()
    hubs: dict[tuple[str, str], str] = {}
    for teaching_lang, topic_slug, ui_lang, topic in _topic_editions():
        hub_html = hubs.setdefault((teaching_lang, ui_lang), client.get(f"/{ui_lang}/teaching/{teaching_lang}").get_data(as_text=True))
        topic_href = f"/{ui_lang}/teaching/{teaching_lang}/{topic_slug}"
        response = client.get(topic_href)
        public = topic_is_public(teaching_lang, ui_lang, topic_slug)

        if _is_marked_unfinished(topic):
            assert not public, topic_href
            assert response.status_code != 200, topic_href
            assert f'href="{topic_href}"' not in hub_html, topic_href
        else:
            assert public, topic_href
            assert response.status_code == 200, topic_href
            assert f'href="{topic_href}"' in hub_html, topic_href


def test_public_topics_carry_no_placeholder_author_status_or_scaffold_text(real_app_factory) -> None:
    client = real_app_factory().test_client()
    for teaching_lang, topic_slug, ui_lang, topic in _topic_editions():
        if _is_marked_unfinished(topic):
            continue
        body = client.get(f"/{ui_lang}/teaching/{teaching_lang}/{topic_slug}").get_data(as_text=True)
        assert ">NN<" not in body and "NN</" not in body, (teaching_lang, topic_slug, ui_lang)
        for marker in PLACEHOLDER_MARKERS:
            assert marker not in body, (teaching_lang, topic_slug, ui_lang, marker)


@pytest.mark.parametrize(
    ("topic", "expected"),
    [
        ({"title": "A"}, True),
        ({"title": "A", "status": "draft"}, False),
        ({"title": "A", "status": "Draft"}, False),
        ({"title": "A", "hub": {"status": "draft"}}, False),
        ({"title": "A", "is_public": False}, False),
        ({"title": "A", "is_available": "false"}, False),
        ({"title": "A", "metadata": {"authors": ["NN"]}}, False),
        ({"title": "A", "metadata": {"authors": ["nn", "N.N."]}}, False),
        ({"title": "A", "metadata": {"authors": ["Felix Tacke", "NN"]}}, True),
        ({"title": "A", "metadata": {"authors": ["Felix Tacke"]}}, True),
        ({"title": "A", "status": "published", "metadata": {"authors": ["Felix Tacke"]}}, True),
        ({"title": "A", "is_public": True, "status": "draft"}, False),
    ],
)
def test_topic_publicness_rule(topic: dict, expected: bool) -> None:
    from app.teaching_content import topic_is_public

    assert topic_is_public("spanish", "de", "x", raw_topic=topic) is expected


# --- METADATA-01: document.title ------------------------------------------------------------------------------


def test_no_client_script_rewrites_the_server_title() -> None:
    allowed_title_writers = {"research-player.js"}  # applies the title of a fetched server page after fragment navigation
    offenders = []
    for path in sorted(STATIC_JS_ROOT.rglob("*.js")):
        source = path.read_text(encoding="utf-8")
        if re.search(r"document\.title\s*=(?!=)", source) and path.name not in allowed_title_writers:
            offenders.append(path.name)
    assert offenders == []
    assert not (STATIC_JS_ROOT / "modules" / "navigation" / "page-title.js").exists()
    assert "page-title" not in (STATIC_JS_ROOT / "modules" / "navigation" / "index.js").read_text(encoding="utf-8")
    assert "Pronunciation Matters'" not in (STATIC_JS_ROOT / "modules" / "core" / "ui.js").read_text(encoding="utf-8")


@pytest.mark.parametrize(
    ("path", "needle"),
    [
        ("/de", "Pronunciation Matters"),
        ("/en", "Pronunciation Matters"),
        ("/de/teaching/spanish/which-pronunciation", "Welche Aussprache unterrichten?"),
        ("/en/teaching/spanish/which-pronunciation", "Which pronunciation should you teach?"),
        ("/de/research/spanish/design", "Pronunciation Matters"),
        ("/de/impressum", "Pronunciation Matters"),
        ("/en/privacy", "Pronunciation Matters"),
    ],
)
def test_server_renders_route_specific_titles(real_app_factory, path: str, needle: str) -> None:
    body = real_app_factory().test_client().get(path).get_data(as_text=True)
    title = re.search(r"<title>(.*?)</title>", body, flags=re.S)

    assert title is not None, path
    assert needle in title.group(1), (path, title.group(1))


def test_route_titles_differ_between_pages(real_app_factory) -> None:
    client = real_app_factory().test_client()
    titles = {
        path: re.search(r"<title>(.*?)</title>", client.get(path).get_data(as_text=True), flags=re.S).group(1).strip()
        for path in ("/de/teaching/spanish/which-pronunciation", "/de/research/spanish/design", "/de/impressum", "/de/teaching")
    }

    assert len(set(titles.values())) == len(titles), titles


# --- CITE-01: citation URL points at the cited resource -------------------------------------------------------

CANONICAL_ORIGIN = "https://pronunciation-matters.de"


def test_topic_citation_urls_point_at_their_own_page_on_the_canonical_host(real_app_factory) -> None:
    client = real_app_factory().test_client()
    checked = 0
    for teaching_lang, topic_slug, ui_lang, topic in _topic_editions():
        citation = topic.get("citation")
        if not isinstance(citation, dict):
            continue
        page_path = f"/{ui_lang}/teaching/{teaching_lang}/{topic_slug}"
        for field in ("text", "copy_text"):
            urls = re.findall(r"https?://[^\s)\]]+", citation.get(field, ""))
            assert urls, (page_path, field)
            for url in urls:
                url = url.rstrip(".,;")
                parsed = urlparse(url)
                assert f"{parsed.scheme}://{parsed.netloc}" == CANONICAL_ORIGIN, (page_path, url)
                assert "www." not in parsed.netloc
                assert parsed.path == page_path, (page_path, url)
                response = client.get(parsed.path)
                assert response.status_code == 200, (page_path, url)
        checked += 1
    assert checked >= 2, "the which-pronunciation page (de, en) is expected to carry a citation"


def test_rendered_citation_box_exposes_the_page_url(real_app_factory) -> None:
    client = real_app_factory().test_client()
    for ui_lang in ("de", "en"):
        body = client.get(f"/{ui_lang}/teaching/spanish/which-pronunciation").get_data(as_text=True)
        copy_texts = re.findall(r'data-copy-text="([^"]*)"', body)

        assert copy_texts, ui_lang
        assert any(f"{CANONICAL_ORIGIN}/{ui_lang}/teaching/spanish/which-pronunciation" in text for text in copy_texts), ui_lang
        assert not any("www.pronunciation-matters.de" in text for text in copy_texts)
        assert not any(text.rstrip(".").endswith("pronunciation-matters.de") for text in copy_texts)


def test_set_api_does_not_expose_account_ids(set_client) -> None:
    client, set_id, _ = set_client

    for response in (client.get(f"/api/research/sets/{set_id}"), client.get("/api/research/sets?corpus_language=spanish")):
        body = response.get_data(as_text=True)
        assert "created_by_user_id" not in body
        assert "updated_by_user_id" not in body
        assert "user-1" not in body
