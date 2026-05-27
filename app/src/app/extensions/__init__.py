"""Register Flask extensions for PROMAT."""

from __future__ import annotations

from flask import Flask, jsonify, request
from flask_caching import Cache
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from ..i18n import PREFERRED_UI_LANGUAGE_COOKIE_NAME, resolve_request_ui_language, translate

jwt = JWTManager()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["1000 per day", "200 per hour"],
    strategy="fixed-window",
)
cache = Cache(config={"CACHE_TYPE": "SimpleCache", "CACHE_DEFAULT_TIMEOUT": 300})


def _resolve_auth_ui_language() -> str:
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


def register_extensions(app: Flask) -> None:
    """Attach Flask extensions to the app."""
    jwt.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)
    if app.debug:
        limiter.enabled = False
    register_jwt_handlers()


def register_jwt_handlers() -> None:
    """Register JWT error handlers with HTML and JSON behavior."""

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        if request.path.startswith(("/static/", "/favicon", "/robots.txt", "/health", "/ready")):
            return jsonify({"authenticated": False}), 200

        token_type = jwt_payload.get("type", "access")
        error_code = "access_expired" if token_type == "access" else "refresh_expired"
        if request.path.startswith("/api/") or request.accept_mimetypes.best == "application/json":
            return jsonify({"error": "token_expired", "code": error_code}), 401

        from flask import flash, redirect, url_for
        from ..routes.auth import save_return_url

        save_return_url()
        try:
            flash(
                translate(_resolve_auth_ui_language(), "auth.flash.session_expired"),
                "info",
            )
        except RuntimeError:
            pass
        return redirect(url_for("public.login"), 303)

    @jwt.invalid_token_loader
    def invalid_token_callback(error_string):
        if request.path.startswith("/api/") or request.accept_mimetypes.best == "application/json":
            return jsonify({"error": "invalid_token", "message": error_string}), 401

        from flask import flash, redirect, url_for
        from ..routes.auth import save_return_url

        save_return_url()
        try:
            flash(
                translate(_resolve_auth_ui_language(), "auth.flash.invalid_session"),
                "info",
            )
        except RuntimeError:
            pass
        return redirect(url_for("public.login"), 303)

    @jwt.unauthorized_loader
    def unauthorized_callback(error_string):
        if request.path.startswith("/api/") or request.accept_mimetypes.best == "application/json":
            return jsonify({"error": "unauthorized", "message": error_string}), 401

        from flask import flash, redirect, url_for
        from ..routes.auth import save_return_url

        save_return_url()
        try:
            flash(
                translate(_resolve_auth_ui_language(), "auth.flash.login_required"),
                "info",
            )
        except RuntimeError:
            pass
        return redirect(url_for("public.login"), 303)
