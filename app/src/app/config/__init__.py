"""Configuration for the PROMAT web application."""

from __future__ import annotations

import os
from pathlib import Path
import re
from urllib.parse import urlsplit

from ..runtime_paths import (
    resolve_environment_name,
    get_config_root,
    get_data_root,
    get_logs_dir,
    get_public_root,
    get_runtime_root,
    get_sessions_root,
)


DEFAULT_SECRET_SENTINEL = "__CHANGE_ME__"
# Local development serves on this origin (scripts/dev-start.ps1); used when no public base URL is configured.
DEFAULT_DEV_PUBLIC_BASE_URL = "http://127.0.0.1:8000"
# Template markers such as `__CHANGE_ME__` or `__SET_PUBLIC_BASE_URL__` in app/passwords.env.template. A real
# random secret or URL never has this shape, so this does not reject legitimate values.
_TEMPLATE_PLACEHOLDER_PATTERN = re.compile(r"^__[A-Z0-9_]+__$")
_DEV_LIKE_ENVS = frozenset({"development", "dev", "testing", "test"})
# Production secrets must be real random values: HS256 signing keys shorter than this are guessable, and the
# role claim in the signed token is trusted without a database lookup.
MIN_PRODUCTION_SECRET_LENGTH = 32
_MIN_PRODUCTION_SECRET_DISTINCT_CHARACTERS = 8
_WEAK_SECRET_VALUES = frozenset({"changeme", "change-me", "change_me", "secret", "password", "test-secret", "dev-secret"})
_MAIL_ADDRESS_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
DEFAULT_DEV_DATABASE_URL = "postgresql+psycopg2://promat_auth:promat_auth@127.0.0.1:54321/promat_auth"
GOATCOUNTER_ENDPOINT = "https://pronunciation-matters.goatcounter.com/count"


def _normalize_value(value: str | None) -> str:
    return (value or "").strip()


def _default_database_url(env_name: str) -> str:
    if env_name in {"development", "dev", "testing", "test"}:
        return DEFAULT_DEV_DATABASE_URL
    return ""


def _default_rate_limit_storage_uri(env_name: str) -> str:
    if env_name in {"development", "dev", "testing", "test"}:
        return "memory://"
    return ""


def _default_access_request_mail_enabled(env_name: str) -> bool:
    return env_name not in {"development", "dev", "testing", "test"}


def _default_mail_backend(env_name: str) -> str:
    if env_name in {"development", "dev", "testing", "test"}:
        return "disabled"
    return "smtp"


def is_unset_or_placeholder(value: str | None) -> bool:
    """True for empty values and for template markers such as ``__CHANGE_ME__`` (never logs the value)."""
    normalized = _normalize_value(value)
    return not normalized or bool(_TEMPLATE_PLACEHOLDER_PATTERN.match(normalized))


def normalize_public_base_url(raw_value: str | None) -> str:
    """Return the canonical external origin (no trailing slash) or raise ``ValueError`` if it is unusable."""
    value = _normalize_value(raw_value)
    if is_unset_or_placeholder(value):
        raise ValueError("PROMAT_PUBLIC_BASE_URL is not set to a real URL.")
    parts = urlsplit(value)
    if parts.scheme not in {"http", "https"} or not parts.hostname:
        raise ValueError("PROMAT_PUBLIC_BASE_URL must be an absolute http(s) URL such as https://example.org.")
    if parts.username or parts.password or parts.query or parts.fragment:
        raise ValueError("PROMAT_PUBLIC_BASE_URL must not contain credentials, a query string, or a fragment.")
    return value.rstrip("/")


def _validate_production_secret(name: str, value: str | None) -> None:
    """Reject unusable production secrets without ever including the value in the message."""
    normalized = _normalize_value(value)
    if is_unset_or_placeholder(normalized):
        raise RuntimeError(
            f"{name} must be configured for non-development environments "
            f"(it is empty or still a template placeholder such as {DEFAULT_SECRET_SENTINEL})."
        )
    if normalized.lower() in _WEAK_SECRET_VALUES:
        raise RuntimeError(f"{name} is a well-known placeholder value; configure a random secret.")
    if len(normalized) < MIN_PRODUCTION_SECRET_LENGTH:
        raise RuntimeError(f"{name} must be at least {MIN_PRODUCTION_SECRET_LENGTH} characters for non-development environments.")
    if len(set(normalized)) < _MIN_PRODUCTION_SECRET_DISTINCT_CHARACTERS:
        raise RuntimeError(f"{name} is too repetitive; configure a random secret.")


def _validate_access_request_mail(app_config) -> None:
    """With access-request mail enabled, an unusable sender, recipient or SMTP host is a startup error, not a runtime 500."""
    if not app_config.get("AUTH_ACCESS_REQUEST_MAIL_ENABLED"):
        return
    recipient = _normalize_value(app_config.get("AUTH_ACCESS_REQUEST_EMAIL"))
    sender = _normalize_value(app_config.get("AUTH_ACCESS_REQUEST_FROM_EMAIL") or app_config.get("AUTH_MAIL_FROM_EMAIL"))
    if is_unset_or_placeholder(recipient) or not _MAIL_ADDRESS_PATTERN.match(recipient):
        raise RuntimeError("AUTH_ACCESS_REQUEST_EMAIL must be a real e-mail address when access-request mail is enabled.")
    if is_unset_or_placeholder(sender) or not _MAIL_ADDRESS_PATTERN.match(sender):
        raise RuntimeError("AUTH_ACCESS_REQUEST_FROM_EMAIL (or AUTH_MAIL_FROM_EMAIL) must be a real e-mail address when access-request mail is enabled.")
    if app_config.get("AUTH_MAIL_BACKEND") == "smtp" and is_unset_or_placeholder(app_config.get("AUTH_ACCESS_REQUEST_SMTP_HOST")):
        raise RuntimeError("AUTH_ACCESS_REQUEST_SMTP_HOST must be set to a real host when the smtp mail backend is used.")


def _is_production_env(env_name: str) -> bool:
    return env_name in {"production", "prod"}


def _parse_bool_env(name: str, default: bool) -> bool:
    raw_value = _normalize_value(os.getenv(name))
    if not raw_value:
        return default
    return raw_value.lower() in {"1", "true", "yes", "on"}


def _resolve_rate_limit_storage_uri(env_name: str) -> str:
    configured = _normalize_value(
        os.getenv("RATE_LIMIT_STORAGE_URI") or os.getenv("RATELIMIT_STORAGE_URI")
    )
    if configured:
        return configured
    return _default_rate_limit_storage_uri(env_name)


class BaseConfig:
    PROJECT_ROOT = Path(__file__).resolve().parents[3]
    APP_ENV = resolve_environment_name()
    PROMAT_ENV = APP_ENV
    PROMAT_PUBLIC_BASE_URL = _normalize_value(os.getenv("PROMAT_PUBLIC_BASE_URL") or "")

    SECRET_KEY = _normalize_value(os.getenv("FLASK_SECRET_KEY")) or DEFAULT_SECRET_SENTINEL
    JWT_SECRET_KEY = _normalize_value(os.getenv("JWT_SECRET_KEY") or os.getenv("JWT_SECRET") or SECRET_KEY)

    FLASK_ENV = APP_ENV
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = _normalize_value(os.getenv("FLASK_SESSION_SECURE") or "true").lower() == "true"
    SESSION_COOKIE_SAMESITE = _normalize_value(os.getenv("FLASK_SESSION_SAMESITE") or "lax")

    JWT_TOKEN_LOCATION = ["headers", "cookies"]
    JWT_COOKIE_SECURE = SESSION_COOKIE_SECURE
    JWT_COOKIE_CSRF_PROTECT = True
    JWT_CSRF_CHECK_FORM = True
    JWT_COOKIE_SAMESITE = "Lax"
    JWT_ACCESS_COOKIE_PATH = "/"
    JWT_REFRESH_COOKIE_PATH = "/"
    ACCESS_TOKEN_EXP = int(_normalize_value(os.getenv("ACCESS_TOKEN_EXP") or "3600"))
    REFRESH_TOKEN_EXP = int(_normalize_value(os.getenv("REFRESH_TOKEN_EXP") or "604800"))

    AUTH_DATABASE_URL = _normalize_value(os.getenv("AUTH_DATABASE_URL")) or _default_database_url(APP_ENV)
    AUTH_HASH_ALGO = _normalize_value(os.getenv("AUTH_HASH_ALGO") or "argon2")
    AUTH_ARGON2_TIME_COST = int(_normalize_value(os.getenv("AUTH_ARGON2_TIME_COST") or "2"))
    AUTH_ARGON2_MEMORY_COST = int(_normalize_value(os.getenv("AUTH_ARGON2_MEMORY_COST") or "102400"))
    AUTH_ARGON2_PARALLELISM = int(_normalize_value(os.getenv("AUTH_ARGON2_PARALLELISM") or "4"))
    AUTH_ACCOUNT_ANONYMIZE_AFTER_DAYS = int(_normalize_value(os.getenv("AUTH_ACCOUNT_ANONYMIZE_AFTER_DAYS") or "30"))
    AUTH_RESET_TOKEN_EXP_DAYS = int(_normalize_value(os.getenv("AUTH_RESET_TOKEN_EXP_DAYS") or "14"))
    AUTH_ACCESS_REQUEST_EMAIL = _normalize_value(os.getenv("AUTH_ACCESS_REQUEST_EMAIL") or "")
    AUTH_ACCESS_REQUEST_SUBJECT = _normalize_value(
        os.getenv("AUTH_ACCESS_REQUEST_SUBJECT") or 'Zugangsanfrage "Pronunciation Matters"'
    )
    AUTH_ACCESS_REQUEST_MAIL_ENABLED = _parse_bool_env(
        "AUTH_ACCESS_REQUEST_MAIL_ENABLED",
        _default_access_request_mail_enabled(APP_ENV),
    )
    AUTH_MAIL_BACKEND = _normalize_value(os.getenv("AUTH_MAIL_BACKEND") or _default_mail_backend(APP_ENV)).lower()
    AUTH_MAIL_FROM_EMAIL = _normalize_value(
        os.getenv("AUTH_MAIL_FROM_EMAIL") or os.getenv("AUTH_ACCESS_REQUEST_FROM_EMAIL") or ""
    )
    AUTH_MAIL_FROM_NAME = _normalize_value(
        os.getenv("AUTH_MAIL_FROM_NAME") or "Pronunciation Matters Administrator"
    )
    AUTH_MAIL_DEFAULT_REPLY_TO = _normalize_value(
        os.getenv("AUTH_MAIL_DEFAULT_REPLY_TO") or os.getenv("AUTH_ACCESS_REQUEST_EMAIL") or ""
    )
    AUTH_MAIL_SENDMAIL_PATH = _normalize_value(os.getenv("AUTH_MAIL_SENDMAIL_PATH") or "/usr/sbin/sendmail")
    AUTH_MAIL_TIMEOUT_SECONDS = int(_normalize_value(os.getenv("AUTH_MAIL_TIMEOUT_SECONDS") or "10"))
    AUTH_ACCESS_REQUEST_FROM_EMAIL = _normalize_value(
        os.getenv("AUTH_ACCESS_REQUEST_FROM_EMAIL") or AUTH_MAIL_FROM_EMAIL
    )
    AUTH_ACCESS_REQUEST_REPLY_TO_ENABLED = _parse_bool_env(
        "AUTH_ACCESS_REQUEST_REPLY_TO_ENABLED",
        True,
    )
    AUTH_ACCESS_REQUEST_SMTP_HOST = _normalize_value(os.getenv("AUTH_ACCESS_REQUEST_SMTP_HOST") or "")
    AUTH_ACCESS_REQUEST_SMTP_PORT = int(_normalize_value(os.getenv("AUTH_ACCESS_REQUEST_SMTP_PORT") or "587"))
    AUTH_ACCESS_REQUEST_SMTP_USERNAME = _normalize_value(os.getenv("AUTH_ACCESS_REQUEST_SMTP_USERNAME") or "")
    AUTH_ACCESS_REQUEST_SMTP_PASSWORD = _normalize_value(os.getenv("AUTH_ACCESS_REQUEST_SMTP_PASSWORD") or "")
    AUTH_ACCESS_REQUEST_SMTP_USE_TLS = _parse_bool_env("AUTH_ACCESS_REQUEST_SMTP_USE_TLS", True)
    AUTH_ACCESS_REQUEST_SMTP_USE_SSL = _parse_bool_env("AUTH_ACCESS_REQUEST_SMTP_USE_SSL", False)
    AUTH_ACCESS_REQUEST_SMTP_TIMEOUT_SECONDS = int(
        _normalize_value(os.getenv("AUTH_ACCESS_REQUEST_SMTP_TIMEOUT_SECONDS") or "10")
    )
    AUTH_ACCESS_REQUEST_FORM_MAX_AGE_SECONDS = int(
        _normalize_value(os.getenv("AUTH_ACCESS_REQUEST_FORM_MAX_AGE_SECONDS") or "43200")
    )
    AUTH_ACCESS_REQUEST_MIN_SUBMIT_SECONDS = float(
        _normalize_value(os.getenv("AUTH_ACCESS_REQUEST_MIN_SUBMIT_SECONDS") or "0.5")
    )
    # How often a worker probes the rate-limit storage; while it is down the limiter is skipped (see extensions).
    RATELIMIT_HEALTH_POLL_SECONDS = float(_normalize_value(os.getenv("RATELIMIT_HEALTH_POLL_SECONDS") or "5"))
    # Largest accepted request body. Forms and the JSON set API stay far below this; anything bigger is rejected with
    # 413 before it is parsed or stored.
    MAX_CONTENT_LENGTH = int(_normalize_value(os.getenv("MAX_CONTENT_LENGTH") or str(1024 * 1024)))
    RESEARCH_SET_DRAFT_TTL_DAYS = int(_normalize_value(os.getenv("RESEARCH_SET_DRAFT_TTL_DAYS") or "14"))

    APP_REPOSITORY_URL = _normalize_value(os.getenv("APP_REPOSITORY_URL") or "https://github.com/FTacke/promat-webapp")
    APP_VERSION = _normalize_value(os.getenv("VITE_APP_VERSION") or os.getenv("APP_VERSION") or "dev")
    APP_RELEASE_TAG = _normalize_value(os.getenv("APP_RELEASE_TAG") or APP_VERSION or "dev")
    APP_RELEASE_URL = _normalize_value(
        os.getenv("APP_RELEASE_URL")
        or (f"{APP_REPOSITORY_URL}/releases/tag/{APP_RELEASE_TAG}" if APP_RELEASE_TAG != "dev" else f"{APP_REPOSITORY_URL}/releases/latest")
    )
    VITE_GOATCOUNTER_URL = _normalize_value(os.getenv("VITE_GOATCOUNTER_URL") or "")
    GOATCOUNTER_URL = VITE_GOATCOUNTER_URL if _is_production_env(APP_ENV) and VITE_GOATCOUNTER_URL == GOATCOUNTER_ENDPOINT else ""

    RUNTIME_ROOT = get_runtime_root()
    DATA_ROOT = get_data_root()
    SESSIONS_ROOT = get_sessions_root()
    PUBLIC_ROOT = get_public_root()
    CONFIG_ROOT = get_config_root()
    LOGS_DIR = get_logs_dir()

    DEBUG = False
    TESTING = False


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SESSION_COOKIE_SECURE = False
    JWT_COOKIE_SECURE = False
    JWT_COOKIE_CSRF_PROTECT = False
    TEMPLATES_AUTO_RELOAD = True
    SEND_FILE_MAX_AGE_DEFAULT = 0


class TestingConfig(DevelopmentConfig):
    TESTING = True


class ProductionConfig(BaseConfig):
    pass


CONFIG_MAP = {
    "development": DevelopmentConfig,
    "dev": DevelopmentConfig,
    "testing": TestingConfig,
    "test": TestingConfig,
    "production": ProductionConfig,
    "prod": ProductionConfig,
}


def load_config(app, env_name: str | None = None) -> None:
    """Load environment-specific config into the Flask app."""
    resolved_env = resolve_environment_name(env_name)
    config_class = CONFIG_MAP.get(resolved_env, ProductionConfig)
    app.config.from_object(config_class)
    app.config["FLASK_ENV"] = resolved_env

    rate_limit_storage_uri = _resolve_rate_limit_storage_uri(resolved_env)
    app.config["RATE_LIMIT_STORAGE_URI"] = rate_limit_storage_uri
    app.config["RATELIMIT_STORAGE_URI"] = rate_limit_storage_uri
    if rate_limit_storage_uri.lower().startswith(("redis://", "rediss://")):
        # Short timeouts: with a dead Redis every request must fail open quickly instead of waiting on a socket.
        app.config["RATELIMIT_STORAGE_OPTIONS"] = {"socket_connect_timeout": 1, "socket_timeout": 1}

    if not app.config.get("AUTH_DATABASE_URL"):
        raise RuntimeError("AUTH_DATABASE_URL is required for PROMAT.")
    if resolved_env not in _DEV_LIKE_ENVS:
        _validate_production_secret("FLASK_SECRET_KEY", app.config.get("SECRET_KEY"))
        # Roles are read from the signed token, so a weak or placeholder JWT secret would let anyone forge an admin token.
        _validate_production_secret("JWT_SECRET_KEY", app.config.get("JWT_SECRET_KEY"))
        if app.config.get("SECRET_KEY") == app.config.get("JWT_SECRET_KEY"):
            raise RuntimeError("JWT_SECRET_KEY must differ from FLASK_SECRET_KEY.")
    # Canonical external origin for links that leave the app (password reset / invitation mails). It is never
    # derived from request headers, which a client can forge. Production requires a real https origin; local
    # development and tests fall back to the dev origin when nothing is configured.
    configured_base_url = _normalize_value(app.config.get("PROMAT_PUBLIC_BASE_URL"))
    if configured_base_url or resolved_env not in _DEV_LIKE_ENVS:
        try:
            app.config["PROMAT_PUBLIC_BASE_URL"] = normalize_public_base_url(configured_base_url)
        except ValueError as exc:
            raise RuntimeError(str(exc)) from exc
        if resolved_env not in _DEV_LIKE_ENVS and not app.config["PROMAT_PUBLIC_BASE_URL"].startswith("https://"):
            raise RuntimeError("PROMAT_PUBLIC_BASE_URL must use https:// for non-development environments.")
    else:
        app.config["PROMAT_PUBLIC_BASE_URL"] = DEFAULT_DEV_PUBLIC_BASE_URL
    if resolved_env not in _DEV_LIKE_ENVS:
        if not rate_limit_storage_uri:
            raise RuntimeError("RATE_LIMIT_STORAGE_URI must be configured for non-development environments.")
        if rate_limit_storage_uri.lower() == "memory://":
            raise RuntimeError("RATE_LIMIT_STORAGE_URI must not use memory:// for non-development environments.")
    if app.config.get("AUTH_MAIL_BACKEND") not in {"disabled", "smtp", "sendmail"}:
        raise RuntimeError("AUTH_MAIL_BACKEND must be one of disabled, smtp, or sendmail.")
    if resolved_env not in _DEV_LIKE_ENVS:
        _validate_access_request_mail(app.config)
    if app.config.get("AUTH_ACCESS_REQUEST_SMTP_USE_TLS") and app.config.get("AUTH_ACCESS_REQUEST_SMTP_USE_SSL"):
        raise RuntimeError("AUTH_ACCESS_REQUEST_SMTP_USE_TLS and AUTH_ACCESS_REQUEST_SMTP_USE_SSL are mutually exclusive.")
