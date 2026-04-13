from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from html import unescape
import os
from pathlib import Path
import re
import sys
from urllib.parse import unquote

from flask import Flask
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

TEST_REPO_ROOT = Path(__file__).resolve().parents[2]
os.environ.setdefault("FLASK_ENV", "development")
os.environ.setdefault("PROMAT_RUNTIME_ROOT", str(TEST_REPO_ROOT))
os.environ.setdefault("PROMAT_PUBLIC_ROOT", str(TEST_REPO_ROOT / "public"))

from app import register_auth_context, register_context_processors
from app.auth.models import AnalyticsDaily, AnalyticsLanguageAreaDaily, Base, ResetToken, User
from app.auth import services as auth_services
from app.extensions import register_extensions
from app.extensions.sqlalchemy_ext import get_engine, get_session, init_engine
from app.routes.admin import blueprint as admin_blueprint
from app.routes.auth import blueprint as auth_blueprint
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
    app.config.update(
        TESTING=True,
        SECRET_KEY="test-secret",
        SERVER_NAME="promat.test",
        JWT_SECRET_KEY="test-secret",
        JWT_TOKEN_LOCATION=["cookies"],
        JWT_COOKIE_CSRF_PROTECT=False,
        AUTH_DATABASE_URL=f"sqlite:///{db_path.as_posix()}",
        AUTH_RESET_TOKEN_EXP_DAYS=14,
    )

    register_context_processors(app)
    register_extensions(app)
    init_engine(app)
    register_auth_context(app)

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


def _extract_mailto(html: str) -> str:
    match = re.search(r'href="([^"]*mailto:[^"]+)"', html)
    assert match is not None
    return unquote(unescape(match.group(1)))


def _extract_element_by_id(html: str, tag: str, element_id: str) -> str:
    match = re.search(
        rf'<{tag}[^>]*id="{re.escape(element_id)}".*?</{tag}>',
        html,
        re.DOTALL,
    )
    assert match is not None
    return match.group(0)


def test_login_page_renders_english_copy_from_next_path(auth_app: Flask) -> None:
    client = auth_app.test_client()

    response = client.get("/login?next=/en/research/spanish/comparison")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Email address" in html
    assert "Pronunciation Matters" in html
    assert "pseudonymized data from learners" in html
    assert "Request access by email" in html
    assert "No access yet?" in html
    assert "Access to the research corpora can be requested by email, is reviewed institutionally at short notice, and is then provided by email." in html
    assert "promat-panel__section-header" not in html
    assert "app-shell--panel-hidden app-shell--auth" in html
    assert "pm-auth-surface" in html
    assert "pm-auth-secondary" in html
    assert "md3-card" not in html
    assert "md3-button" not in html
    assert "md3-outlined-textfield" not in html
    assert 'name="next" value="/en/research/spanish/comparison"' in html


def test_login_page_mailto_contains_required_fields_and_exact_subject(auth_app: Flask) -> None:
    client = auth_app.test_client()

    response = client.get("/login?ui_lang=de")

    assert response.status_code == 200
    mailto = _extract_mailto(response.get_data(as_text=True))
    assert mailto.startswith('mailto:felix.tacke@uni-marburg.de?subject=Zugangsanfrage "Pronunciation Matters"&body=')
    assert "Nachname, Vorname:" in mailto
    assert "Institution:" in mailto
    assert "Rolle/Funktion:" in mailto
    assert "Institutionelle E-Mail-Adresse:" in mailto
    assert "Zweck der Nutzung:" in mailto
    assert "Die angegebene E-Mail-Adresse wird für die Einrichtung des Zugangs verwendet." in mailto
    assert "datenschutzrechtlichen Vorgaben sowie die Vertraulichkeit der pseudonymisierten Forschungsdaten" in mailto
    assert "Bitte verwenden Sie die angegebene E-Mail-Adresse für meinen Zugang." not in mailto
    assert "Login-Identifier / Benutzername" not in mailto
    assert "Viele Grüße" not in mailto


def test_login_page_mailto_contains_required_english_fields(auth_app: Flask) -> None:
    client = auth_app.test_client()

    response = client.get("/login?ui_lang=en")

    assert response.status_code == 200
    mailto = _extract_mailto(response.get_data(as_text=True))
    assert "Last name, first name:" in mailto
    assert "Institutional email address:" in mailto
    assert "The email address provided above will be used to set up access." in mailto
    assert "confidentiality of the pseudonymized research data" in mailto
    assert "Please use the email address provided above for my access." not in mailto
    assert "login identifier / username" not in mailto
    assert "Best regards" not in mailto


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


def test_login_blocks_expired_account_with_localized_message(auth_app: Flask) -> None:
    client = auth_app.test_client()

    response = client.post(
        "/auth/login",
        data={"email": "expired@example.org", "password": "ValidPass1", "ui_lang": "en"},
        follow_redirects=False,
    )

    assert response.status_code == 403
    assert "Access for this account has expired." in response.get_data(as_text=True)


def test_password_forgot_creates_reset_token_without_leaking_account(auth_app: Flask) -> None:
    client = auth_app.test_client()

    response = client.post(
        "/auth/password/forgot",
        data={"email": "alice@example.org", "ui_lang": "en"},
        follow_redirects=False,
    )

    assert response.status_code == 200
    assert "a new link to set the password has been prepared" in response.get_data(as_text=True)
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


def test_admin_create_user_returns_invite_preview_and_expiry(auth_app: Flask) -> None:
    client = auth_app.test_client()
    login_response = _login(client, email="admin@example.org")

    assert login_response.status_code == 303

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

    with auth_app.app_context():
        user = auth_services.find_user_by_email("new.user@example.org")
        assert user is not None
        assert user.role == "user"
        assert user.first_name == "Nora"
        assert user.last_name == "New"
        assert user.created_by_user_id == "admin-1"
        assert user.must_reset_password is True
        assert user.access_expires_at.date().isoformat() == "2030-01-31"


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
    assert 'href="/auth/account?ui_lang=de"' in html
    assert 'href="/auth/account?ui_lang=en"' in html
    assert "Internal area" not in html


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
    assert "pm-icon-mask--section" not in drawer_html
    assert 'href="/admin/users/page?ui_lang=de"' in html
    assert 'href="/admin/users/page?ui_lang=en"' in html
    assert "My account" in user_menu_html
    assert "Admin area" in user_menu_html
    assert "Logout" in user_menu_html
    assert user_menu_html.index("My account") < user_menu_html.index("Admin area") < user_menu_html.index("Logout")


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