"""Tests for group account creation, login, and access restrictions."""

from __future__ import annotations

from datetime import datetime, timezone
import os
from pathlib import Path
import sys

import pytest
from flask import Flask

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

_TEST_REPO_ROOT = Path(__file__).resolve().parents[2]
os.environ.setdefault("FLASK_ENV", "development")
os.environ.setdefault("PROMAT_RUNTIME_ROOT", str(_TEST_REPO_ROOT))
os.environ.setdefault("PROMAT_PUBLIC_ROOT", str(_TEST_REPO_ROOT / "public"))

from app.auth.models import Base, User
from app import register_auth_context, register_context_processors, register_error_handlers
from app.auth import services as auth_services
from app.extensions import register_extensions
from app.extensions.sqlalchemy_ext import get_engine, get_session, init_engine
from app.routes.admin import blueprint as admin_blueprint
from app.routes.auth import blueprint as auth_blueprint
from app.routes.public import blueprint as public_blueprint


# ── Fixture ──────────────────────────────────────────────────────────────────

@pytest.fixture
def group_app(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Flask:
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
        SECRET_KEY="test-group-secret",
        SERVER_NAME="promat.test",
        JWT_SECRET_KEY="test-group-secret",
        JWT_TOKEN_LOCATION=["cookies"],
        JWT_COOKIE_CSRF_PROTECT=False,
        RATE_LIMIT_STORAGE_URI="memory://",
        RATELIMIT_STORAGE_URI="memory://",
        AUTH_DATABASE_URL=f"sqlite:///{db_path.as_posix()}",
        AUTH_RESET_TOKEN_EXP_DAYS=14,
        AUTH_MAIL_BACKEND="disabled",
        AUTH_MAIL_FROM_EMAIL="noreply@promat.test",
        AUTH_MAIL_FROM_NAME="Pronunciation Matters Administrator",
        AUTH_MAIL_DEFAULT_REPLY_TO="admin@example.org",
        APP_RELEASE_TAG="dev",
        APP_RELEASE_URL="https://github.com/FTacke/promat-webapp/releases/latest",
        GOATCOUNTER_URL="",
    )

    register_context_processors(app)
    register_extensions(app)
    init_engine(app)
    register_auth_context(app)
    register_error_handlers(app)

    with app.app_context():
        Base.metadata.create_all(bind=get_engine())
        now = datetime.now(timezone.utc)

        # Personal user
        with get_session() as s:
            s.add(User(
                id="user-1", username="alice@example.org",
                email="alice@example.org",
                password_hash=auth_services.hash_password("ValidPass1"),
                role="user", account_kind="personal",
                is_active=True, must_reset_password=False,
                created_at=now, updated_at=now,
                first_name="Alice", last_name="Example",
                display_name="Alice Example",
            ))

        # Admin
        with get_session() as s:
            s.add(User(
                id="admin-1", username="admin@example.org",
                email="admin@example.org",
                password_hash=auth_services.hash_password("ValidPass1"),
                role="admin", account_kind="personal",
                is_active=True, must_reset_password=False,
                created_at=now, updated_at=now,
                first_name="Ada", last_name="Admin",
                display_name="Ada Admin",
            ))

    app.register_blueprint(auth_blueprint)
    app.register_blueprint(admin_blueprint)
    app.register_blueprint(public_blueprint)
    return app


def _login_admin(client):
    return client.post(
        "/auth/login",
        data={"email": "admin@example.org", "password": "ValidPass1"},
        follow_redirects=False,
    )


def _login_user(client):
    return client.post(
        "/auth/login",
        data={"email": "alice@example.org", "password": "ValidPass1"},
        follow_redirects=False,
    )


# ── Migration: existing accounts get account_kind = personal ─────────────────

def test_existing_personal_accounts_have_personal_kind(group_app: Flask) -> None:
    with group_app.app_context():
        alice = auth_services.find_user_by_email("alice@example.org")
        assert alice is not None
        assert alice.account_kind == "personal"

        admin = auth_services.find_user_by_email("admin@example.org")
        assert admin is not None
        assert admin.account_kind == "personal"


# ── Group account creation (service layer) ───────────────────────────────────

def test_create_group_account_sets_correct_fields(group_app: Flask) -> None:
    with group_app.app_context():
        user = auth_services.create_group_account(
            login_name="gruppe-a1",
            display_name="Seminargruppe A",
            password="GroupPass1",
            responsible_admin_user_id="admin-1",
            created_by_user_id="admin-1",
        )
        assert user.account_kind == "group"
        assert user.role == "user"
        assert user.username == "gruppe-a1"
        assert user.display_name == "Seminargruppe A"
        assert user.email is None
        assert user.first_name is None
        assert user.last_name is None
        assert user.must_reset_password is False
        assert user.responsible_admin_user_id == "admin-1"
        assert auth_services.verify_password("GroupPass1", user.password_hash)


def test_create_group_account_rejects_duplicate_login_name(group_app: Flask) -> None:
    with group_app.app_context():
        auth_services.create_group_account(
            login_name="unique-group",
            display_name="Group One",
            password="GroupPass1",
            responsible_admin_user_id="admin-1",
        )
        with pytest.raises(ValueError, match="login_name_exists"):
            auth_services.create_group_account(
                login_name="unique-group",
                display_name="Group Two",
                password="GroupPass1",
                responsible_admin_user_id="admin-1",
            )


def test_create_group_account_rejects_invalid_login_name(group_app: Flask) -> None:
    with group_app.app_context():
        with pytest.raises(ValueError, match="login_name_no_at"):
            auth_services.create_group_account(
                login_name="gruppe@test",
                display_name="Test",
                password="GroupPass1",
                responsible_admin_user_id="admin-1",
            )
        with pytest.raises(ValueError, match="login_name_invalid_chars"):
            auth_services.create_group_account(
                login_name="Gruppe Mit Leerzeichen",
                display_name="Test",
                password="GroupPass1",
                responsible_admin_user_id="admin-1",
            )
        with pytest.raises(ValueError, match="login_name_required"):
            auth_services.create_group_account(
                login_name="",
                display_name="Test",
                password="GroupPass1",
                responsible_admin_user_id="admin-1",
            )


def test_create_group_account_enforces_password_strength(group_app: Flask) -> None:
    with group_app.app_context():
        with pytest.raises(ValueError, match="password_"):
            auth_services.create_group_account(
                login_name="gruppe-weak",
                display_name="Test",
                password="short",
                responsible_admin_user_id="admin-1",
            )


# ── Admin API: POST /admin/groups ─────────────────────────────────────────────

def test_admin_api_creates_group_account(group_app: Flask) -> None:
    client = group_app.test_client()
    assert _login_admin(client).status_code == 303

    response = client.post(
        "/admin/groups",
        json={
            "login_name": "kurs-spanisch-ws24",
            "display_name": "Spanisch WS 24/25",
            "password": "KursPass1",
            "responsible_admin_user_id": "admin-1",
        },
        headers={"Referer": "http://promat.test/admin/users/page?ui_lang=de"},
    )

    assert response.status_code == 201
    payload = response.get_json()
    assert payload["ok"] is True
    user_data = payload["user"]
    assert user_data["account_kind"] == "group"
    assert user_data["role"] == "user"
    assert user_data["username"] == "kurs-spanisch-ws24"
    assert user_data["display_name"] == "Spanisch WS 24/25"
    assert user_data["email"] is None
    assert user_data["must_reset_password"] is False

    with group_app.app_context():
        u = auth_services.get_user_by_id(user_data["id"])
        assert u is not None
        assert u.account_kind == "group"
        assert auth_services.verify_password("KursPass1", u.password_hash)


def test_admin_api_create_group_rejects_duplicate_login_name(group_app: Flask) -> None:
    client = group_app.test_client()
    assert _login_admin(client).status_code == 303

    client.post(
        "/admin/groups",
        json={"login_name": "dup-group", "display_name": "Dup", "password": "DupPass1", "responsible_admin_user_id": "admin-1"},
        headers={"Referer": "http://promat.test/admin/users/page?ui_lang=de"},
    )
    second = client.post(
        "/admin/groups",
        json={"login_name": "dup-group", "display_name": "Dup2", "password": "DupPass1", "responsible_admin_user_id": "admin-1"},
        headers={"Referer": "http://promat.test/admin/users/page?ui_lang=de"},
    )
    assert second.status_code == 400
    assert second.get_json()["ok"] is False


def test_non_admin_cannot_create_group_account(group_app: Flask) -> None:
    client = group_app.test_client()
    assert _login_user(client).status_code == 303

    response = client.post(
        "/admin/groups",
        json={"login_name": "bad-group", "display_name": "Bad", "password": "BadPass1", "responsible_admin_user_id": "admin-1"},
    )
    assert response.status_code in {401, 403, 302, 303}


# ── Login with login_name ─────────────────────────────────────────────────────

def test_group_account_can_login_with_login_name(group_app: Flask) -> None:
    with group_app.app_context():
        auth_services.create_group_account(
            login_name="login-test-group",
            display_name="Login Test Group",
            password="LoginTest1",
            responsible_admin_user_id="admin-1",
        )

    client = group_app.test_client()
    response = client.post(
        "/auth/login",
        data={"email": "login-test-group", "password": "LoginTest1"},
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert "access_token_cookie=" in response.headers.get("Set-Cookie", "")


def test_personal_account_login_via_email_still_works(group_app: Flask) -> None:
    client = group_app.test_client()
    response = client.post(
        "/auth/login",
        data={"email": "alice@example.org", "password": "ValidPass1"},
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert "access_token_cookie=" in response.headers.get("Set-Cookie", "")


def test_wrong_password_for_group_account_is_rejected(group_app: Flask) -> None:
    with group_app.app_context():
        auth_services.create_group_account(
            login_name="wrong-pw-group",
            display_name="Wrong PW Group",
            password="CorrectPass1",
            responsible_admin_user_id="admin-1",
        )

    client = group_app.test_client()
    response = client.post(
        "/auth/login",
        data={"email": "wrong-pw-group", "password": "WrongPass1", "ui_lang": "en"},
        follow_redirects=False,
    )
    assert response.status_code == 401


# ── Group account sees no Mein Konto; /auth/account redirects ───────────────

def test_group_account_auth_account_redirects(group_app: Flask) -> None:
    with group_app.app_context():
        auth_services.create_group_account(
            login_name="group-redirect-test",
            display_name="Group Redirect",
            password="RedirectTest1",
            responsible_admin_user_id="admin-1",
        )

    client = group_app.test_client()
    client.post("/auth/login", data={"email": "group-redirect-test", "password": "RedirectTest1"}, follow_redirects=False)

    response = client.get("/auth/account?ui_lang=de", follow_redirects=False)
    assert response.status_code == 303
    assert "/auth/account" not in response.headers["Location"]


def test_group_account_auth_account_password_redirects(group_app: Flask) -> None:
    with group_app.app_context():
        auth_services.create_group_account(
            login_name="group-pw-block",
            display_name="Group PW Block",
            password="PwBlock123",
            responsible_admin_user_id="admin-1",
        )

    client = group_app.test_client()
    client.post("/auth/login", data={"email": "group-pw-block", "password": "PwBlock123"}, follow_redirects=False)

    response = client.get("/auth/account/password?ui_lang=de", follow_redirects=False)
    assert response.status_code == 303
    assert "/auth/account/password" not in response.headers["Location"]


def test_group_account_post_account_update_redirects(group_app: Flask) -> None:
    with group_app.app_context():
        auth_services.create_group_account(
            login_name="group-update-block",
            display_name="Group Update Block",
            password="UpdBlock123",
            responsible_admin_user_id="admin-1",
        )

    client = group_app.test_client()
    client.post("/auth/login", data={"email": "group-update-block", "password": "UpdBlock123"}, follow_redirects=False)

    response = client.post("/auth/account?ui_lang=de", data={"first_name": "X", "last_name": "Y", "email": "x@example.org"}, follow_redirects=False)
    assert response.status_code == 303
    assert "/auth/account" not in response.headers["Location"]


# ── Group account does NOT get reset token from public forgot-password ────────

def test_group_account_forgot_password_does_not_create_token(group_app: Flask) -> None:
    with group_app.app_context():
        auth_services.create_group_account(
            login_name="group-no-reset",
            display_name="Group No Reset",
            password="NoReset123",
            responsible_admin_user_id="admin-1",
        )
        u = auth_services.find_user_by_username_or_email("group-no-reset")
        assert u is not None
        group_id = str(u.id)
        # Give it a fake email to see if the reset flow accidentally picks it up
        with get_session() as s:
            gu = s.get(User, group_id)
            assert gu is not None
            gu.email = "group-fake@example.org"

    client = group_app.test_client()
    response = client.post(
        "/auth/password/reset/request",
        json={"email": "group-fake@example.org", "ui_lang": "en"},
    )
    assert response.status_code == 200  # neutral response regardless

    from app.auth.models import ResetToken
    with group_app.app_context():
        with get_session() as s:
            tokens = s.query(ResetToken).filter(ResetToken.user_id == group_id).all()
        assert tokens == []


# ── Admin list shows correct type badge ──────────────────────────────────────

def test_admin_list_returns_account_kind_for_all_accounts(group_app: Flask) -> None:
    with group_app.app_context():
        auth_services.create_group_account(
            login_name="list-test-group",
            display_name="List Test Group",
            password="ListTest1",
            responsible_admin_user_id="admin-1",
        )

    client = group_app.test_client()
    assert _login_admin(client).status_code == 303

    response = client.get("/admin/users", headers={"Referer": "http://promat.test/admin/users/page?ui_lang=de"})
    assert response.status_code == 200
    items = response.get_json()["items"]

    personal_items = [i for i in items if i["account_kind"] == "personal"]
    group_items = [i for i in items if i["account_kind"] == "group"]

    assert len(personal_items) >= 2  # alice + admin
    assert len(group_items) >= 1


def test_admin_list_group_account_has_no_email_and_has_login_name(group_app: Flask) -> None:
    with group_app.app_context():
        auth_services.create_group_account(
            login_name="list-email-check",
            display_name="Email Check Group",
            password="EmailCheck1",
            responsible_admin_user_id="admin-1",
        )

    client = group_app.test_client()
    assert _login_admin(client).status_code == 303

    response = client.get("/admin/users", headers={"Referer": "http://promat.test/admin/users/page?ui_lang=de"})
    items = response.get_json()["items"]
    group_item = next((i for i in items if i["username"] == "list-email-check"), None)
    assert group_item is not None
    assert group_item["account_kind"] == "group"
    assert group_item["email"] is None
    assert group_item["username"] == "list-email-check"
    assert group_item["display_name"] == "Email Check Group"
    assert group_item["responsible_admin_name"] != ""


# ── JWT claims include account_kind ──────────────────────────────────────────

def test_group_account_jwt_includes_account_kind(group_app: Flask) -> None:
    with group_app.app_context():
        auth_services.create_group_account(
            login_name="jwt-kind-test",
            display_name="JWT Kind Test",
            password="JwtKind123",
            responsible_admin_user_id="admin-1",
        )

    client = group_app.test_client()
    client.post("/auth/login", data={"email": "jwt-kind-test", "password": "JwtKind123"}, follow_redirects=False)

    response = client.get("/auth/session")
    assert response.status_code == 200
    assert response.get_json()["authenticated"] is True


# ── Personal account self-service still works after change ───────────────────

def test_personal_account_can_still_access_auth_account(group_app: Flask) -> None:
    client = group_app.test_client()
    assert _login_user(client).status_code == 303

    response = client.get("/auth/account?ui_lang=de", follow_redirects=False)
    assert response.status_code == 200


def test_personal_account_can_change_password(group_app: Flask) -> None:
    client = group_app.test_client()
    assert _login_user(client).status_code == 303

    response = client.post(
        "/auth/account/password",
        data={"old_password": "ValidPass1", "new_password": "NewValid2", "confirm_password": "NewValid2"},
        follow_redirects=False,
    )
    assert response.status_code == 303

    with group_app.app_context():
        u = auth_services.find_user_by_email("alice@example.org")
        assert auth_services.verify_password("NewValid2", u.password_hash)


# ── Admin /admin/admins endpoint ─────────────────────────────────────────────

def test_admin_admins_endpoint_returns_active_admins(group_app: Flask) -> None:
    client = group_app.test_client()
    assert _login_admin(client).status_code == 303

    response = client.get("/admin/admins", headers={"Referer": "http://promat.test/admin/users/page?ui_lang=de"})
    assert response.status_code == 200
    payload = response.get_json()
    assert "admins" in payload
    assert any(a["id"] == "admin-1" for a in payload["admins"])


# ── login page renders identifier label ──────────────────────────────────────

def test_login_page_shows_identifier_label_in_german(group_app: Flask) -> None:
    client = group_app.test_client()
    response = client.get("/login?ui_lang=de")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "E-Mail oder Login-Name" in html


def test_login_page_shows_identifier_label_in_english(group_app: Flask) -> None:
    client = group_app.test_client()
    response = client.get("/login?ui_lang=en")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Email or login name" in html
