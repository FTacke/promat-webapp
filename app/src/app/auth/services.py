"""Auth service helpers: hashing, token generation, token rotation, account checks.

Intended to be used by the DB-backed auth routes. Uses SQLAlchemy sessions
from extensions.sqlalchemy_ext.get_session.
"""

from __future__ import annotations

import hashlib
import secrets
import uuid
from dataclasses import dataclass
from datetime import date
from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Tuple
from urllib.parse import quote

from flask import current_app
from flask_jwt_extended import create_access_token
from passlib.hash import argon2, bcrypt
import bcrypt as _bcrypt_module  # fallback direct bcrypt usage when passlib backend behaves oddly
from sqlalchemy import select
from werkzeug.security import (
    check_password_hash,
)  # supports scrypt, pbkdf2_sha256, etc.

from ..branding import BRANDING
from ..i18n import translate
from ..extensions.sqlalchemy_ext import get_session
from . import Role, normalize_role_value
from .models import User, RefreshToken, ResetToken

# NOTE: Old counter metrics removed - analytics now handled by /api/analytics/event
# Auth events are no longer tracked (privacy-focused approach)


# Type for account status
@dataclass
class AccountStatus:
    ok: bool
    code: Optional[str] = None
    message: Optional[str] = None


_UNSET = object()


# Password hashing
def hash_password(plain: str) -> str:
    algo = current_app.config.get("AUTH_HASH_ALGO", "argon2")
    if algo == "argon2":
        # passlib argon2 uses reasonable defaults; we allow tuning via config
        return argon2.using(
            time_cost=current_app.config.get("AUTH_ARGON2_TIME_COST", 2),
            memory_cost=current_app.config.get("AUTH_ARGON2_MEMORY_COST", 102400),
            parallelism=current_app.config.get("AUTH_ARGON2_PARALLELISM", 4),
        ).hash(plain)
    else:
        # fallback to bcrypt
        # bcrypt (the underlying C library) has a 72-byte input limit; passlib tries to detect
        # features by hashing very long secrets which can raise a ValueError in some envs.
        # Truncate input to 72 bytes when using bcrypt and fall back to the bcrypt module
        # if passlib's handler raises an error.
        try:
            # try the passlib wrapper first (handles salt/cost config)
            return bcrypt.hash(plain)
        except Exception:
            # deterministic truncation to bcrypt's max 72 bytes (utf-8)
            b = plain.encode("utf-8")[:72]
            hashed = _bcrypt_module.hashpw(b, _bcrypt_module.gensalt())
            # bcrypt.hashpw returns bytes
            return hashed.decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a password against a stored hash.

    Supports multiple hash formats:
    - Werkzeug (scrypt, pbkdf2_sha256) - used by generate_password_hash()
    - argon2 - modern algorithm
    - bcrypt - legacy but still common

    For development environments the runtime hashing backend may differ from
    whatever was available when a password hash was created (e.g. argon2
    backend missing). To make local logins resilient we attempt verification
    using multiple methods.
    """
    # Try Werkzeug first (handles scrypt:, pbkdf2:sha256:, etc.)
    # This is the most common format when using Flask/Werkzeug's generate_password_hash
    try:
        if check_password_hash(hashed, plain):
            return True
    except Exception:
        pass

    # Try argon2 (best/modern algorithm)
    try:
        if argon2.verify(plain, hashed):
            return True
    except Exception:
        pass

    # Try passlib bcrypt
    try:
        if bcrypt.verify(plain, hashed):
            return True
    except Exception:
        # passlib bcrypt failed — try low-level bcrypt.checkpw with truncation
        try:
            b = plain.encode("utf-8")[:72]
            return _bcrypt_module.checkpw(b, hashed.encode("utf-8"))
        except Exception:
            pass

    return False


# Password strength validation
def validate_password_strength(password: str) -> tuple[bool, str | None]:
    """Validate password meets minimum security requirements.

    Requirements:
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit

    Returns:
        Tuple of (is_valid, error_message)
    """
    import re

    if len(password) < 8:
        return False, "password_too_short"

    if not re.search(r"[A-Z]", password):
        return False, "password_missing_uppercase"

    if not re.search(r"[a-z]", password):
        return False, "password_missing_lowercase"

    if not re.search(r"\d", password):
        return False, "password_missing_digit"

    return True, None


# Access token creation
def create_access_token_for_user(user: User) -> str:
    expires_seconds = current_app.config.get("ACCESS_TOKEN_EXP", 900)
    expires_delta = timedelta(seconds=int(expires_seconds))
    claims = {
        "sub": str(user.id),
        "username": user.username,
        "role": normalize_role_value(user.role),
        "is_active": bool(user.is_active),
        "must_reset_password": bool(user.must_reset_password),
    }
    token = create_access_token(
        identity=str(user.id), additional_claims=claims, expires_delta=expires_delta
    )
    return token


# Refresh token handling
def _hash_refresh_token(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _ensure_utc(dt: Optional[datetime]) -> Optional[datetime]:
    """Return a timezone-aware datetime in UTC for naive datetimes (SQLite may return naive datetimes)."""
    if dt is None:
        return None
    return dt if dt.tzinfo is not None else dt.replace(tzinfo=timezone.utc)


def create_refresh_token_for_user(
    user: User, user_agent: Optional[str] = None, ip_address: Optional[str] = None
) -> Tuple[str, RefreshToken]:
    raw = secrets.token_urlsafe(64)
    token_hash = _hash_refresh_token(raw)
    expires_at = datetime.now(timezone.utc) + timedelta(
        seconds=int(current_app.config.get("REFRESH_TOKEN_EXP", 2592000))
    )

    token_id = str(uuid.uuid4())
    rt = RefreshToken(
        token_id=token_id,
        user_id=str(user.id),
        token_hash=token_hash,
        created_at=datetime.now(timezone.utc),
        expires_at=expires_at,
        user_agent=user_agent,
        ip_address=ip_address,
    )

    with get_session() as session:
        session.add(rt)

    return raw, rt


def rotate_refresh_token(
    old_raw_token: str, user_agent: Optional[str], ip_address: Optional[str]
) -> Tuple[Optional[str], Optional[RefreshToken], str]:
    """Rotate an existing raw refresh token.

    Returns tuple (new_raw, new_model, status) where status is one of:
    - 'ok' (success)
    - 'invalid' (token not found/invalid)
    - 'expired' (token expired)
    - 'reused' (reuse detected)
    """
    # use module-level helper
    old_hash = _hash_refresh_token(old_raw_token)
    marker = f"rotating-{uuid.uuid4()}"

    with get_session() as session:
        # Attempt to mark the row as rotating in a single atomic UPDATE so concurrent
        # rotations race against the DB and only one will win.
        update_count = (
            session.query(RefreshToken)
            .filter(
                RefreshToken.token_hash == old_hash,
                RefreshToken.replaced_by.is_(None),
                RefreshToken.revoked_at.is_(None),
            )
            .update({RefreshToken.replaced_by: marker}, synchronize_session=False)
        )

        # If we couldn't mark the row, inspect why
        if update_count == 0:
            stmt = select(RefreshToken).where(RefreshToken.token_hash == old_hash)
            result = session.execute(stmt).scalars().first()
            if not result:
                return None, None, "invalid"
            token_row: RefreshToken = result

            if (
                _ensure_utc(token_row.expires_at) < datetime.now(timezone.utc)
                or token_row.revoked_at is not None
            ):
                return None, None, "expired"

            # If the token already had a replacement, treat as reuse
            if token_row.replaced_by is not None and token_row.replaced_by != marker:
                # detected reuse -> revoke all tokens for this user
                session.query(RefreshToken).filter(
                    RefreshToken.user_id == token_row.user_id
                ).update({RefreshToken.revoked_at: datetime.now(timezone.utc)})
                return None, None, "reused"

            # Fallback - unknown state
            return None, None, "invalid"

        # reload the token row we claimed
        stmt = select(RefreshToken).where(RefreshToken.token_hash == old_hash)
        token_row = session.execute(stmt).scalars().first()

        # create new token
        new_raw = secrets.token_urlsafe(64)
        new_hash = _hash_refresh_token(new_raw)
        new_id = str(uuid.uuid4())
        new_expires = datetime.now(timezone.utc) + timedelta(
            seconds=int(current_app.config.get("REFRESH_TOKEN_EXP", 2592000))
        )

        new_row = RefreshToken(
            token_id=new_id,
            user_id=token_row.user_id,
            token_hash=new_hash,
            created_at=datetime.now(timezone.utc),
            expires_at=new_expires,
            user_agent=user_agent,
            ip_address=ip_address,
            replaced_by=None,
        )

        # set replaced_by on old row and optionally set last_used_at
        token_row.replaced_by = new_id
        token_row.last_used_at = datetime.now(timezone.utc)

        session.add(new_row)

    return new_raw, new_row, "ok"


def revoke_all_refresh_tokens_for_user(user_id: str) -> None:
    with get_session() as session:
        session.query(RefreshToken).filter(
            RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None)
        ).update({RefreshToken.revoked_at: datetime.now(timezone.utc)})


def revoke_refresh_token_by_raw(raw: str) -> bool:
    """Mark a single refresh token (by raw value) as revoked. Returns True if found."""
    h = _hash_refresh_token(raw)
    with get_session() as session:
        stmt = select(RefreshToken).where(RefreshToken.token_hash == h)
        r = session.execute(stmt).scalars().first()
        if not r:
            return False
        r.revoked_at = datetime.now(timezone.utc)
        return True


def anonymize_user(user_id: str) -> None:
    """Anonymize a soft-deleted user by removing PII and marking fields anonymous.

    This function implements the post-deletion pseudonymization step (e.g.
    after the configured retention window). It replaces username/email with a
    non-reversible placeholder and clears user-identifying fields.
    """
    with get_session() as session:
        stmt = select(User).where(User.id == user_id)
        user = session.execute(stmt).scalars().first()
        if not user:
            raise KeyError("user_not_found")

        # ensure user was already soft-deleted
        if not user.deleted_at:
            raise ValueError("user_not_deleted")

        placeholder = f"deleted-{user_id}"
        user.username = placeholder
        user.email = f"{placeholder}@example.invalid"
        user.display_name = None
        # invalidate password (store a random hash)
        user.password_hash = hash_password(secrets.token_urlsafe(32))
        user.is_active = False
        # clear last login info
        user.last_login_at = None

        # revoke refresh/reset tokens for user
        session.query(RefreshToken).filter(RefreshToken.user_id == user_id).update(
            {RefreshToken.revoked_at: datetime.now(timezone.utc)}
        )
        session.query(ResetToken).filter(ResetToken.user_id == user_id).update(
            {ResetToken.used_at: datetime.now(timezone.utc)}
        )


def anonymize_soft_deleted_users_older_than(days: int) -> int:
    """Anonymize all users that were soft-deleted at least `days` days ago.

    Returns the number of users anonymized.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=int(days))
    anonymized = 0
    with get_session() as session:
        stmt = select(User).where(
            User.deleted_at.is_not(None), User.deleted_at <= cutoff
        )
        rows = session.execute(stmt).scalars().all()
        for u in rows:
            anonymize_user(str(u.id))
            anonymized += 1
    return anonymized


# Account check
def check_account_status(user: User) -> AccountStatus:
    now = datetime.now(timezone.utc)
    if not user.is_active:
        return AccountStatus(False, "account_inactive", "Account is not active")
    if user.deleted_at is not None:
        return AccountStatus(False, "account_deleted", "Account deleted")
    if user.valid_from and _ensure_utc(user.valid_from) > now:
        return AccountStatus(False, "account_not_yet_valid", "Account is not valid yet")
    if user.access_expires_at and _ensure_utc(user.access_expires_at) < now:
        return AccountStatus(False, "account_expired", "Account access expired")
    if user.locked_until and _ensure_utc(user.locked_until) > now:
        return AccountStatus(False, "account_locked", "Account temporarily locked")
    return AccountStatus(True)


# Helper: lookup user by username/email
def find_user_by_username_or_email(identifier: str) -> Optional[User]:
    with get_session() as session:
        stmt = select(User).where(User.username == identifier.lower())
        user = session.execute(stmt).scalars().first()
        if user:
            return user
        stmt2 = select(User).where(User.email == identifier.lower())
        return session.execute(stmt2).scalars().first()


def normalize_email(email: str) -> str:
    return (email or "").strip().lower()


def normalize_role(role: str | Role | None) -> str:
    try:
        return normalize_role_value(role)
    except ValueError as exc:  # pragma: no cover - thin guard
        raise ValueError("role_invalid") from exc


def build_display_name(
    *,
    first_name: str | None = None,
    last_name: str | None = None,
    display_name: str | None = None,
    email: str | None = None,
    username: str | None = None,
) -> str | None:
    parts = [part.strip() for part in (first_name, last_name) if part and part.strip()]
    if parts:
        return " ".join(parts)
    fallback = (display_name or "").strip() or (email or "").strip() or (username or "").strip()
    return fallback or None


def access_request_contact_email() -> str:
    return current_app.config.get("AUTH_ACCESS_REQUEST_EMAIL") or BRANDING["contact_email"]


def access_request_subject() -> str:
    return current_app.config.get("AUTH_ACCESS_REQUEST_SUBJECT") or 'Zugangsanfrage "Pronunciation Matters"'


def build_access_request_mailto(ui_lang: str) -> str:
    body = translate(
        ui_lang,
        "auth.access_request.body",
        app_name=BRANDING["app_display_name"],
        institution=BRANDING["institution_name"],
    )
    return f"mailto:{access_request_contact_email()}?subject={quote(access_request_subject())}&body={quote(body)}"


def find_user_by_email(email: str) -> Optional[User]:
    normalized = normalize_email(email)
    if not normalized:
        return None
    with get_session() as session:
        stmt = select(User).where(User.email == normalized)
        return session.execute(stmt).scalars().first()


def _build_internal_username(email: str, session) -> str:
    base = normalize_email(email)
    candidate = base
    suffix = 1
    while session.execute(select(User).where(User.username == candidate)).scalars().first():
        candidate = f"{base}-{suffix}"
        suffix += 1
    return candidate


def get_user_by_id(user_id: str) -> Optional[User]:
    with get_session() as session:
        stmt = select(User).where(User.id == user_id)
        return session.execute(stmt).scalars().first()


def _creator_name_lookup(users: list[User]) -> dict[str, str]:
    creator_ids = {
        str(user.created_by_user_id)
        for user in users
        if user.created_by_user_id
    }
    if not creator_ids:
        return {}
    with get_session() as session:
        creators = session.execute(select(User).where(User.id.in_(creator_ids))).scalars().all()
    return {
        str(creator.id): build_display_name(
            first_name=creator.first_name,
            last_name=creator.last_name,
            display_name=creator.display_name,
            email=creator.email,
            username=creator.username,
        )
        or str(creator.email or creator.username or creator.id)
        for creator in creators
    }


def _status_sort_order(user: User) -> int:
    return {
        "active": 0,
        "invited": 1,
        "expired": 2,
        "deactivated": 3,
    }.get(admin_status_code(user), 99)


def _role_sort_order(user: User) -> int:
    return {
        Role.ADMIN.value: 0,
        Role.USER.value: 1,
    }.get(normalize_role_value(user.role), 99)


def list_users(
    *,
    include_inactive: bool = False,
    search_query: str | None = None,
    sort_by: str = "created_desc",
) -> list[User]:
    normalized_query = (search_query or "").strip().lower()
    with get_session() as session:
        stmt = select(User)
        items = list(session.execute(stmt).scalars().all())
        if not include_inactive:
            items = [item for item in items if item.deleted_at is None]
        if normalized_query:
            items = [
                item
                for item in items
                if normalized_query in (item.email or "").lower()
                or normalized_query in (item.first_name or "").lower()
                or normalized_query in (item.last_name or "").lower()
                or normalized_query in (item.display_name or "").lower()
            ]
        creator_lookup = _creator_name_lookup(items)
        if sort_by == "name":
            items.sort(
                key=lambda item: (
                    (item.last_name or "").lower(),
                    (item.first_name or "").lower(),
                    (item.email or "").lower(),
                )
            )
        elif sort_by == "role":
            items.sort(
                key=lambda item: (
                    _role_sort_order(item),
                    (item.last_name or "").lower(),
                    (item.first_name or "").lower(),
                )
            )
        elif sort_by == "status":
            items.sort(
                key=lambda item: (
                    _status_sort_order(item),
                    (item.last_name or "").lower(),
                    (item.first_name or "").lower(),
                )
            )
        elif sort_by == "expires":
            items.sort(
                key=lambda item: (
                    item.access_expires_at is None,
                    _ensure_utc(item.access_expires_at) or datetime.max.replace(tzinfo=timezone.utc),
                    (item.last_name or "").lower(),
                )
            )
        elif sort_by == "created_by":
            items.sort(
                key=lambda item: (
                    (creator_lookup.get(str(item.created_by_user_id), "") or "").lower(),
                    (item.last_name or "").lower(),
                    (item.first_name or "").lower(),
                )
            )
        else:
            items.sort(
                key=lambda item: (
                    _ensure_utc(item.created_at) or datetime.min.replace(tzinfo=timezone.utc),
                    (item.email or "").lower(),
                    (item.username or "").lower(),
                ),
                reverse=True,
            )
        return items


def count_active_admins() -> int:
    with get_session() as session:
        users = session.execute(select(User)).scalars().all()
    return sum(
        1
        for user in users
        if normalize_role_value(user.role) == Role.ADMIN.value
        and user.deleted_at is None
        and bool(user.is_active)
        and not (user.access_expires_at and _ensure_utc(user.access_expires_at) < datetime.now(timezone.utc))
    )


def _protect_last_admin(
    *,
    user: User,
    requested_role: str | None = None,
    requested_is_active: bool | None = None,
    requested_access_expires_at: Any = _UNSET,
) -> None:
    current_role = normalize_role_value(user.role)
    next_role = current_role if requested_role is None else normalize_role(requested_role)
    next_is_active = bool(user.is_active) if requested_is_active is None else bool(requested_is_active)
    next_access_expires_at = (
        user.access_expires_at
        if requested_access_expires_at is _UNSET
        else requested_access_expires_at
    )

    removes_admin_access = (
        current_role == Role.ADMIN.value
        and (
            next_role != Role.ADMIN.value
            or not next_is_active
            or (
                next_access_expires_at is not None
                and _ensure_utc(next_access_expires_at) < datetime.now(timezone.utc)
            )
        )
    )

    if removes_admin_access and count_active_admins() <= 1:
        raise ValueError("last_admin_required")


def create_user(
    *,
    email: str,
    first_name: str,
    last_name: str,
    role: str = "user",
    display_name: str | None = None,
    is_active: bool = True,
    access_expires_at: datetime | None = None,
    created_by_user_id: str | None = None,
) -> User:
    normalized_email = normalize_email(email)
    if not normalized_email:
        raise ValueError("email_required")

    normalized_first_name = (first_name or "").strip()
    normalized_last_name = (last_name or "").strip()
    if not normalized_first_name:
        raise ValueError("first_name_required")
    if not normalized_last_name:
        raise ValueError("last_name_required")

    normalized_role = normalize_role(role)
    if normalized_role == Role.ADMIN.value:
        access_expires_at = None

    now = datetime.now(timezone.utc)
    with get_session() as session:
        existing = session.execute(select(User).where(User.email == normalized_email)).scalars().first()
        if existing:
            raise ValueError("email_exists")

        user = User(
            id=str(uuid.uuid4()),
            username=_build_internal_username(normalized_email, session),
            email=normalized_email,
            password_hash=hash_password(secrets.token_urlsafe(32)),
            role=normalized_role,
            is_active=bool(is_active),
            must_reset_password=True,
            created_at=now,
            updated_at=now,
            access_expires_at=access_expires_at,
            first_name=normalized_first_name,
            last_name=normalized_last_name,
            display_name=build_display_name(
                first_name=normalized_first_name,
                last_name=normalized_last_name,
                display_name=display_name,
                email=normalized_email,
            ),
            created_by_user_id=created_by_user_id,
        )
        session.add(user)
        session.flush()
        return user


def update_user_admin(
    user_id: str,
    *,
    first_name: str | None = None,
    last_name: str | None = None,
    email: str | None = None,
    role: str | None = None,
    is_active: bool | None = None,
    access_expires_at: Any = _UNSET,
) -> User:
    with get_session() as session:
        stmt = select(User).where(User.id == user_id)
        user = session.execute(stmt).scalars().first()
        if not user:
            raise KeyError("user_not_found")

        _protect_last_admin(
            user=user,
            requested_role=role,
            requested_is_active=is_active,
            requested_access_expires_at=access_expires_at,
        )

        if first_name is not None:
            normalized_first_name = first_name.strip()
            if not normalized_first_name:
                raise ValueError("first_name_required")
            user.first_name = normalized_first_name

        if last_name is not None:
            normalized_last_name = last_name.strip()
            if not normalized_last_name:
                raise ValueError("last_name_required")
            user.last_name = normalized_last_name

        if email is not None:
            normalized_email = normalize_email(email)
            if not normalized_email:
                raise ValueError("email_required")
            existing = session.execute(select(User).where(User.email == normalized_email, User.id != user_id)).scalars().first()
            if existing:
                raise ValueError("email_exists")
            user.email = normalized_email

        if role is not None:
            user.role = normalize_role(role)

        if is_active is not None:
            user.is_active = bool(is_active)

        if access_expires_at is not _UNSET:
            user.access_expires_at = access_expires_at

        if normalize_role_value(user.role) == Role.ADMIN.value:
            user.access_expires_at = None

        user.display_name = build_display_name(
            first_name=user.first_name,
            last_name=user.last_name,
            display_name=user.display_name,
            email=user.email,
            username=user.username,
        )

        user.updated_at = datetime.now(timezone.utc)
        session.flush()
        return user


def mark_user_for_password_reset(user_id: str) -> User:
    with get_session() as session:
        stmt = select(User).where(User.id == user_id)
        user = session.execute(stmt).scalars().first()
        if not user:
            raise KeyError("user_not_found")
        user.must_reset_password = True
        user.updated_at = datetime.now(timezone.utc)
        session.flush()
        return user


def admin_status_code(user: User) -> str:
    if user.deleted_at is not None:
        return "deactivated"
    if not user.is_active:
        return "deactivated"
    if user.access_expires_at and _ensure_utc(user.access_expires_at) < datetime.now(timezone.utc):
        return "expired"
    if user.must_reset_password:
        return "invited"
    return "active"


def serialize_user_for_admin(
    user: User,
    *,
    creator_lookup: dict[str, str] | None = None,
) -> dict[str, Any]:
    creator_id = str(user.created_by_user_id) if user.created_by_user_id else ""
    return {
        "id": str(user.id),
        "username": user.username,
        "email": user.email,
        "display_name": build_display_name(
            first_name=user.first_name,
            last_name=user.last_name,
            display_name=user.display_name,
            email=user.email,
            username=user.username,
        ),
        "first_name": user.first_name or "",
        "last_name": user.last_name or "",
        "role": normalize_role_value(user.role),
        "is_active": bool(user.is_active),
        "must_reset_password": bool(user.must_reset_password),
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "updated_at": user.updated_at.isoformat() if user.updated_at else None,
        "access_expires_at": user.access_expires_at.isoformat() if user.access_expires_at else None,
        "access_expires_on": _ensure_utc(user.access_expires_at).date().isoformat() if user.access_expires_at else "",
        "created_by_user_id": creator_id,
        "created_by_name": (creator_lookup or {}).get(creator_id, ""),
        "created_by_is_system": not bool(creator_id),
        "status_code": admin_status_code(user),
    }


def serialize_users_for_admin(users: list[User]) -> list[dict[str, Any]]:
    creator_lookup = _creator_name_lookup(users)
    return [serialize_user_for_admin(user, creator_lookup=creator_lookup) for user in users]


def update_user_password(user_id: str, new_hashed: str) -> None:
    with get_session() as session:
        stmt = select(User).where(User.id == user_id)
        user = session.execute(stmt).scalars().first()
        if not user:
            raise KeyError("user_not_found")
        user.password_hash = new_hashed
        user.must_reset_password = False
        user.updated_at = datetime.now(timezone.utc)


def update_user_profile(
    user_id: str,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    email: Optional[str] = None,
) -> None:
    with get_session() as session:
        stmt = select(User).where(User.id == user_id)
        user = session.execute(stmt).scalars().first()
        if not user:
            raise KeyError("user_not_found")
        if first_name is not None:
            normalized_first_name = first_name.strip()
            if not normalized_first_name:
                raise ValueError("first_name_required")
            user.first_name = normalized_first_name
        if last_name is not None:
            normalized_last_name = last_name.strip()
            if not normalized_last_name:
                raise ValueError("last_name_required")
            user.last_name = normalized_last_name
        if email is not None:
            normalized_email = normalize_email(email)
            if not normalized_email:
                raise ValueError("email_required")
            existing = session.execute(select(User).where(User.email == normalized_email, User.id != user_id)).scalars().first()
            if existing:
                raise ValueError("email_exists")
            user.email = normalized_email
        user.display_name = build_display_name(
            first_name=user.first_name,
            last_name=user.last_name,
            display_name=user.display_name,
            email=user.email,
            username=user.username,
        )
        user.updated_at = datetime.now(timezone.utc)


def mark_user_deleted(user_id: str) -> None:
    with get_session() as session:
        stmt = select(User).where(User.id == user_id)
        user = session.execute(stmt).scalars().first()
        if not user:
            raise KeyError("user_not_found")
        _protect_last_admin(user=user, requested_is_active=False)
        user.deletion_requested_at = datetime.now(timezone.utc)
        user.deleted_at = datetime.now(timezone.utc)
        user.is_active = False


def create_reset_token_for_user(user: User) -> Tuple[str, ResetToken]:
    """Create a reset token for a user.

    Expiration is configurable via the Flask config key
    'AUTH_RESET_TOKEN_EXP_DAYS' (default: 14 days).
    Returns the raw token string and the created ResetToken row.
    """
    raw = secrets.token_urlsafe(48)
    token_hash = _hash_refresh_token(raw)
    rid = str(uuid.uuid4())
    days = int(current_app.config.get("AUTH_RESET_TOKEN_EXP_DAYS", 14))
    expires_at = datetime.now(timezone.utc) + timedelta(days=days)
    rt = ResetToken(
        id=rid,
        user_id=str(user.id),
        token_hash=token_hash,
        created_at=datetime.now(timezone.utc),
        expires_at=expires_at,
    )
    with get_session() as session:
        session.query(ResetToken).filter(
            ResetToken.user_id == str(user.id),
            ResetToken.used_at.is_(None),
        ).update({ResetToken.used_at: datetime.now(timezone.utc)})
        session.add(rt)
    return raw, rt


def inspect_reset_token(raw: str) -> Tuple[Optional[ResetToken], str]:
    """Verify reset token without consuming it. Returns (row, status)."""
    h = _hash_refresh_token(raw)
    with get_session() as session:
        stmt = select(ResetToken).where(ResetToken.token_hash == h)
        r = session.execute(stmt).scalars().first()
        if not r:
            return None, "invalid"
        if r.used_at is not None:
            return None, "used"
        if _ensure_utc(r.expires_at) < datetime.now(timezone.utc):
            return None, "expired"
        return r, "ok"


def verify_and_use_reset_token(raw: str) -> Tuple[Optional[ResetToken], str]:
    """Verify reset token and mark used if valid. Returns (row, status)."""
    h = _hash_refresh_token(raw)
    with get_session() as session:
        stmt = select(ResetToken).where(ResetToken.token_hash == h)
        r = session.execute(stmt).scalars().first()
        if not r:
            return None, "invalid"
        if r.used_at is not None:
            return None, "used"
        if _ensure_utc(r.expires_at) < datetime.now(timezone.utc):
            return None, "expired"
        r.used_at = datetime.now(timezone.utc)
        return r, "ok"


# Helper to mark login success/failure
def on_successful_login(user: User) -> None:
    with get_session() as session:
        stmt = select(User).where(User.id == user.id)
        dbu = session.execute(stmt).scalars().first()
        if dbu:
            dbu.login_failed_count = 0
            dbu.locked_until = None
            dbu.last_login_at = datetime.now(timezone.utc)
            dbu.updated_at = datetime.now(timezone.utc)


def on_failed_login(user: Optional[User]) -> None:
    if user is None:
        return
    with get_session() as session:
        stmt = select(User).where(User.id == user.id)
        dbu = session.execute(stmt).scalars().first()
        if dbu:
            dbu.login_failed_count = (dbu.login_failed_count or 0) + 1
            # Lockout policy: 5 failed attempts -> lock for 10 minutes
            if dbu.login_failed_count >= 5:
                dbu.locked_until = datetime.now(timezone.utc) + timedelta(minutes=10)
            dbu.updated_at = datetime.now(timezone.utc)
