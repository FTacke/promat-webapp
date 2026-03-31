"""Register Flask extensions for PROMAT."""

from __future__ import annotations

from flask import Flask, jsonify, request
from flask_caching import Cache
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

jwt = JWTManager()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["1000 per day", "200 per hour"],
    storage_uri="memory://",
    strategy="fixed-window",
)
cache = Cache(config={"CACHE_TYPE": "SimpleCache", "CACHE_DEFAULT_TIMEOUT": 300})


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
        if request.path.startswith(("/static/", "/favicon", "/robots.txt", "/health")):
            return jsonify({"authenticated": False}), 200

        token_type = jwt_payload.get("type", "access")
        error_code = "access_expired" if token_type == "access" else "refresh_expired"
        if request.path.startswith("/api/") or request.accept_mimetypes.best == "application/json":
            return jsonify({"error": "token_expired", "code": error_code}), 401

        from flask import flash, redirect, url_for
        from ..routes.auth import save_return_url

        save_return_url()
        try:
            flash("Ihre Sitzung ist abgelaufen. Bitte melden Sie sich erneut an.", "info")
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
            flash("Ihre Anmeldung ist ungültig. Bitte melden Sie sich erneut an.", "info")
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
            flash("Bitte melden Sie sich an, um diesen Bereich zu nutzen.", "info")
        except RuntimeError:
            pass
        return redirect(url_for("public.login"), 303)