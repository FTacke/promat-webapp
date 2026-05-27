"""Configuration for the PROMAT web application."""

from __future__ import annotations

import os
from pathlib import Path

from ..runtime_paths import (
    get_config_root,
    get_data_root,
    get_logs_dir,
    get_public_root,
    get_runtime_root,
    get_sessions_root,
)


DEFAULT_SECRET_SENTINEL = "__CHANGE_ME__"
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
    APP_ENV = _normalize_value(os.getenv("PROMAT_ENV") or os.getenv("APP_ENV") or os.getenv("FLASK_ENV") or "production").lower()
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
    resolved_env = _normalize_value(
        env_name or os.getenv("PROMAT_ENV") or os.getenv("FLASK_ENV") or os.getenv("APP_ENV") or "production"
    ).lower()
    config_class = CONFIG_MAP.get(resolved_env, ProductionConfig)
    app.config.from_object(config_class)
    app.config["FLASK_ENV"] = resolved_env

    rate_limit_storage_uri = _resolve_rate_limit_storage_uri(resolved_env)
    app.config["RATE_LIMIT_STORAGE_URI"] = rate_limit_storage_uri
    app.config["RATELIMIT_STORAGE_URI"] = rate_limit_storage_uri

    if not app.config.get("AUTH_DATABASE_URL"):
        raise RuntimeError("AUTH_DATABASE_URL is required for PROMAT.")
    if app.config.get("SECRET_KEY") == DEFAULT_SECRET_SENTINEL and resolved_env not in {"development", "dev", "testing", "test"}:
        raise RuntimeError("FLASK_SECRET_KEY must be configured for non-development environments.")
    if resolved_env not in {"development", "dev", "testing", "test"}:
        if not rate_limit_storage_uri:
            raise RuntimeError("RATE_LIMIT_STORAGE_URI must be configured for non-development environments.")
        if rate_limit_storage_uri.lower() == "memory://":
            raise RuntimeError("RATE_LIMIT_STORAGE_URI must not use memory:// for non-development environments.")
    if app.config.get("AUTH_ACCESS_REQUEST_SMTP_USE_TLS") and app.config.get("AUTH_ACCESS_REQUEST_SMTP_USE_SSL"):
        raise RuntimeError("AUTH_ACCESS_REQUEST_SMTP_USE_TLS and AUTH_ACCESS_REQUEST_SMTP_USE_SSL are mutually exclusive.")
    if app.config.get("AUTH_MAIL_BACKEND") not in {"disabled", "smtp", "sendmail"}:
        raise RuntimeError("AUTH_MAIL_BACKEND must be one of disabled, smtp, or sendmail.")
