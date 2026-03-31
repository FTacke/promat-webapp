"""Authentication routes for PROMAT."""

from __future__ import annotations

from urllib.parse import unquote, urlparse

from flask import Blueprint, Response, current_app, flash, jsonify, make_response, redirect, render_template, request, session, url_for
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required, set_access_cookies, unset_jwt_cookies, verify_jwt_in_request

from ..auth import services as auth_services
from ..extensions import limiter

blueprint = Blueprint("auth", __name__, url_prefix="/auth")
RETURN_URL_SESSION_KEY = "_return_url_after_login"


def save_return_url(url: str | None = None) -> None:
    """Remember a target URL for the next successful login."""
    current_url = url or request.url
    if current_url and not any(part in current_url for part in ["/auth/", "/static/", "/health"]):
        session[RETURN_URL_SESSION_KEY] = current_url


def _safe_next(raw: str | None) -> str | None:
    if not raw:
        return None
    parsed = urlparse(unquote(raw))
    if parsed.netloc and parsed.netloc != request.host:
        return None
    if parsed.path.startswith(("/auth/login", "/auth/logout", "/login")):
        return None
    safe = parsed.path or ""
    if parsed.query:
        safe += f"?{parsed.query}"
    return safe or None


@blueprint.get("/session")
def check_session() -> Response:
    try:
        verify_jwt_in_request(optional=True, locations=["cookies"])
        token = get_jwt() or {}
        identity = token.get("sub")
        username = token.get("username") or identity
        exp = token.get("exp")
        response = jsonify({"authenticated": bool(identity), "user": username, "exp": exp})
    except Exception:
        response = jsonify({"authenticated": False, "user": None, "exp": None})

    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, private"
    response.headers["Pragma"] = "no-cache"
    response.headers["Vary"] = "Cookie"
    return response, 200


@blueprint.get("/konto")
@jwt_required()
def account_page() -> Response:
    user = None
    identity = get_jwt_identity()
    if identity:
        user = auth_services.get_user_by_id(identity)
    return render_template("pages/account.html", user=user), 200


@blueprint.get("/password/forgot")
def password_forgot_page() -> Response:
    return render_template("auth/password_forgot.html"), 200


@blueprint.get("/password/reset")
def password_reset_page() -> Response:
    token = request.args.get("token") or ""
    return render_template("auth/password_reset.html", token=token), 200


@blueprint.get("/login", endpoint="login")
def login_form() -> Response:
    next_url = _safe_next(request.args.get("next") or request.referrer)
    target = url_for("public.login", next=next_url) if next_url else url_for("public.login")
    return redirect(target, 303)


@blueprint.post("/login", endpoint="login_post")
@limiter.limit("5 per minute")
def login_post() -> Response:
    identifier = (request.form.get("username") or "").strip().lower()
    password = request.form.get("password", "")
    next_raw = request.form.get("next") or request.args.get("next") or session.pop(RETURN_URL_SESSION_KEY, None)
    next_url = _safe_next(next_raw)

    if not identifier:
        flash("Bitte geben Sie einen Benutzernamen oder eine E-Mail-Adresse ein.", "error")
        return render_template("auth/login.html", next=next_url or ""), 400

    user = auth_services.find_user_by_username_or_email(identifier)
    if not user or not auth_services.verify_password(password, user.password_hash):
        flash("Anmeldung fehlgeschlagen. Bitte prüfen Sie Ihre Zugangsdaten.", "error")
        return render_template("auth/login.html", next=next_url or ""), 401

    status = auth_services.check_account_status(user)
    if not status.ok:
        flash("Dieses Konto ist derzeit nicht verfügbar.", "error")
        return render_template("auth/login.html", next=next_url or ""), 403

    access_token = auth_services.create_access_token_for_user(user)
    target = next_url or url_for("auth.account_page")
    response = make_response(redirect(target, 303))
    set_access_cookies(response, access_token)
    response.headers["Cache-Control"] = "no-store, private"
    return response


@blueprint.route("/logout_any", methods=["GET", "POST"])
def logout_any() -> Response:
    response = make_response(redirect(url_for("public.landing_page"), 303))
    unset_jwt_cookies(response)
    session.pop(RETURN_URL_SESSION_KEY, None)
    return response