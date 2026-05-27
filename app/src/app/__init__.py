"""Application factory for the PROMAT web application."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from importlib import metadata
from logging.handlers import RotatingFileHandler
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from flask import Flask, jsonify, redirect, render_template, request, url_for
from werkzeug.middleware.proxy_fix import ProxyFix

from .branding import BRANDING, format_page_title
from .analytics import register_analytics
from .i18n import PREFERRED_UI_LANGUAGE_COOKIE_NAME, normalize_supported_ui_language, resolve_request_ui_language, resolve_ui_language, translate
from .extensions import register_extensions
from .routes import register_blueprints
from .runtime_paths import get_logs_dir
from .teaching_content import resolve_teaching_switch_path
from .config import load_config


def _resolve_request_ui_language() -> str:
    """Resolve UI language for routes that do not carry a ui_lang path segment."""
    return resolve_request_ui_language(
        path_ui_lang=(request.view_args or {}).get("ui_lang"),
        explicit_ui_lang=request.values.get("lang") or request.values.get("ui_lang"),
        stored_ui_lang=request.cookies.get(PREFERRED_UI_LANGUAGE_COOKIE_NAME),
        next_candidates=(
            request.values.get("next"),
            request.args.get("next"),
            request.referrer,
            request.path,
        ),
        accept_language=request.headers.get("Accept-Language"),
    )


def _path_has_ui_lang_prefix(path: str) -> bool:
    if not path.startswith("/"):
        return False
    first_segment = path.lstrip("/").split("/", 1)[0]
    return first_segment in {"de", "en"}


def _swap_ui_lang_prefix(path: str, target_ui_lang: str) -> str:
    if not _path_has_ui_lang_prefix(path):
        return path
    stripped = path.lstrip("/")
    parts = stripped.split("/", 1)
    remainder = parts[1] if len(parts) > 1 else ""
    return f"/{target_ui_lang}" + (f"/{remainder}" if remainder else "")


def _rewrite_local_ui_lang_url(raw_url: str | None, target_ui_lang: str) -> str | None:
    if not raw_url:
        return raw_url

    parsed = urlsplit(str(raw_url))
    path = parsed.path or ""
    if not path.startswith("/"):
        return raw_url

    query_items = [
        (key, value)
        for key, value in parse_qsl(parsed.query, keep_blank_values=True)
        if key not in {"ui_lang", "lang"}
    ]
    rewritten_items: list[tuple[str, str]] = []
    for key, value in query_items:
        if key == "next":
            rewritten_items.append((key, _rewrite_local_ui_lang_url(value, target_ui_lang) or value))
        else:
            rewritten_items.append((key, value))

    rewritten_path = _swap_ui_lang_prefix(path, target_ui_lang) if _path_has_ui_lang_prefix(path) else path

    return urlunsplit(("", "", rewritten_path, urlencode(rewritten_items, doseq=True), parsed.fragment))


def _build_ui_lang_switch_url(target_ui_lang: str) -> str:
    target_ui_lang = resolve_ui_language(target_ui_lang)
    path = request.path or "/"
    query_items = [
        (key, value)
        for key, value in request.args.items(multi=True)
        if key not in {"ui_lang", "lang"}
    ]
    rewritten_items: list[tuple[str, str]] = []
    for key, value in query_items:
        if key == "next":
            rewritten_items.append((key, _rewrite_local_ui_lang_url(value, target_ui_lang) or value))
        else:
            rewritten_items.append((key, value))

    teaching_override = resolve_teaching_switch_path(path, target_ui_lang)
    localized_path = teaching_override or (_swap_ui_lang_prefix(path, target_ui_lang) if _path_has_ui_lang_prefix(path) else path)
    rewritten_items.append(("lang", target_ui_lang))

    query = urlencode(rewritten_items, doseq=True)
    return f"{localized_path}?{query}" if query else localized_path


def _verify_critical_dependencies() -> list[str]:
    """Verify critical dependencies are available."""
    errors = []

    try:
        import psycopg2

        logging.getLogger(__name__).debug(f"psycopg2 version: {psycopg2.__version__}")
    except ImportError as e:
        errors.append(f"psycopg2 not available: {e}. PostgreSQL support disabled.")

    try:
        argon2_version = metadata.version("argon2-cffi")
        logging.getLogger(__name__).debug(f"argon2-cffi version: {argon2_version}")
    except ImportError as e:
        errors.append(
            f"argon2-cffi not available: {e}. Secure password hashing may be degraded."
        )
    except metadata.PackageNotFoundError as e:
        errors.append(
            f"argon2-cffi package metadata unavailable: {e}. Secure password hashing may be degraded."
        )

    try:
        from passlib.hash import argon2 as passlib_argon2

        _ = passlib_argon2.hash("test")
        logging.getLogger(__name__).debug("passlib argon2 backend: OK")
    except Exception as e:
        errors.append(
            f"passlib argon2 backend unavailable: {e}. Will fall back to bcrypt."
        )

    return errors


def _verify_auth_db_connection(app: Flask) -> None:
    """Verify auth database connection and schema."""
    from sqlalchemy import inspect, text
    from .extensions.sqlalchemy_ext import get_engine

    engine = get_engine()
    if engine is None:
        raise RuntimeError("Auth engine not initialized")

    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))

    inspector = inspect(engine)
    if not inspector.has_table("users"):
        raise RuntimeError(
            "Auth DB schema is not initialized: required table 'users' is missing. "
            "Run scripts/dev-setup.ps1 or apply the auth migration before starting the app."
        )

    app.logger.info(f"Auth DB connection verified: {engine.url}")


def create_app(env_name: str | None = None) -> Flask:
    """Create and configure the Flask application instance."""

    project_root = Path(__file__).resolve().parents[2]
    template_dir = project_root / "templates"
    static_dir = project_root / "static"

    app = Flask(
        __name__,
        instance_relative_config=True,
        template_folder=str(template_dir),
        static_folder=str(static_dir),
    )
    load_config(app, env_name)
    setup_logging(app)

    dep_errors = _verify_critical_dependencies()
    if dep_errors:
        for err in dep_errors:
            app.logger.warning("Dependency warning: %s", err)

    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

    from .extensions.sqlalchemy_ext import init_engine as init_auth_db

    auth_db_url = app.config.get("AUTH_DATABASE_URL", "")
    auth_db_driver = auth_db_url.split(":", 1)[0] if auth_db_url else "<missing>"

    try:
        app.logger.info(
            "Initializing auth DB engine for FLASK_ENV=%s using driver=%s",
            app.config.get("FLASK_ENV"),
            auth_db_driver,
        )
        init_auth_db(app)
        _verify_auth_db_connection(app)
    except Exception as e:
        app.logger.error(
            "Auth DB initialization failed for FLASK_ENV=%s with driver=%s: %s",
            app.config.get("FLASK_ENV"),
            auth_db_driver,
            e,
        )
        app.logger.error(
            "Refusing to continue with auth half-initialized. Check AUTH_DATABASE_URL, DB readiness, and installed PostgreSQL driver."
        )
        raise RuntimeError(f"Auth DB initialization failed: {e}") from e

    import time

    app.config["APP_BUILD_ID"] = time.strftime("%Y%m%d%H%M%S")
    app.config["_STARTUP_DEP_WARNINGS"] = dep_errors

    register_extensions(app)
    register_blueprints(app)
    register_context_processors(app)
    register_auth_context(app)
    register_analytics(app)
    register_security_headers(app)
    register_maintenance_commands(app)
    register_error_handlers(app)

    return app


def register_maintenance_commands(app: Flask) -> None:
    """Register maintenance CLI commands."""
    from flask.cli import with_appcontext

    @app.cli.command("auth-anonymize")
    @with_appcontext
    def auth_anonymize_command():
        """Anonymize soft-deleted accounts older than configured window.

        Usage: flask auth-anonymize
        """
        from .auth import services

        days = int(app.config.get("AUTH_ACCOUNT_ANONYMIZE_AFTER_DAYS", 30))
        count = services.anonymize_soft_deleted_users_older_than(days)
        app.logger.info(f"Anonymized {count} users soft-deleted older than {days} days")

    @app.cli.command("research-sets-cleanup")
    @with_appcontext
    def research_sets_cleanup_command():
        """Delete expired draft research sets."""
        from .research_sets import delete_expired_drafts

        count = delete_expired_drafts()
        app.logger.info("Deleted %s expired draft research sets", count)


def register_context_processors(app: Flask) -> None:
    """Expose helpers to the template engine."""

    if app.extensions.get("promat_context_processors_registered"):
        return

    def static_asset(filename: str) -> str:
        static_root = Path(app.static_folder or "")
        target = static_root / filename
        if target.exists():
            return url_for("static", filename=filename, v=str(target.stat().st_mtime_ns))
        return url_for("static", filename=filename)

    @app.context_processor
    def inject_utilities():  # pragma: no cover - thin wrapper
        current_ui_lang = _resolve_request_ui_language()
        return {
            "now": lambda: datetime.now(timezone.utc),
            "app_version": app.config.get("APP_VERSION", ""),
            "app_release_tag": app.config.get("APP_RELEASE_TAG", ""),
            "app_release_url": app.config.get("APP_RELEASE_URL", ""),
            "format_page_title": format_page_title,
            "static_asset": static_asset,
            "current_ui_lang": current_ui_lang,
            "ui_lang_switch_urls": {
                "de": _build_ui_lang_switch_url("de"),
                "en": _build_ui_lang_switch_url("en"),
            },
            "t": lambda key, **kwargs: translate(current_ui_lang, key, **kwargs),
            **BRANDING,
        }

    @app.after_request
    def persist_explicit_ui_language(response):
        selected_ui_lang = normalize_supported_ui_language(request.values.get("lang") or request.values.get("ui_lang"))
        if selected_ui_lang is not None:
            response.set_cookie(
                PREFERRED_UI_LANGUAGE_COOKIE_NAME,
                selected_ui_lang,
                max_age=60 * 60 * 24 * 365,
                httponly=True,
                secure=bool(app.config.get("SESSION_COOKIE_SECURE", False)),
                samesite=app.config.get("SESSION_COOKIE_SAMESITE", "Lax"),
                path="/",
            )
        return response

    app.extensions["promat_context_processors_registered"] = True


def register_auth_context(app: Flask) -> None:
    """Register request and template auth context."""
    from flask import g
    from flask_jwt_extended import get_jwt, get_jwt_identity, verify_jwt_in_request
    from .auth import coerce_role

    @app.before_request
    def _set_auth_context():
        """Load auth state into g context for all requests."""
        PUBLIC_PREFIXES = (
            "/static/",
            "/favicon",
            "/robots.txt",
            "/health",
            "/ready",
        )

        path = request.path

        if any(path.startswith(p) for p in PUBLIC_PREFIXES):
            g.user = None
            g.user_id = None
            g.role = None
            g.must_reset_password = False
            return

        try:
            verify_jwt_in_request(optional=True, locations=["cookies"])
            identity = get_jwt_identity()
            token = get_jwt() or {}
            g.user_id = identity if isinstance(identity, str) and identity.strip() else None
            g.user = token.get("username") or identity
            role_value = token.get("role")
            try:
                g.role = coerce_role(role_value) if role_value else None
            except (ValueError, KeyError):
                g.role = None
            g.must_reset_password = bool(token.get("must_reset_password", False))
        except Exception:  # noqa: BLE001
            g.user = None
            g.user_id = None
            g.role = None
            g.must_reset_password = False

        allowed_prefixes = (
            "/static/",
            "/favicon",
            "/robots.txt",
            "/health",
            "/ready",
            "/auth/account/password",
            "/auth/password/reset",
            "/auth/password/forgot",
            "/auth/login",
            "/login",
            "/auth/logout_any",
        )

        if getattr(g, "user", None) and getattr(g, "must_reset_password", False):
            if not any(request.path.startswith(p) for p in allowed_prefixes):
                if request.headers.get("HX-Request") or request.is_json:
                    return jsonify({"error": "password_reset_required"}), 403
                return redirect(
                    url_for("auth.account_password_page") + "?mustReset=1", 303
                )

    @app.context_processor
    def _inject_auth_context():
        """Expose auth state to templates."""
        user = getattr(g, "user", None)
        must_reset = getattr(g, "must_reset_password", False)
        return {
            "is_authenticated": bool(user),
            "current_user": user,
            "must_reset_password": must_reset,
        }


def register_security_headers(app: Flask) -> None:
    """Add security headers to all responses."""

    @app.after_request
    def set_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        if not app.debug:
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )

        csp = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "img-src 'self' data: https: blob:; "
            "font-src 'self' https://fonts.gstatic.com; "
            "connect-src 'self'; "
            "frame-src 'self' https://www.youtube.com https://datawrapper.dwcdn.net; "
            "frame-ancestors 'none'; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "form-action 'self';"
        )
        response.headers["Content-Security-Policy"] = csp

        if request.path.startswith("/auth/"):
            response.headers["Cache-Control"] = "no-store, private"
            response.headers["Vary"] = "Cookie"

        return response


def _request_prefers_json_errors() -> bool:
    return (
        request.path.startswith("/api/")
        or request.accept_mimetypes.best == "application/json"
        or request.is_json
    )


def _json_error_response(message: str, status_code: int, *, error: str | None = None):
    payload = {"error": error or message, "message": message}
    return jsonify(payload), status_code


def register_error_handlers(app: Flask) -> None:
    """Register custom error handlers for common HTTP errors."""

    @app.errorhandler(400)
    def bad_request(error):
        app.logger.warning("Bad request: %s", error)
        if _request_prefers_json_errors():
            return _json_error_response(str(error), 400, error="Bad request")
        return render_template("errors/400.html", error=error), 400

    @app.errorhandler(401)
    def unauthorized(error):
        app.logger.warning("Unauthorized request: %s", request.path)
        if _request_prefers_json_errors():
            return _json_error_response("Unauthorized", 401)
        return render_template("errors/401.html", error=error), 401

    @app.errorhandler(403)
    def forbidden(error):
        app.logger.warning("Forbidden request: %s", request.path)
        if _request_prefers_json_errors():
            return _json_error_response("Forbidden", 403)
        return render_template("errors/403.html", error=error), 403

    @app.errorhandler(404)
    def not_found(error):
        if _request_prefers_json_errors():
            return _json_error_response("Not found", 404)
        return render_template("errors/404.html", error=error), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        app.logger.exception("Unhandled application error: %s", error)
        if _request_prefers_json_errors():
            return _json_error_response("Internal server error", 500)
        return render_template("errors/500.html", error=error), 500


def setup_logging(app: Flask) -> None:
    """Configure file logging for non-debug environments."""
    if app.debug or app.testing or app.extensions.get("promat_logging_configured"):
        return

    logs_dir = get_logs_dir()
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_path = logs_dir / "promat-web.log"
    for existing_handler in app.logger.handlers:
        if isinstance(existing_handler, RotatingFileHandler) and Path(
            getattr(existing_handler, "baseFilename", "")
        ) == log_path.resolve():
            app.extensions["promat_logging_configured"] = True
            return

    handler = RotatingFileHandler(log_path, maxBytes=1_000_000, backupCount=5)
    handler.set_name("promat.file")
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
    )
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)
    app.logger.propagate = False
    app.extensions["promat_logging_configured"] = True
    app.logger.info("PROMAT application startup")
