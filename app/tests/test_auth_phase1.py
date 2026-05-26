from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
import logging
import os
from pathlib import Path
import re
import sys

from flask import Flask, abort, jsonify, render_template
import pytest
from flask_jwt_extended import jwt_required

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

TEST_REPO_ROOT = Path(__file__).resolve().parents[2]
os.environ.setdefault("FLASK_ENV", "development")
os.environ.setdefault("PROMAT_RUNTIME_ROOT", str(TEST_REPO_ROOT))
os.environ.setdefault("PROMAT_PUBLIC_ROOT", str(TEST_REPO_ROOT / "public"))

from app import register_auth_context, register_context_processors, register_error_handlers, register_security_headers
from app.auth.models import AccessRequest, AnalyticsDaily, AnalyticsLanguageAreaDaily, Base, ResetToken, User
from app.auth import services as auth_services
from app.extensions import limiter, register_extensions
from app.extensions.sqlalchemy_ext import get_engine, get_session, init_engine
from app.routes.admin import blueprint as admin_blueprint
from app.routes.auth import blueprint as auth_blueprint
from app.routes import public as public_routes
from app.routes.public import blueprint as public_blueprint


def _insert_user(
    *,
    user_id: str,
    username: str,
    email: str,
    first_name: str = "",
    last_name: str = "",
    role: str = "user",
    is_active: bool = True,
    access_expires_at: datetime | None = None,
    created_by_user_id: str | None = None,
) -> None:
    now = datetime.now(timezone.utc)
    with get_session() as session:
        session.add(
            User(
                id=user_id,
                username=username,
                email=email,
                password_hash=auth_services.hash_password("ValidPass1"),
                role=role,
                is_active=is_active,
                must_reset_password=False,
                created_at=now,
                updated_at=now,
                access_expires_at=access_expires_at,
                first_name=first_name,
                last_name=last_name,
                display_name=f"{first_name} {last_name}".strip() or None,
                created_by_user_id=created_by_user_id,
            )
        )


@pytest.fixture
def auth_app(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Flask:
    runtime_root = tmp_path / "runtime"
    public_root = tmp_path / "public"
    runtime_root.mkdir(parents=True, exist_ok=True)
    public_root.mkdir(parents=True, exist_ok=True)

    monkeypatch.setenv("FLASK_ENV", "testing")
    monkeypatch.setenv("PROMAT_RUNTIME_ROOT", str(runtime_root))
    monkeypatch.setenv("PROMAT_PUBLIC_ROOT", str(public_root))

    db_path = tmp_path / "auth.sqlite3"
    app_root = Path(__file__).resolve().parents[1]
    app = Flask(
        __name__,
        template_folder=str(app_root / "templates"),
        static_folder=str(app_root / "static"),
    )
    sent_access_request_messages: list[object] = []

    def fake_access_request_mail_sender(message) -> None:
        sent_access_request_messages.append(message)

    app.config.update(
        TESTING=True,
        SECRET_KEY="test-secret",
        SERVER_NAME="promat.test",
        JWT_SECRET_KEY="test-secret",
        JWT_TOKEN_LOCATION=["cookies"],
        JWT_COOKIE_CSRF_PROTECT=False,
        RATE_LIMIT_STORAGE_URI="memory://",
        RATELIMIT_STORAGE_URI="memory://",
        AUTH_DATABASE_URL=f"sqlite:///{db_path.as_posix()}",
        AUTH_RESET_TOKEN_EXP_DAYS=14,
        AUTH_ACCESS_REQUEST_MAIL_ENABLED=True,
        AUTH_ACCESS_REQUEST_EMAIL="access-requests@example.org",
        AUTH_ACCESS_REQUEST_SUBJECT='Zugangsanfrage "Pronunciation Matters"',
        AUTH_ACCESS_REQUEST_FROM_EMAIL="noreply@promat.test",
        AUTH_ACCESS_REQUEST_REPLY_TO_ENABLED=True,
        AUTH_ACCESS_REQUEST_SMTP_HOST="smtp.promat.test",
        AUTH_ACCESS_REQUEST_SMTP_PORT=587,
        AUTH_ACCESS_REQUEST_SMTP_USE_TLS=True,
        AUTH_ACCESS_REQUEST_SMTP_USE_SSL=False,
        AUTH_ACCESS_REQUEST_SMTP_TIMEOUT_SECONDS=10,
        AUTH_ACCESS_REQUEST_FORM_MAX_AGE_SECONDS=43200,
        AUTH_ACCESS_REQUEST_MIN_SUBMIT_SECONDS=0,
        AUTH_ACCESS_REQUEST_MAIL_SENDER=fake_access_request_mail_sender,
        TEST_ACCESS_REQUEST_MESSAGES=sent_access_request_messages,
    )

    register_context_processors(app)
    register_extensions(app)
    init_engine(app)
    register_auth_context(app)
    register_error_handlers(app)

    @app.get("/auth-test/protected-html")
    @jwt_required()
    def auth_test_protected_html() -> str:
        return "ok"

    @app.get("/api/auth-test/protected-json")
    @jwt_required()
    def auth_test_protected_json():
        return jsonify({"ok": True})

    @app.get("/auth-test/unauthorized")
    def auth_test_unauthorized_html() -> str:
        abort(401)

    @app.get("/auth-test/bad-request")
    def auth_test_bad_request_html() -> str:
        abort(400)

    @app.get("/api/auth-test/unauthorized")
    def auth_test_unauthorized_json() -> str:
        abort(401)

    @app.get("/auth-test/forbidden")
    def auth_test_forbidden_html() -> str:
        abort(403)

    @app.get("/api/auth-test/forbidden")
    def auth_test_forbidden_json() -> str:
        abort(403)

    @app.get("/auth-test/server-error")
    def auth_test_server_error_html() -> str:
        abort(500)

    with app.app_context():
        Base.metadata.create_all(bind=get_engine())
        _insert_user(user_id="user-1", username="alice", email="alice@example.org", first_name="Alice", last_name="Example")
        _insert_user(user_id="admin-1", username="admin", email="admin@example.org", first_name="Ada", last_name="Admin", role="admin")
        _insert_user(
            user_id="expired-1",
            username="expired",
            email="expired@example.org",
            first_name="Erin",
            last_name="Expired",
            access_expires_at=datetime.now(timezone.utc) - timedelta(days=1),
        )

    app.register_blueprint(auth_blueprint)
    app.register_blueprint(admin_blueprint)
    app.register_blueprint(public_blueprint)
    return app


def _login(client, *, email: str, password: str = "ValidPass1"):
    return client.post(
        "/auth/login",
        data={"email": email, "password": password},
        follow_redirects=False,
    )


def _extract_element_by_id(html: str, tag: str, element_id: str) -> str:
    match = re.search(
        rf'<{tag}[^>]*id="{re.escape(element_id)}".*?</{tag}>',
        html,
        re.DOTALL,
    )
    assert match is not None
    return match.group(0)


def _render_auth_template(app: Flask, template_name: str, *, ui_lang: str) -> str:
    with app.test_request_context(f"/auth-test/template?ui_lang={ui_lang}"):
        return render_template(
            template_name,
            auth_ui_lang=ui_lang,
            current_ui_lang=ui_lang,
            ui_lang=ui_lang,
        )


def _extract_hidden_input_value(html: str, name: str) -> str:
    match = re.search(rf'name="{re.escape(name)}" value="([^"]*)"', html)
    assert match is not None
    return match.group(1)


def _build_access_request_payload(
    client,
    *,
    next_url: str = "/de/research/spanish",
    overrides: dict[str, str] | None = None,
) -> dict[str, str]:
    response = client.get(f"/access-request?next={next_url}")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    payload = {
        "first_name": "Mara",
        "last_name": "Fischer",
        "institution": "Universität Marburg",
        "role_or_function": "Wissenschaftliche Mitarbeiterin",
        "email": "mara.fischer@uni-marburg.de",
        "purpose": "Ich benötige Zugang für ein Seminar zur Ausspracheforschung und für die Auswertung ausgewählter Korpusdaten.",
        "consent_confirmed": "1",
        "ui_lang": "de",
        "next": next_url,
        "website": "",
        "access_request_form_token": _extract_hidden_input_value(html, "access_request_form_token"),
    }
    if overrides:
        payload.update(overrides)
    return payload


def test_login_page_renders_english_copy_from_next_path(auth_app: Flask) -> None:
    client = auth_app.test_client()

    response = client.get("/login?next=/en/research/spanish/comparison")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Email address" in html
    assert "Pronunciation Matters" in html
    assert "pseudonymized data from learners" in html
    assert "Open request form" in html
    assert "No access yet?" in html
    assert "Access to the research corpora is requested through a short form, reviewed institutionally, and answered by email." in html
    assert "promat-panel__section-header" not in html
    assert "app-shell--panel-hidden app-shell--auth" in html
    assert "pm-auth-surface" in html
    assert "pm-auth-secondary" in html
    assert 'pm-action-button pm-action-button--tertiary pm-action-button--medium pm-auth-action-link' in html
    assert 'pm-action-button pm-action-button--primary pm-action-button--medium pm-auth-submit' in html
    assert 'pm-nav-pill pm-nav-pill--secondary pm-nav-pill--medium' in html
    assert 'pm-interaction__icon pm-interaction__icon--leading" aria-hidden="true">login<' in html
    assert "md3-card" not in html
    assert "md3-button" not in html
    assert "md3-outlined-textfield" not in html
    assert 'name="next" value="/en/research/spanish/comparison"' in html
    assert 'href="/access-request?next=/en/research/spanish/comparison"' in html


def test_login_page_links_to_request_form_in_german(auth_app: Flask) -> None:
    client = auth_app.test_client()

    response = client.get("/login?ui_lang=de")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Zum Anfrageformular" in html
    assert 'href="/access-request?ui_lang=de"' in html
    assert "Zugang zu den Forschungskorpora wird über ein kurzes Formular angefragt" in html
    assert 'pm-action-button pm-action-button--tertiary pm-action-button--medium pm-auth-action-link' in html
    assert 'pm-action-button pm-action-button--primary pm-action-button--medium pm-auth-submit' in html
    assert 'pm-nav-pill pm-nav-pill--secondary pm-nav-pill--medium pm-auth-secondary__action-link' in html


@pytest.mark.parametrize(
    ("accept_language", "expected_target"),
    [
        ("de-DE,de;q=0.9,en;q=0.8", "/de"),
        ("en-US,en;q=0.9,de;q=0.8", "/en"),
        ("fr-FR,fr;q=0.9,de;q=0.8", "/en"),
    ],
)
def test_root_landing_redirect_uses_accept_language_when_no_override(
    auth_app: Flask,
    accept_language: str,
    expected_target: str,
) -> None:
    client = auth_app.test_client()

    response = client.get("/", headers={"Accept-Language": accept_language})

    assert response.status_code == 302
    assert response.headers["Location"] == expected_target


def test_explicit_lang_query_overrides_stored_preference_on_root(auth_app: Flask) -> None:
    client = auth_app.test_client()

    first_response = client.get("/login?lang=en")
    assert first_response.status_code == 200
    assert "pm_ui_lang=en" in "\n".join(first_response.headers.getlist("Set-Cookie"))

    response = client.get("/?lang=de", headers={"Accept-Language": "en-US,en;q=0.9"})

    assert response.status_code == 302
    assert response.headers["Location"] == "/de"
    assert "pm_ui_lang=de" in "\n".join(response.headers.getlist("Set-Cookie"))


def test_stored_ui_language_overrides_accept_language_on_unprefixed_auth_route(auth_app: Flask) -> None:
    client = auth_app.test_client()

    first_response = client.get("/login?lang=de")
    assert first_response.status_code == 200
    assert "pm_ui_lang=de" in "\n".join(first_response.headers.getlist("Set-Cookie"))

    response = client.get("/login", headers={"Accept-Language": "en-US,en;q=0.9"})

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Zum Anfrageformular" in html
    assert "Zugang zu den Forschungskorpora wird über ein kurzes Formular angefragt" in html


def test_landing_page_renders_english_copy_and_shared_language_switch(auth_app: Flask) -> None:
    client = auth_app.test_client()

    response = client.get("/en")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Exploring and teaching foreign languages digitally." in html
    assert "Research pronunciation" in html
    assert "Empirical speech data on learner pronunciation and analysis tools for research and university teaching." in html
    assert "Go to research" in html
    assert "Research setting with a discussion and audio analysis on a laptop" in html
    assert "Teach pronunciation" in html
    assert "Teaching materials for practising and reflecting on pronunciation in foreign language education." in html
    assert "Go to teaching" in html
    assert "Classroom scene representing teaching materials and listening examples" in html
    assert 'class="promat-topbar__language-switch"' in html
    assert 'href="/de?lang=de"' in html
    assert 'href="/en?lang=en"' in html
    assert '<header id="top-app-bar">' not in html


@pytest.mark.parametrize(
    ("path", "expected_nav_label", "expected_imprint_label", "expected_privacy_label"),
    [
        ("/login?ui_lang=de", "Rechtliches", "Impressum", "Datenschutz"),
        ("/login?next=/en/research/spanish/comparison", "Legal", "Imprint", "Privacy"),
    ],
)
def test_shared_footer_localizes_legal_links(
    auth_app: Flask,
    path: str,
    expected_nav_label: str,
    expected_imprint_label: str,
    expected_privacy_label: str,
) -> None:
    client = auth_app.test_client()

    response = client.get(path)

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert f'aria-label="{expected_nav_label}"' in html
    assert f'>{expected_imprint_label}<' in html
    assert f'>{expected_privacy_label}<' in html


def test_access_request_page_renders_form_and_login_link_with_return_target(auth_app: Flask) -> None:
    client = auth_app.test_client()

    response = client.get("/access-request?next=/de/research/spanish")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Zugangspfad für neue legitime Nutzer:innen aus Forschungs- und Bildungseinrichtungen." in html
    assert "Bereits freigeschaltet?" in html
    assert 'action="/access-request"' in html
    assert 'name="first_name"' in html
    assert 'name="last_name"' in html
    assert 'name="institution"' in html
    assert 'name="role_or_function"' in html
    assert 'name="email"' in html
    assert 'name="purpose"' in html
    assert 'name="consent_confirmed"' in html
    assert 'name="website"' in html
    assert 'name="access_request_form_token"' in html
    assert html.count('href="/login?next=/de/research/spanish"') == 1
    assert "Anfrage absenden" in html
    assert 'pm-action-button pm-action-button--primary pm-action-button--medium pm-auth-submit' in html
    assert 'pm-nav-pill pm-nav-pill--secondary pm-nav-pill--medium pm-auth-secondary__action-link' in html


def test_access_request_submit_persists_request_and_shows_success(auth_app: Flask) -> None:
    client = auth_app.test_client()
    payload = _build_access_request_payload(client)

    response = client.post(
        "/access-request",
        data=payload,
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["Location"] == "/access-request?next=/de/research/spanish"

    follow_up = client.get(response.headers["Location"])
    assert follow_up.status_code == 200
    html = follow_up.get_data(as_text=True)
    assert "Ihre Anfrage wurde erfasst. Wir melden uns nach der Prüfung per E-Mail." in html

    with auth_app.app_context():
        with get_session() as session:
            requests = session.query(AccessRequest).all()
        assert len(requests) == 1
        assert requests[0].first_name == "Mara"
        assert requests[0].last_name == "Fischer"
        assert requests[0].institution == "Universität Marburg"
        assert requests[0].role_or_function == "Wissenschaftliche Mitarbeiterin"
        assert requests[0].email == "mara.fischer@uni-marburg.de"
        assert requests[0].requested_path == "/de/research/spanish"
        assert requests[0].consent_confirmed is True
        assert requests[0].status == "notified"

    sent_messages = auth_app.config["TEST_ACCESS_REQUEST_MESSAGES"]
    assert len(sent_messages) == 1
    message = sent_messages[0]
    assert message.from_address == "noreply@promat.test"
    assert message.to_address == "access-requests@example.org"
    assert message.reply_to == "mara.fischer@uni-marburg.de"
    assert message.subject == 'Zugangsanfrage "Pronunciation Matters"'
    assert "Request ID:" in message.body
    assert "Name: Fischer, Mara" in message.body
    assert "Email: mara.fischer@uni-marburg.de" in message.body
    assert "Institution: Universität Marburg" in message.body
    assert "Role / function: Wissenschaftliche Mitarbeiterin" in message.body
    assert "Ich benötige Zugang für ein Seminar" in message.body


def test_access_request_submit_marks_notification_failure_without_losing_request(auth_app: Flask) -> None:
    client = auth_app.test_client()
    auth_app.config["AUTH_ACCESS_REQUEST_MAIL_SENDER"] = lambda _message: (_ for _ in ()).throw(RuntimeError("smtp down"))
    payload = _build_access_request_payload(client)

    response = client.post("/access-request", data=payload, follow_redirects=False)

    assert response.status_code == 303
    with auth_app.app_context():
        with get_session() as session:
            requests = session.query(AccessRequest).all()
        assert len(requests) == 1
        assert requests[0].status == "notification_failed"


def test_access_request_submit_shows_field_errors(auth_app: Flask) -> None:
    client = auth_app.test_client()
    payload = _build_access_request_payload(
        client,
        overrides={
            "first_name": "",
            "last_name": "",
            "institution": "",
            "role_or_function": "",
            "email": "invalid",
            "purpose": "",
            "consent_confirmed": "",
        },
    )

    response = client.post(
        "/access-request",
        data=payload,
        follow_redirects=False,
    )

    assert response.status_code == 400
    html = response.get_data(as_text=True)
    assert "Bitte prüfen Sie die markierten Felder und senden Sie die Anfrage erneut." in html
    assert "Bitte geben Sie Ihren Vornamen ein." in html
    assert "Bitte geben Sie eine gültige E-Mail-Adresse ein." in html
    assert "Bitte bestätigen Sie die Datenschutz- und Vertraulichkeitsvorgaben." in html


def test_access_request_submit_keeps_rate_limit(auth_app: Flask) -> None:
    client = auth_app.test_client()

    for index in range(5):
        payload = _build_access_request_payload(
            client,
            overrides={"email": f"rate.limit.{index}@uni-marburg.de"},
        )
        response = client.post("/access-request", data=payload, follow_redirects=False)
        assert response.status_code == 303

    blocked = client.post(
        "/access-request",
        data=_build_access_request_payload(
            client,
            overrides={"email": "rate.limit.blocked@uni-marburg.de"},
        ),
        follow_redirects=False,
    )

    assert blocked.status_code == 429


def test_access_request_honeypot_submit_skips_db_and_mail(auth_app: Flask) -> None:
    client = auth_app.test_client()
    payload = _build_access_request_payload(client, overrides={"website": "https://spam.invalid"})

    response = client.post("/access-request", data=payload, follow_redirects=False)

    assert response.status_code == 303
    with auth_app.app_context():
        with get_session() as session:
            requests = session.query(AccessRequest).all()
        assert requests == []
    assert auth_app.config["TEST_ACCESS_REQUEST_MESSAGES"] == []


def test_access_request_submit_timing_guard_skips_db_and_mail(
    auth_app: Flask,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = auth_app.test_client()
    auth_app.config["AUTH_ACCESS_REQUEST_MIN_SUBMIT_SECONDS"] = 1.0
    monkeypatch.setattr(public_routes.time, "time", lambda: 100.0)
    payload = _build_access_request_payload(client)
    monkeypatch.setattr(public_routes.time, "time", lambda: 100.2)

    response = client.post("/access-request", data=payload, follow_redirects=False)

    assert response.status_code == 303
    with auth_app.app_context():
        with get_session() as session:
            requests = session.query(AccessRequest).all()
        assert requests == []
    assert auth_app.config["TEST_ACCESS_REQUEST_MESSAGES"] == []


def test_access_request_rejects_too_long_fields(auth_app: Flask) -> None:
    client = auth_app.test_client()
    payload = _build_access_request_payload(client, overrides={"purpose": "x" * 4001})

    response = client.post("/access-request", data=payload, follow_redirects=False)

    assert response.status_code == 400
    assert "Bitte kürzen Sie diesen Eintrag." in response.get_data(as_text=True)


def test_access_request_rejects_header_injection_input(auth_app: Flask) -> None:
    client = auth_app.test_client()
    payload = _build_access_request_payload(
        client,
        overrides={
            "first_name": "Mara\r\nInjected",
            "email": "mara.fischer@uni-marburg.de\r\nBcc:evil@example.org",
        },
    )

    response = client.post("/access-request", data=payload, follow_redirects=False)

    assert response.status_code == 400
    html = response.get_data(as_text=True)
    assert "Bitte entfernen Sie unzulässige Zeichen aus diesem Feld." in html
    with auth_app.app_context():
        with get_session() as session:
            requests = session.query(AccessRequest).all()
        assert requests == []
    assert auth_app.config["TEST_ACCESS_REQUEST_MESSAGES"] == []


def test_access_request_logs_metadata_without_full_pii(
    auth_app: Flask,
    caplog: pytest.LogCaptureFixture,
) -> None:
    client = auth_app.test_client()
    payload = _build_access_request_payload(client)

    with caplog.at_level(logging.INFO):
        response = client.post("/access-request", data=payload, follow_redirects=False)

    assert response.status_code == 303
    assert "Recorded access request | request_id=" in caplog.text
    assert "Access request notification sent | request_id=" in caplog.text
    assert "mara.fischer@uni-marburg.de" not in caplog.text
    assert "Universität Marburg" not in caplog.text
    assert "Ich benötige Zugang für ein Seminar" not in caplog.text
    assert "Purpose:" not in caplog.text


def test_public_auth_pages_redirect_authenticated_users(auth_app: Flask) -> None:
    client = auth_app.test_client()

    login_response = _login(client, email="alice@example.org")

    assert login_response.status_code == 303
    public_login = client.get("/login?next=/de/research/spanish", follow_redirects=False)
    public_request = client.get("/access-request?next=/de/research/spanish", follow_redirects=False)

    assert public_login.status_code == 303
    assert public_login.headers["Location"] == "/de/research/spanish"
    assert public_request.status_code == 303
    assert public_request.headers["Location"] == "/de/research/spanish"


def test_login_from_corpus_root_returns_to_same_corpus_root(auth_app: Flask) -> None:
    client = auth_app.test_client()

    landing_response = client.get("/de/research/spanish")

    assert landing_response.status_code == 200
    assert 'href="/login?next=/de/research/spanish"' in landing_response.get_data(as_text=True)

    login_response = client.post(
        "/auth/login",
        data={
            "email": "alice@example.org",
            "password": "ValidPass1",
            "next": "/de/research/spanish",
        },
        follow_redirects=False,
    )

    assert login_response.status_code == 303
    assert login_response.headers["Location"] == "/de/research/spanish"


def test_login_accepts_email_only_and_rejects_username(auth_app: Flask) -> None:
    client = auth_app.test_client()

    success = client.post(
        "/auth/login",
        data={
            "email": "alice@example.org",
            "password": "ValidPass1",
            "next": "/de/research/spanish/comparison",
        },
        follow_redirects=False,
    )
    failure = client.post(
        "/auth/login",
        data={"email": "alice", "password": "ValidPass1", "ui_lang": "en"},
        follow_redirects=False,
    )

    assert success.status_code == 303
    assert success.headers["Location"] == "/de/research/spanish/comparison"
    assert "access_token_cookie=" in success.headers.get("Set-Cookie", "")
    assert failure.status_code == 401
    assert "Sign-in failed" in failure.get_data(as_text=True)


def test_logout_clears_auth_cookie_and_session_state(auth_app: Flask) -> None:
    client = auth_app.test_client()

    login_response = _login(client, email="alice@example.org")

    assert login_response.status_code == 303
    session_response = client.get("/auth/session")
    assert session_response.status_code == 200
    assert session_response.get_json()["authenticated"] is True

    logout_response = client.get("/auth/logout", follow_redirects=False)

    assert logout_response.status_code == 303
    assert logout_response.headers["Location"] == "/"
    cleared_cookie = logout_response.headers.getlist("Set-Cookie")
    assert any("access_token_cookie=;" in value for value in cleared_cookie)

    session_after_logout = client.get("/auth/session")
    assert session_after_logout.status_code == 200
    assert session_after_logout.get_json()["authenticated"] is False


def test_protected_html_route_without_auth_redirects_to_login(auth_app: Flask) -> None:
    client = auth_app.test_client()

    response = client.get("/auth-test/protected-html", follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["Location"] == "/login"


def test_protected_api_route_without_auth_returns_json_401(auth_app: Flask) -> None:
    client = auth_app.test_client()

    response = client.get("/api/auth-test/protected-json")

    assert response.status_code == 401
    assert response.is_json is True
    payload = response.get_json()
    assert payload["error"] == "unauthorized"
    assert "cookie" in payload["message"].lower()


def test_generic_html_401_renders_error_page(auth_app: Flask) -> None:
    client = auth_app.test_client()

    response = client.get("/auth-test/unauthorized?lang=de")

    assert response.status_code == 401
    html = response.get_data(as_text=True)
    assert "Nicht autorisiert" in html
    assert 'pm-error-surface pm-surface-density--standard' in html
    assert 'pm-error-surface__code">401<' in html
    assert 'pm-error-surface__actions pm-action-row' in html
    assert 'pm-action-button pm-action-button--primary pm-action-button--medium' in html
    assert 'pm-action-button pm-action-button--secondary pm-action-button--medium' in html
    assert "md3-error-page" not in html
    assert "md3-error-container" not in html
    assert "md3-button" not in html


def test_generic_html_400_renders_error_page(auth_app: Flask) -> None:
    client = auth_app.test_client()

    response = client.get("/auth-test/bad-request?lang=de")

    assert response.status_code == 400
    html = response.get_data(as_text=True)
    assert "Ungültige Anfrage" in html
    assert "Die Anfrage konnte nicht verarbeitet werden." in html
    assert 'pm-error-surface pm-surface-density--standard' in html
    assert 'pm-error-surface__code">400<' in html
    assert 'pm-error-surface__actions pm-action-row' in html
    assert 'pm-action-button pm-action-button--primary pm-action-button--medium' in html
    assert 'pm-action-button pm-action-button--secondary pm-action-button--medium' in html
    assert "md3-error-page" not in html
    assert "md3-error-container" not in html
    assert "md3-button" not in html


def test_generic_api_401_returns_json_error(auth_app: Flask) -> None:
    client = auth_app.test_client()

    response = client.get("/api/auth-test/unauthorized")

    assert response.status_code == 401
    assert response.is_json is True
    assert response.get_json() == {
        "error": "Unauthorized",
        "message": "Unauthorized",
    }


def test_generic_html_403_renders_error_page(auth_app: Flask) -> None:
    client = auth_app.test_client()

    response = client.get("/auth-test/forbidden?lang=de")

    assert response.status_code == 403
    html = response.get_data(as_text=True)
    assert "Zugriff verweigert" in html
    assert 'pm-error-surface pm-surface-density--standard' in html
    assert 'pm-error-surface__code">403<' in html
    assert 'pm-error-surface__actions pm-action-row' in html
    assert 'pm-action-button pm-action-button--primary pm-action-button--medium' in html
    assert 'pm-action-button pm-action-button--secondary pm-action-button--medium' in html
    assert "md3-error-page" not in html
    assert "md3-error-container" not in html
    assert "md3-button" not in html


@pytest.mark.parametrize(
    ("path", "expected_status", "expected_title", "expected_message", "expected_primary_label", "expected_secondary_label"),
    [
        ("/auth-test/bad-request?ui_lang=en", 400, "Bad request", "The request could not be processed.", "Home", "Back"),
        ("/auth-test/unauthorized?ui_lang=en", 401, "Unauthorized", "This resource is available only after sign-in.", "Login", "Home"),
        ("/auth-test/forbidden?ui_lang=en", 403, "Access denied", "You do not have permission to access this page.", "Home", "Back"),
        ("/en/missing-page", 404, "Page not found", "The requested page does not exist or has been moved.", "Home", "Back"),
        ("/auth-test/server-error?ui_lang=en", 500, "Internal server error", "An unexpected error occurred.", "Home", "Reload page"),
    ],
)
def test_error_pages_render_english_shared_copy(
    auth_app: Flask,
    path: str,
    expected_status: int,
    expected_title: str,
    expected_message: str,
    expected_primary_label: str,
    expected_secondary_label: str,
) -> None:
    client = auth_app.test_client()

    response = client.get(path)

    assert response.status_code == expected_status
    html = response.get_data(as_text=True)
    assert expected_title in html
    assert expected_message in html
    assert f'>{expected_primary_label}<' in html
    assert f'>{expected_secondary_label}<' in html
    assert 'pm-error-surface pm-surface-density--standard' in html
    assert 'pm-error-surface__actions pm-action-row' in html
    assert 'pm-action-button pm-action-button--primary pm-action-button--medium' in html
    assert 'pm-action-button pm-action-button--secondary pm-action-button--medium' in html
    assert "md3-error-page" not in html
    assert "md3-error-container" not in html
    assert "md3-button" not in html


def test_generic_api_403_returns_json_error(auth_app: Flask) -> None:
    client = auth_app.test_client()

    response = client.get("/api/auth-test/forbidden")

    assert response.status_code == 403
    assert response.is_json is True
    assert response.get_json() == {
        "error": "Forbidden",
        "message": "Forbidden",
    }


def test_login_blocks_expired_account_with_localized_message(auth_app: Flask) -> None:
    client = auth_app.test_client()

    response = client.post(
        "/auth/login",
        data={"email": "expired@example.org", "password": "ValidPass1", "ui_lang": "en"},
        follow_redirects=False,
    )

    assert response.status_code == 403
    assert "Access for this account has expired." in response.get_data(as_text=True)


def test_password_forgot_creates_reset_token_without_leaking_account(auth_app: Flask, caplog: pytest.LogCaptureFixture) -> None:
    client = auth_app.test_client()

    with caplog.at_level(logging.INFO):
        response = client.post(
            "/auth/password/forgot",
            data={"email": "alice@example.org", "ui_lang": "en"},
            follow_redirects=False,
        )

    assert response.status_code == 200
    assert "a new link to set the password has been prepared" in response.get_data(as_text=True)
    assert "Prepared password-reset message metadata" in caplog.text
    assert "recipient_domain=example.org" in caplog.text
    assert "alice@example.org" not in caplog.text
    assert "/auth/password/reset?token=" not in caplog.text
    assert "token=" not in caplog.text
    assert "Use this link to choose a new password" not in caplog.text
    with auth_app.app_context():
        with get_session() as session:
            tokens = session.query(ResetToken).filter(ResetToken.user_id == "user-1").all()
        assert len(tokens) == 1
        expires_at = tokens[0].expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        expires_in = expires_at - datetime.now(timezone.utc)
        assert 13 <= expires_in.days <= 14


def test_password_forgot_page_uses_user_facing_copy_in_english(auth_app: Flask) -> None:
    client = auth_app.test_client()

    response = client.get("/auth/password/forgot?ui_lang=en")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "If access exists for that address" in html
    assert "For security reasons, we do not indicate whether an account already exists" in html
    assert "No access yet?" in html
    assert "pm-auth-surface" in html
    assert "pm-auth-secondary" in html
    assert 'pm-action-button pm-action-button--primary pm-action-button--medium pm-auth-submit' in html
    assert html.count('pm-nav-pill pm-nav-pill--secondary pm-nav-pill--medium') >= 2
    assert 'pm-nav-pill--back' in html
    assert 'pm-nav-pill__label">Login</span>' in html
    assert "md3-card" not in html
    assert "md3-button" not in html
    assert "md3-outlined-textfield" not in html
    assert "The reset message is prepared on the server" not in html


def test_password_reset_page_uses_user_facing_invalid_link_copy(auth_app: Flask) -> None:
    client = auth_app.test_client()

    response = client.get("/auth/password/reset?token=invalid-token&ui_lang=en")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Use this link to choose a new password for your Pronunciation Matters account." in html
    assert "If needed, request a new one via" in html
    assert "If you need new access instead of an existing account" in html
    assert "pm-auth-surface" in html
    assert "pm-auth-state" in html
    assert "pm-auth-secondary" in html
    assert 'pm-action-button pm-action-button--primary pm-action-button--medium pm-auth-submit' in html
    assert 'pm-nav-pill pm-nav-pill--secondary pm-nav-pill--medium pm-auth-secondary__action-link' in html
    assert 'pm-nav-pill__label">Login</span>' in html
    assert "md3-card" not in html
    assert "md3-button" not in html
    assert "md3-outlined-textfield" not in html


def test_password_reset_updates_password_and_consumes_token(auth_app: Flask) -> None:
    with auth_app.app_context():
        user = auth_services.find_user_by_email("alice@example.org")
        raw_token, _ = auth_services.create_reset_token_for_user(user)

    client = auth_app.test_client()
    response = client.post(
        "/auth/password/reset",
        data={
            "token": raw_token,
            "new_password": "NewValid1",
            "confirm_password": "NewValid1",
            "ui_lang": "en",
        },
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["Location"].startswith("/login")
    with auth_app.app_context():
        user = auth_services.find_user_by_email("alice@example.org")
        assert auth_services.verify_password("NewValid1", user.password_hash)
        _, status = auth_services.inspect_reset_token(raw_token)
        assert status == "used"


def test_admin_create_user_returns_invite_preview_and_expiry(auth_app: Flask, caplog: pytest.LogCaptureFixture) -> None:
    client = auth_app.test_client()
    login_response = _login(client, email="admin@example.org")

    assert login_response.status_code == 303

    with caplog.at_level(logging.INFO):
        response = client.post(
            "/admin/users",
            json={
                "first_name": "Nora",
                "last_name": "New",
                "email": "new.user@example.org",
                "role": "user",
                "access_expires_on": "2030-01-31",
                "invite_note": "Please review the shared corpus guidelines before your first login.",
            },
            headers={"Referer": "http://promat.test/admin/users/page?ui_lang=en"},
        )

    assert response.status_code == 201
    payload = response.get_json()
    assert payload["ok"] is True
    assert "/auth/password/reset?token=" in payload["inviteLink"]
    assert "ui_lang=en" in payload["inviteLink"]
    assert "Please review the shared corpus guidelines" in payload["inviteMailBody"]
    assert "Prepared admin invite message metadata" in caplog.text
    assert "recipient_domain=example.org" in caplog.text
    assert "new.user@example.org" not in caplog.text
    assert payload["inviteLink"] not in caplog.text
    assert "token=" not in caplog.text
    assert payload["inviteMailBody"] not in caplog.text

    with auth_app.app_context():
        user = auth_services.find_user_by_email("new.user@example.org")
        assert user is not None
        assert user.role == "user"
        assert user.first_name == "Nora"
        assert user.last_name == "New"
        assert user.created_by_user_id == "admin-1"
        assert user.must_reset_password is True
        assert user.access_expires_at.date().isoformat() == "2030-01-31"


def test_admin_reset_password_preview_keeps_secret_logging(auth_app: Flask, caplog: pytest.LogCaptureFixture) -> None:
    client = auth_app.test_client()
    login_response = _login(client, email="admin@example.org")

    assert login_response.status_code == 303

    with caplog.at_level(logging.INFO):
        response = client.post(
            "/admin/users/user-1/reset-password",
            headers={"Referer": "http://promat.test/admin/users/page?ui_lang=en"},
        )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["ok"] is True
    assert "Prepared admin reset message metadata" in caplog.text
    assert "recipient_domain=example.org" in caplog.text
    assert "alice@example.org" not in caplog.text
    assert payload["inviteLink"] not in caplog.text
    assert "token=" not in caplog.text
    assert payload["inviteMailBody"] not in caplog.text


def test_login_post_keeps_rate_limit(auth_app: Flask) -> None:
    client = auth_app.test_client()

    for _ in range(5):
        response = client.post(
            "/auth/login",
            data={"email": "alice@example.org", "password": "WrongPass1"},
            follow_redirects=False,
        )
        assert response.status_code in {401, 403}

    blocked = client.post(
        "/auth/login",
        data={"email": "alice@example.org", "password": "WrongPass1"},
        follow_redirects=False,
    )

    assert blocked.status_code == 429


def test_password_forgot_submit_keeps_rate_limit(auth_app: Flask) -> None:
    client = auth_app.test_client()

    for _ in range(5):
        response = client.post(
            "/auth/password/forgot",
            data={"email": "alice@example.org", "ui_lang": "en"},
            follow_redirects=False,
        )
        assert response.status_code == 200

    blocked = client.post(
        "/auth/password/forgot",
        data={"email": "alice@example.org", "ui_lang": "en"},
        follow_redirects=False,
    )

    assert blocked.status_code == 429


def test_password_reset_api_keeps_rate_limit(auth_app: Flask) -> None:
    client = auth_app.test_client()

    for _ in range(10):
        response = client.post(
            "/auth/reset-password/confirm",
            json={
                "resetToken": "invalid-token",
                "newPassword": "ValidPass2",
                "confirmPassword": "ValidPass2",
            },
            follow_redirects=False,
        )
        assert response.status_code == 400

    blocked = client.post(
        "/auth/reset-password/confirm",
        json={
            "resetToken": "invalid-token",
            "newPassword": "ValidPass2",
            "confirmPassword": "ValidPass2",
        },
        follow_redirects=False,
    )

    assert blocked.status_code == 429


def test_admin_user_create_keeps_rate_limit(auth_app: Flask) -> None:
    client = auth_app.test_client()
    login_response = _login(client, email="admin@example.org")

    assert login_response.status_code == 303

    for index in range(10):
        response = client.post(
            "/admin/users",
            json={
                "first_name": "Rate",
                "last_name": "Limit",
                "email": f"rate.limit.{index}@example.org",
                "role": "user",
                "access_expires_on": "2030-01-31",
            },
            headers={"Referer": "http://promat.test/admin/users/page?ui_lang=en"},
        )
        assert response.status_code == 201

    blocked = client.post(
        "/admin/users",
        json={
            "first_name": "Rate",
            "last_name": "Blocked",
            "email": "rate.limit.blocked@example.org",
            "role": "user",
            "access_expires_on": "2030-01-31",
        },
        headers={"Referer": "http://promat.test/admin/users/page?ui_lang=en"},
    )

    assert blocked.status_code == 429


def test_admin_user_patch_keeps_rate_limit(auth_app: Flask) -> None:
    client = auth_app.test_client()
    login_response = _login(client, email="admin@example.org")

    assert login_response.status_code == 303

    for index in range(10):
        response = client.patch(
            "/admin/users/user-1?ui_lang=en",
            json={"first_name": f"Alice-{index}"},
        )
        assert response.status_code == 200

    blocked = client.patch(
        "/admin/users/user-1?ui_lang=en",
        json={"first_name": "Alice-blocked"},
    )

    assert blocked.status_code == 429


def test_admin_user_reset_keeps_rate_limit(auth_app: Flask) -> None:
    client = auth_app.test_client()
    login_response = _login(client, email="admin@example.org")

    assert login_response.status_code == 303

    for _ in range(10):
        response = client.post(
            "/admin/users/user-1/reset-password",
            headers={"Referer": "http://promat.test/admin/users/page?ui_lang=en"},
        )
        assert response.status_code == 200

    blocked = client.post(
        "/admin/users/user-1/reset-password",
        headers={"Referer": "http://promat.test/admin/users/page?ui_lang=en"},
    )

    assert blocked.status_code == 429


def test_admin_user_page_renders_in_english_after_admin_login(auth_app: Flask) -> None:
    client = auth_app.test_client()
    login_response = _login(client, email="admin@example.org")

    assert login_response.status_code == 303

    response = client.get("/admin/users/page?ui_lang=en")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "User management" in html
    assert "Create user" in html
    assert "Last name" in html
    assert "First name" in html
    assert "Role" in html
    assert "Status" in html
    assert "Created by" in html
    assert "Pronunciation Matters" in html
    assert "admin-users-config" in html
    assert "pm-admin-toolbar" in html
    assert "pm-admin-dialog" in html
    assert "pm-research-table pm-admin-table" in html
    assert 'pm-action-button pm-action-button--secondary pm-action-button--medium' in html
    assert 'pm-action-button pm-action-button--primary pm-action-button--medium' in html
    assert 'class="pm-filter-chip"' in html
    assert "Editor" not in html
    assert "window.PROMAT_ADMIN_USERS_I18N" not in html
    assert "js/auth/admin_users.js?v=" in html
    assert "md3-card" not in html
    assert "md3-dialog" not in html
    assert "md3-outlined-textfield" not in html
    assert "md3-button" not in html


def test_dev_start_script_wires_expected_dev_admin_email() -> None:
    script = (Path(__file__).resolve().parents[1] / "scripts" / "dev-start.ps1").read_text(encoding="utf-8")

    assert "StartAdminEmail" in script
    assert "felix.tacke@uni-marburg.de" in script
    assert "--email $StartAdminEmail" in script


def test_login_without_next_redirects_to_role_default_targets(auth_app: Flask) -> None:
    client = auth_app.test_client()

    user_response = _login(client, email="alice@example.org")
    assert user_response.status_code == 303
    assert user_response.headers["Location"] == "/auth/account?ui_lang=de"

    admin_client = auth_app.test_client()
    admin_response = _login(admin_client, email="admin@example.org")
    assert admin_response.status_code == 303
    assert admin_response.headers["Location"] == "/admin/users/page?ui_lang=de"


def test_account_page_renders_real_account_surface_for_user(auth_app: Flask) -> None:
    client = auth_app.test_client()
    login_response = _login(client, email="alice@example.org")

    assert login_response.status_code == 303
    response = client.get("/auth/account?ui_lang=en")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "My account" in html
    assert "Account details" in html
    assert "Access and security" in html
    assert "Save account details" in html
    assert "Change password" in html
    assert "app-shell--panel-hidden" in html
    assert 'href="/auth/account?lang=de"' in html
    assert 'href="/auth/account?ui_lang=en"' in html
    assert 'pm-action-button pm-action-button--primary pm-action-button--medium' in html
    assert 'pm-nav-pill pm-nav-pill--secondary pm-nav-pill--medium' in html
    assert 'pm-account-security-action' in html
    assert "Internal area" not in html


def test_account_password_page_uses_header_back_link_to_account(auth_app: Flask) -> None:
    client = auth_app.test_client()
    login_response = _login(client, email="alice@example.org")

    assert login_response.status_code == 303
    response = client.get("/auth/account/password?ui_lang=en")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'class="pm-back-link pm-content-header__back"' in html
    assert 'pm-nav-pill__label">My account</span>' in html
    assert html.count('pm-nav-pill--back') == 1
    assert "Current password" in html
    assert "Save password" in html


def test_account_page_user_menu_stays_compact_for_regular_users(auth_app: Flask) -> None:
    client = auth_app.test_client()

    login_response = _login(client, email="alice@example.org")

    assert login_response.status_code == 303
    response = client.get("/auth/account?ui_lang=en")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    user_menu_html = _extract_element_by_id(html, "div", "user-menu-dropdown")

    assert html.index("promat-topbar__language-switch") < html.index('id="themeToggle"') < html.index("data-user-menu-root")
    assert "My account" in user_menu_html
    assert "Logout" in user_menu_html
    assert "Admin area" not in user_menu_html
    assert user_menu_html.index("My account") < user_menu_html.index("Logout")


def test_admin_users_page_uses_sidebar_only_for_admin_area_navigation(auth_app: Flask) -> None:
    client = auth_app.test_client()

    login_response = _login(client, email="admin@example.org")

    assert login_response.status_code == 303
    response = client.get("/admin/users/page?ui_lang=en")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    drawer_html = _extract_element_by_id(html, "aside", "navigation-drawer-standard")
    user_menu_html = _extract_element_by_id(html, "div", "user-menu-dropdown")

    assert "Admin area" in drawer_html
    assert "Users" in drawer_html
    assert "Analytics" in drawer_html
    assert "My account" not in drawer_html
    assert "Logout" not in drawer_html
    assert 'pm-panel__section-icon pm-icon-mask pm-icon-mask--section' in drawer_html
    assert 'href="/admin/users/page?lang=de"' in html
    assert 'href="/admin/users/page?ui_lang=en"' in html
    assert "My account" in user_menu_html
    assert "Admin area" in user_menu_html
    assert "Logout" in user_menu_html
    assert user_menu_html.index("My account") < user_menu_html.index("Admin area") < user_menu_html.index("Logout")


def test_security_headers_allow_project_youtube_embed() -> None:
    app = Flask(__name__)

    @app.get("/probe")
    def probe() -> str:
        return "ok"

    register_security_headers(app)

    with app.test_client() as client:
        response = client.get("/probe")

    assert response.status_code == 200
    csp = response.headers["Content-Security-Policy"]
    assert "script-src 'self';" in csp
    assert "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com;" in csp
    assert "font-src 'self' https://fonts.gstatic.com;" in csp
    assert "frame-src 'self' https://www.youtube.com https://datawrapper.dwcdn.net;" in csp
    assert "object-src 'none';" in csp
    assert "base-uri 'self';" in csp
    assert "form-action 'self';" in csp
    assert "cdnjs.cloudflare.com" not in csp
    assert "cdn.jsdelivr.net" not in csp
    assert "youtube-nocookie.com" not in csp


def test_access_request_page_does_not_load_removed_icon_cdns(auth_app: Flask) -> None:
    client = auth_app.test_client()

    response = client.get("/access-request")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "fonts.googleapis.com/css2?family=Inter" in html
    assert "fonts.gstatic.com" in html
    assert "css/md3/components/material-symbols-fallback.css" in html
    assert "cdnjs.cloudflare.com/ajax/libs/font-awesome" not in html
    assert "cdn.jsdelivr.net/npm/bootstrap-icons" not in html


def test_legacy_auth_snackbar_icon_path_is_removed() -> None:
    legacy_module = TEST_REPO_ROOT / "app" / "static" / "js" / "modules" / "auth" / "snackbar.js"
    snackbar_css = TEST_REPO_ROOT / "app" / "static" / "css" / "md3" / "components" / "snackbar.css"

    assert not legacy_module.exists()
    css = snackbar_css.read_text(encoding="utf-8")
    assert "md3-snackbar--auth-expired" not in css
    assert "material-symbols-outlined" not in css


def test_admin_users_static_js_uses_semantic_action_button_classes(auth_app: Flask) -> None:
    client = auth_app.test_client()

    response = client.get('/static/js/auth/admin_users.js')

    assert response.status_code == 200
    js = response.get_data(as_text=True)
    assert 'pm-action-button pm-action-button--secondary pm-action-button--small pm-admin-toast__action' in js
    assert 'pm-action-button pm-action-button--secondary pm-action-button--small pm-admin-table__action edit-user-btn' in js
    assert 'pm-action-button__label' in js
    assert 'element.innerHTML ||' not in js
    assert 'element.textContent ||' in js


def test_last_admin_cannot_be_deactivated_or_demoted(auth_app: Flask) -> None:
    client = auth_app.test_client()
    login_response = _login(client, email="admin@example.org")

    assert login_response.status_code == 303

    deactivate_response = client.patch(
        "/admin/users/admin-1?ui_lang=en",
        json={"is_active": False},
    )
    assert deactivate_response.status_code == 400
    assert "last active admin" in deactivate_response.get_json()["error"].lower()

    role_response = client.patch(
        "/admin/users/admin-1?ui_lang=en",
        json={"role": "user"},
    )
    assert role_response.status_code == 400
    assert "last active admin" in role_response.get_json()["error"].lower()


def test_admin_analytics_page_renders_aggregated_usage(auth_app: Flask) -> None:
    with auth_app.app_context():
        now = datetime.now(timezone.utc)
        with get_session() as session:
            session.add(
                AnalyticsDaily(
                    activity_date=date(2026, 4, 13),
                    unique_visitors=4,
                    page_views=12,
                    created_at=now,
                    updated_at=now,
                )
            )
            session.add(
                AnalyticsLanguageAreaDaily(
                    activity_date=date(2026, 4, 13),
                    section="research",
                    corpus_language="spanish",
                    unique_visitors=3,
                    page_views=8,
                    created_at=now,
                    updated_at=now,
                )
            )
            session.add(
                AnalyticsLanguageAreaDaily(
                    activity_date=date(2026, 4, 13),
                    section="teaching",
                    corpus_language="spanish",
                    unique_visitors=2,
                    page_views=4,
                    created_at=now,
                    updated_at=now,
                )
            )

    client = auth_app.test_client()
    login_response = _login(client, email="admin@example.org")

    assert login_response.status_code == 303
    response = client.get("/admin/analytics/page?ui_lang=en&period=30d")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Analytics" in html
    assert "Usage by language and area" in html
    assert "Unique visitors" in html
    assert "Spanish" in html
    assert "8" in html