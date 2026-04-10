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


def _normalize_value(value: str | None) -> str:
    return (value or "").strip()


def _default_database_url(env_name: str) -> str:
    if env_name in {"development", "dev", "testing", "test"}:
        return DEFAULT_DEV_DATABASE_URL
    return ""


class BaseConfig:
    PROJECT_ROOT = Path(__file__).resolve().parents[3]
    APP_ENV = _normalize_value(os.getenv("APP_ENV") or os.getenv("FLASK_ENV") or "production").lower()

    SECRET_KEY = _normalize_value(os.getenv("FLASK_SECRET_KEY")) or DEFAULT_SECRET_SENTINEL
    JWT_SECRET_KEY = _normalize_value(os.getenv("JWT_SECRET_KEY") or os.getenv("JWT_SECRET") or SECRET_KEY)

    FLASK_ENV = APP_ENV
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = _normalize_value(os.getenv("FLASK_SESSION_SECURE") or "true").lower() == "true"
    SESSION_COOKIE_SAMESITE = _normalize_value(os.getenv("FLASK_SESSION_SAMESITE") or "lax")

    JWT_TOKEN_LOCATION = ["headers", "cookies"]
    JWT_COOKIE_SECURE = SESSION_COOKIE_SECURE
    JWT_COOKIE_CSRF_PROTECT = True
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
    RESEARCH_SET_DRAFT_TTL_DAYS = int(_normalize_value(os.getenv("RESEARCH_SET_DRAFT_TTL_DAYS") or "14"))

    APP_REPOSITORY_URL = _normalize_value(os.getenv("APP_REPOSITORY_URL") or "")
    APP_VERSION = _normalize_value(os.getenv("APP_VERSION") or "")
    APP_RELEASE_TAG = _normalize_value(os.getenv("APP_RELEASE_TAG") or APP_VERSION)
    APP_RELEASE_URL = _normalize_value(os.getenv("APP_RELEASE_URL") or "")

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
    resolved_env = _normalize_value(env_name or os.getenv("FLASK_ENV") or os.getenv("APP_ENV") or "production").lower()
    config_class = CONFIG_MAP.get(resolved_env, ProductionConfig)
    app.config.from_object(config_class)
    app.config["FLASK_ENV"] = resolved_env

    if not app.config.get("AUTH_DATABASE_URL"):
        raise RuntimeError("AUTH_DATABASE_URL is required for PROMAT.")
    if app.config.get("SECRET_KEY") == DEFAULT_SECRET_SENTINEL and resolved_env not in {"development", "dev", "testing", "test"}:
        raise RuntimeError("FLASK_SECRET_KEY must be configured for non-development environments.")