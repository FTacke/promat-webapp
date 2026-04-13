"""Authentication utilities and role definitions."""

from __future__ import annotations

from enum import StrEnum


LEGACY_ROLE_ALIASES = {
    "editor": "user",
}


class Role(StrEnum):
    ADMIN = "admin"
    USER = "user"


ROLE_ORDER = [Role.ADMIN, Role.USER]


def coerce_role(value: str | Role | None, *, default: Role = Role.USER) -> Role:
    if isinstance(value, Role):
        return value

    normalized = str(value or "").strip().lower()
    if not normalized:
        return default

    normalized = LEGACY_ROLE_ALIASES.get(normalized, normalized)
    return Role(normalized)


def normalize_role_value(value: str | Role | None, *, default: Role = Role.USER) -> str:
    return coerce_role(value, default=default).value
