"""Server-side session state, e-mail change re-authentication and admin account invariants (TI-04, TI-25).

A signed access token must never outlive the account state it was issued for. These tests run against the composed
application (``real_app_factory``) and change the account state *after* the token was issued.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import os
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
os.environ.setdefault("FLASK_ENV", "development")
os.environ.setdefault("PROMAT_RUNTIME_ROOT", str(Path(__file__).resolve().parents[2]))
os.environ.setdefault("PROMAT_PUBLIC_ROOT", str(Path(__file__).resolve().parents[2] / "public"))

PASSWORD = "ValidPass1"
PROTECTED_PAGE = "/de/research/spanish/speakers"
PROTECTED_API = "/api/research/sets?corpus_language=spanish"


def _add_user(user_id: str, username: str, *, role: str = "user", **fields) -> None:
    from app.auth import services as auth_services
    from app.auth.models import User
    from app.extensions.sqlalchemy_ext import get_session

    now = datetime.now(timezone.utc)
    values = dict(
        id=user_id,
        username=username,
        email=f"{username}@example.org",
        password_hash=auth_services.hash_password(PASSWORD),
        role=role,
        is_active=True,
        must_reset_password=False,
        created_at=now,
        updated_at=now,
        first_name=username.title(),
        last_name="Example",
        display_name=f"{username.title()} Example",
    )
    values.update(fields)
    with get_session() as session:
        session.add(User(**values))


def _update_user(user_id: str, **fields) -> None:
    from app.auth.models import User
    from app.extensions.sqlalchemy_ext import get_session

    with get_session() as session:
        user = session.get(User, user_id)
        for key, value in fields.items():
            setattr(user, key, value)


def _login(flask_app, username: str, password: str = PASSWORD):
    client = flask_app.test_client()
    identifier = username if "@" in username else f"{username}@example.org"
    response = client.post("/auth/login", data={"email": identifier, "password": password})
    assert response.status_code == 303, response.get_data(as_text=True)
    return client


def _token(client) -> str:
    cookie = client.get_cookie("access_token_cookie", domain="localhost")
    assert cookie is not None
    return cookie.value


def _client_with_token(flask_app, token: str):
    client = flask_app.test_client()
    client.set_cookie("access_token_cookie", token, domain="localhost")
    return client


def _is_rejected(client) -> bool:
    page = client.get(PROTECTED_PAGE)
    api = client.get(PROTECTED_API, headers={"Accept": "application/json"})
    return page.status_code in {302, 303} and page.headers["Location"].startswith("/login") and api.status_code == 401


@pytest.fixture
def app_with_user(real_app_factory, fixture_runtime_root):
    flask_app = real_app_factory(runtime_root=fixture_runtime_root)
    with flask_app.app_context():
        _add_user("user-1", "alice")
        _add_user("admin-1", "ada", role="admin")
    return flask_app


def test_a_valid_token_is_accepted(app_with_user) -> None:
    client = _login(app_with_user, "alice")

    assert client.get(PROTECTED_PAGE).status_code == 200
    assert client.get(PROTECTED_API).status_code == 200


def test_logout_ends_the_copied_token_server_side(app_with_user) -> None:
    client = _login(app_with_user, "alice")
    stolen = _token(client)
    assert client.post("/auth/logout").status_code == 303

    assert _is_rejected(_client_with_token(app_with_user, stolen))


def test_logout_of_one_session_keeps_other_sessions_of_the_same_account(app_with_user) -> None:
    first = _login(app_with_user, "alice")
    second = _login(app_with_user, "alice")
    first.post("/auth/logout")

    assert second.get(PROTECTED_PAGE).status_code == 200


def test_logout_removes_expired_revocations_only(app_with_user) -> None:
    from app.auth.models import RevokedToken
    from app.extensions.sqlalchemy_ext import get_session

    with app_with_user.app_context():
        with get_session() as session:
            session.add(RevokedToken(jti="old", user_id="x", expires_at=datetime.now(timezone.utc) - timedelta(hours=1), revoked_at=datetime.now(timezone.utc)))
    _login(app_with_user, "alice").post("/auth/logout")

    with app_with_user.app_context():
        with get_session() as session:
            remaining = {row.jti for row in session.query(RevokedToken).all()}
    assert "old" not in remaining and len(remaining) == 1


@pytest.mark.parametrize(
    ("label", "change"),
    [
        ("deactivated", {"is_active": False}),
        ("soft-deleted", {"deleted_at": datetime.now(timezone.utc), "is_active": False}),
        ("soft-deleted but still flagged active", {"deleted_at": datetime.now(timezone.utc)}),
        ("access expired", {"access_expires_at": datetime.now(timezone.utc) - timedelta(minutes=1)}),
        ("not yet valid", {"valid_from": datetime.now(timezone.utc) + timedelta(days=1)}),
        ("must reset password after issuance", {"must_reset_password": True}),
        ("role changed to admin", {"role": "admin"}),
        ("account kind changed", {"account_kind": "group"}),
    ],
)
def test_state_changes_after_issuance_take_effect_on_the_next_request(app_with_user, label: str, change: dict) -> None:
    client = _login(app_with_user, "alice")
    assert client.get(PROTECTED_PAGE).status_code == 200

    with app_with_user.app_context():
        _update_user("user-1", **change)

    assert _is_rejected(client), label


def test_demoted_admin_loses_admin_access_immediately(app_with_user) -> None:
    client = _login(app_with_user, "ada")
    assert client.get("/admin/users").status_code == 200

    with app_with_user.app_context():
        _update_user("admin-1", role="user")

    assert client.get("/admin/users").status_code in {302, 303, 401}
    assert client.get("/admin/users", headers={"Accept": "application/json"}).status_code == 401


def test_promoted_user_gets_admin_only_with_a_fresh_login(app_with_user) -> None:
    client = _login(app_with_user, "alice")
    with app_with_user.app_context():
        _update_user("user-1", role="admin")

    assert client.get("/admin/users", headers={"Accept": "application/json"}).status_code == 401
    assert _login(app_with_user, "alice").get("/admin/users").status_code == 200


def test_token_for_an_unknown_subject_is_rejected_even_with_admin_claims(app_with_user) -> None:
    from flask_jwt_extended import create_access_token

    with app_with_user.app_context():
        forged = create_access_token(
            identity="ghost-user",
            additional_claims={"role": "admin", "username": "ghost", "must_reset_password": False, "account_kind": "personal"},
        )

    client = _client_with_token(app_with_user, forged)
    assert _is_rejected(client)
    assert client.get("/admin/users", headers={"Accept": "application/json"}).status_code == 401


def test_a_token_without_identity_claims_is_rejected(app_with_user) -> None:
    from flask_jwt_extended import create_access_token

    with app_with_user.app_context():
        bare = create_access_token(identity="user-1")

    assert _is_rejected(_client_with_token(app_with_user, bare))


def test_session_endpoint_reports_a_revoked_or_disabled_session_as_signed_out(app_with_user) -> None:
    client = _login(app_with_user, "alice")
    assert client.get("/auth/session").get_json()["authenticated"] is True

    with app_with_user.app_context():
        _update_user("user-1", is_active=False)

    assert client.get("/auth/session").get_json()["authenticated"] is False


def test_lockout_after_failed_logins_does_not_end_existing_sessions(app_with_user) -> None:
    client = _login(app_with_user, "alice")
    with app_with_user.app_context():
        _update_user("user-1", locked_until=datetime.now(timezone.utc) + timedelta(minutes=10))

    assert client.get(PROTECTED_PAGE).status_code == 200


# --- e-mail change needs the current password ----------------------------------------------------------------


def _post_account(client, **form):
    data = {"first_name": "Alice", "last_name": "Example", "email": "alice@example.org"}
    data.update(form)
    return client.post("/auth/account", data=data)


def _email_of(flask_app, user_id: str) -> str:
    from app.auth import services as auth_services

    with flask_app.app_context():
        return auth_services.get_user_by_id(user_id).email


def test_email_change_without_the_current_password_is_rejected(app_with_user) -> None:
    client = _login(app_with_user, "alice")

    response = _post_account(client, email="attacker@evil.example")

    assert response.status_code == 400
    assert _email_of(app_with_user, "user-1") == "alice@example.org"


def test_email_change_with_a_wrong_password_is_rejected(app_with_user) -> None:
    client = _login(app_with_user, "alice")

    assert _post_account(client, email="new@example.org", current_password="WrongPass9").status_code == 400
    assert _email_of(app_with_user, "user-1") == "alice@example.org"


def test_email_change_with_the_correct_password_succeeds_and_login_follows_the_new_address(app_with_user) -> None:
    client = _login(app_with_user, "alice")

    response = _post_account(client, email="Alice.New@Example.org", current_password=PASSWORD)

    assert response.status_code == 303
    assert _email_of(app_with_user, "user-1") == "alice.new@example.org"
    assert app_with_user.test_client().post("/auth/login", data={"email": "alice.new@example.org", "password": PASSWORD}).status_code == 303


def test_name_change_without_email_change_needs_no_password(app_with_user) -> None:
    client = _login(app_with_user, "alice")

    assert _post_account(client, first_name="Alicia").status_code == 303


@pytest.mark.parametrize("bad_email", ["no-at-sign", "a@b", "two@@example.org"])
def test_invalid_new_email_is_rejected_even_with_the_password(app_with_user, bad_email: str) -> None:
    client = _login(app_with_user, "alice")

    assert _post_account(client, email=bad_email, current_password=PASSWORD).status_code == 400
    assert _email_of(app_with_user, "user-1") == "alice@example.org"


def test_email_change_to_an_address_in_use_is_rejected(app_with_user) -> None:
    client = _login(app_with_user, "alice")

    assert _post_account(client, email="ada@example.org", current_password=PASSWORD).status_code == 400


# --- admin invariants (docs/spec/auth-accounts.md) -----------------------------------------------------------


@pytest.fixture
def admin_client(app_with_user):
    from app.auth import services as auth_services

    with app_with_user.app_context():
        group = auth_services.create_group_account(
            login_name="seminar-1", display_name="Seminar 1", password="GroupPass-12345", responsible_admin_user_id="admin-1", created_by_user_id="admin-1"
        )
        group_id = str(group.id)
        _add_user("deleted-1", "dora", deleted_at=datetime.now(timezone.utc), is_active=False)
    return _login(app_with_user, "ada"), group_id


@pytest.mark.parametrize(
    "payload",
    [
        {"role": "admin"},
        {"email": "group@example.org"},
        {"first_name": "Gina"},
        {"last_name": "Group"},
    ],
)
def test_admin_patch_cannot_turn_a_group_account_into_a_personal_or_admin_account(admin_client, payload: dict) -> None:
    client, group_id = admin_client

    response = client.patch(f"/admin/users/{group_id}", json=payload)

    assert response.status_code == 400, payload
    from app.auth import services as auth_services

    user = auth_services.get_user_by_id(group_id)
    assert user.role == "user" and user.email is None and user.first_name is None


def test_admin_patch_may_still_deactivate_a_group_account_and_keep_its_role(admin_client) -> None:
    client, group_id = admin_client

    assert client.patch(f"/admin/users/{group_id}", json={"role": "user", "is_active": False}).status_code == 200


def test_admin_patch_cannot_modify_a_deleted_account(admin_client) -> None:
    client, _ = admin_client

    for payload in ({"is_active": True}, {"role": "admin"}, {"email": "revive@example.org"}):
        assert client.patch("/admin/users/deleted-1", json=payload).status_code == 400, payload


def test_admin_patch_rejects_a_malformed_email_and_clearing_the_email(admin_client) -> None:
    client, _ = admin_client

    assert client.patch("/admin/users/user-1", json={"email": "not-an-address"}).status_code == 400
    assert client.patch("/admin/users/user-1", json={"email": ""}).status_code == 400


def test_group_accounts_get_no_password_reset_state_from_the_admin_routes(admin_client) -> None:
    client, group_id = admin_client

    for route in ("reset-password", "invite"):
        assert client.post(f"/admin/users/{group_id}/{route}", json={}).status_code == 400
    from app.auth import services as auth_services

    assert auth_services.get_user_by_id(group_id).must_reset_password is False


def test_group_update_requires_an_active_admin_as_responsible_person(admin_client) -> None:
    client, group_id = admin_client

    assert client.patch(f"/admin/groups/{group_id}", json={"responsible_admin_user_id": "user-1"}).status_code == 400
    assert client.patch(f"/admin/groups/{group_id}", json={"responsible_admin_user_id": "nobody"}).status_code == 400
    assert client.patch(f"/admin/groups/{group_id}", json={"responsible_admin_user_id": "admin-1"}).status_code == 200


def test_the_last_admin_still_cannot_be_demoted_or_deactivated(admin_client) -> None:
    client, _ = admin_client

    assert client.patch("/admin/users/admin-1", json={"role": "user"}).status_code == 400
    assert client.patch("/admin/users/admin-1", json={"is_active": False}).status_code == 400
