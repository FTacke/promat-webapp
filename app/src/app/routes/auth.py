"""Authentication routes for PROMAT."""

from __future__ import annotations

from urllib.parse import unquote, urlparse

from flask import (
    Blueprint,
    Response,
    current_app,
    flash,
    jsonify,
    make_response,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_jwt_extended import (
    get_jwt,
    get_jwt_identity,
    jwt_required,
    set_access_cookies,
    unset_jwt_cookies,
    verify_jwt_in_request,
)

from ..auth import Role
from ..auth import services as auth_services
from ..branding import BRANDING
from ..extensions import limiter
from ..i18n import resolve_ui_language, translate
from ..protected_navigation import (
    build_admin_panel,
    build_protected_content_header,
)

blueprint = Blueprint("auth", __name__, url_prefix="/auth")
RETURN_URL_SESSION_KEY = "_return_url_after_login"


def _recipient_domain(recipient: str) -> str:
    value = (recipient or "").strip()
    if "@" not in value:
        return "unknown"
    return value.rsplit("@", 1)[-1].lower() or "unknown"


def save_return_url(url: str | None = None) -> None:
    """Remember a target URL for the next successful login."""
    current_url = url or request.url
    if current_url and not any(
        part in current_url for part in ["/auth/", "/static/", "/health"]
    ):
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


def _resolve_auth_ui_lang(*candidates: str | None) -> str:
    raw_value = request.values.get("ui_lang") or request.args.get("ui_lang")
    if not raw_value:
        for candidate in candidates:
            if not candidate:
                continue
            parsed = urlparse(unquote(candidate))
            path = parsed.path or str(candidate)
            if not path.startswith("/"):
                continue
            raw_value = path.lstrip("/").split("/", 1)[0]
            if raw_value:
                break
    return resolve_ui_language(raw_value)


def _t(ui_lang: str, key: str, **kwargs: object) -> str:
    return translate(ui_lang, key, **kwargs)


def _build_access_request_href(ui_lang: str, next_url: str | None = None) -> str:
    if next_url:
        return url_for("public.access_request_page", next=next_url)
    return url_for("public.access_request_page", ui_lang=ui_lang)


def _render_login_page(
    *,
    status_code: int = 200,
    next_url: str | None = None,
    email: str = "",
) -> Response:
    ui_lang = _resolve_auth_ui_lang(next_url, request.referrer)
    return (
        render_template(
            "auth/login.html",
            next=next_url or "",
            login_email=email,
            auth_ui_lang=ui_lang,
            access_request_href=_build_access_request_href(ui_lang, next_url),
            page_name="login",
            shell_class="app-shell--panel-hidden",
            ui_lang=ui_lang,
        ),
        status_code,
    )


def _render_password_forgot_page(
    *,
    status_code: int = 200,
    email: str = "",
    submitted: bool = False,
) -> Response:
    ui_lang = _resolve_auth_ui_lang(request.referrer)
    return (
        render_template(
            "auth/password_forgot.html",
            email=email,
            submitted=submitted,
            auth_ui_lang=ui_lang,
            contact_email=auth_services.access_request_contact_email(),
            access_request_href=_build_access_request_href(ui_lang),
            ui_lang=ui_lang,
        ),
        status_code,
    )


def _render_password_reset_page(
    *,
    status_code: int = 200,
    token: str = "",
    token_status: str = "missing",
) -> Response:
    ui_lang = _resolve_auth_ui_lang(request.values.get("next"), request.referrer)
    return (
        render_template(
            "auth/password_reset.html",
            token=token,
            token_status=token_status,
            auth_ui_lang=ui_lang,
            access_request_href=_build_access_request_href(ui_lang),
            ui_lang=ui_lang,
        ),
        status_code,
    )


def _build_password_link(raw_token: str, ui_lang: str) -> str:
    return url_for(
        "auth.password_reset_page",
        token=raw_token,
        ui_lang=ui_lang,
        _external=True,
    )


def _build_password_message(
    *,
    user_email: str,
    raw_token: str,
    ui_lang: str,
    purpose: str,
    admin_note: str | None = None,
) -> dict[str, str]:
    reset_link = _build_password_link(raw_token, ui_lang)
    expiry_days = int(current_app.config.get("AUTH_RESET_TOKEN_EXP_DAYS", 14))
    key_prefix = "auth.mail.invite" if purpose == "invite" else "auth.mail.reset"
    lines = [
        _t(ui_lang, f"{key_prefix}.greeting", app_name=BRANDING["app_display_name"]),
        "",
        _t(ui_lang, f"{key_prefix}.intro"),
        _t(ui_lang, f"{key_prefix}.link", reset_link=reset_link),
        _t(ui_lang, f"{key_prefix}.expiry", expiry_days=expiry_days),
    ]
    normalized_note = (admin_note or "").strip()
    if normalized_note:
        lines.extend(["", _t(ui_lang, "auth.mail.invite.note_label"), normalized_note])
    lines.extend(
        [
            "",
            _t(
                ui_lang,
                f"{key_prefix}.outro",
                contact_email=auth_services.access_request_contact_email(),
            ),
        ]
    )
    return {
        "recipient": user_email,
        "subject": _t(
            ui_lang,
            f"{key_prefix}.subject",
            app_name=BRANDING["app_display_name"],
        ),
        "body": "\n".join(lines),
        "reset_link": reset_link,
    }


def _log_prepared_auth_message(
    *, recipient: str, subject: str, body: str, purpose: str
) -> None:
    current_app.logger.info(
        "Prepared %s message metadata | recipient_domain=%s | subject_length=%s | body_length=%s",
        purpose,
        _recipient_domain(recipient),
        len(subject or ""),
        len(body or ""),
    )


def _password_validation_error(
    ui_lang: str,
    *,
    new_password: str,
    confirm_password: str,
) -> str | None:
    if not new_password:
        return _t(ui_lang, "auth.password_reset.error.password_required")
    if new_password != confirm_password:
        return _t(ui_lang, "auth.password_reset.error.password_mismatch")
    valid, error_key = auth_services.validate_password_strength(new_password)
    if valid:
        return None
    return _t(ui_lang, f"auth.password_rules.{error_key}")


def _forgot_password_response(email: str, ui_lang: str) -> None:
    user = auth_services.find_user_by_email(email)
    if user and user.deleted_at is None:
        raw_token, _ = auth_services.create_reset_token_for_user(user)
        message = _build_password_message(
            user_email=user.email or email,
            raw_token=raw_token,
            ui_lang=ui_lang,
            purpose="reset",
        )
        _log_prepared_auth_message(
            recipient=message["recipient"],
            subject=message["subject"],
            body=message["body"],
            purpose="password-reset",
        )


def _json_ok(payload: dict[str, object] | None = None, *, status_code: int = 200) -> Response:
    response_payload = {"ok": True}
    if payload:
        response_payload.update(payload)
    return jsonify(response_payload), status_code


def _build_account_context(ui_lang: str, *, user, page_key: str) -> dict[str, object]:
    role_value = auth_services.normalize_role(user.role)
    is_admin = role_value == Role.ADMIN.value
    panel = build_admin_panel(ui_lang, active_slug="account", translate=translate) if is_admin else None
    shell_class = "app-shell--inner" if panel else "app-shell--inner app-shell--panel-hidden"
    section_label = panel["section_label"] if panel else None
    content_header = build_protected_content_header(
        page_name="account",
        title=_t(ui_lang, f"auth.{page_key}.heading"),
        intro=_t(ui_lang, f"auth.{page_key}.intro"),
        ui_lang=ui_lang,
        translate=translate,
        section_label=section_label,
        current_href=url_for("auth.account_page", ui_lang=ui_lang),
        back_link={
            "label": _t(ui_lang, "auth.account.heading"),
            "href": url_for("auth.account_page", ui_lang=ui_lang),
        } if page_key == "account_password" else None,
    )
    return {
        "auth_ui_lang": ui_lang,
        "ui_lang": ui_lang,
        "shell_class": shell_class,
        "render_navigation_drawer": bool(panel),
        "promat_panel": panel,
        "content_header": content_header,
        "body_class": "page-protected-account",
        "page_name": None,
    }


def _render_account_page(*, user, status_code: int = 200) -> Response:
    ui_lang = _resolve_auth_ui_lang(request.referrer)
    return (
        render_template(
            "pages/account.html",
            account_user=user,
            account_role=auth_services.normalize_role(user.role),
            account_status=auth_services.admin_status_code(user),
            **_build_account_context(ui_lang, user=user, page_key="account"),
        ),
        status_code,
    )


def _render_account_password_page(*, user, status_code: int = 200) -> Response:
    ui_lang = _resolve_auth_ui_lang(request.referrer)
    return (
        render_template(
            "auth/account_password.html",
            account_user=user,
            must_reset_mode=bool(user.must_reset_password or request.args.get("mustReset")),
            **_build_account_context(ui_lang, user=user, page_key="account_password"),
        ),
        status_code,
    )


def _default_post_login_target(ui_lang: str, *, user) -> str:
    if auth_services.normalize_role(user.role) == Role.ADMIN.value:
        return url_for("admin.users_page", ui_lang=ui_lang)
    return url_for("auth.account_page", ui_lang=ui_lang)


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
def account_page_legacy() -> Response:
    return redirect(url_for("auth.account_page", ui_lang=_resolve_auth_ui_lang(request.referrer)), 303)


@blueprint.get("/account", endpoint="account_page")
@jwt_required()
def account_page() -> Response:
    identity = get_jwt_identity()
    user = auth_services.get_user_by_id(identity) if identity else None
    if not user:
        flash(_t(_resolve_auth_ui_lang(request.referrer), "auth.flash.login_required"), "error")
        return redirect(url_for("public.login", ui_lang=_resolve_auth_ui_lang(request.referrer)), 303)
    return _render_account_page(user=user)


@blueprint.post("/account", endpoint="account_update")
@jwt_required()
def account_update() -> Response:
    identity = get_jwt_identity()
    user = auth_services.get_user_by_id(identity) if identity else None
    ui_lang = _resolve_auth_ui_lang(request.referrer)
    if not user:
        flash(_t(ui_lang, "auth.flash.login_required"), "error")
        return redirect(url_for("public.login", ui_lang=ui_lang), 303)

    try:
        auth_services.update_user_profile(
            str(user.id),
            first_name=request.form.get("first_name", ""),
            last_name=request.form.get("last_name", ""),
            email=request.form.get("email", ""),
        )
    except ValueError as exc:
        flash(_t(ui_lang, f"auth.account.error.{exc}"), "error")
        refreshed_user = auth_services.get_user_by_id(str(user.id)) or user
        return _render_account_page(user=refreshed_user, status_code=400)

    flash(_t(ui_lang, "auth.account.success"), "success")
    return redirect(url_for("auth.account_page", ui_lang=ui_lang), 303)


@blueprint.get("/account/password", endpoint="account_password_page")
@jwt_required()
def account_password_page() -> Response:
    identity = get_jwt_identity()
    user = auth_services.get_user_by_id(identity) if identity else None
    if not user:
        flash(_t(_resolve_auth_ui_lang(request.referrer), "auth.flash.login_required"), "error")
        return redirect(url_for("public.login", ui_lang=_resolve_auth_ui_lang(request.referrer)), 303)
    return _render_account_password_page(user=user)


@blueprint.post("/account/password", endpoint="account_password_submit")
@jwt_required()
def account_password_submit() -> Response:
    ui_lang = _resolve_auth_ui_lang(request.referrer)
    user = auth_services.get_user_by_id(get_jwt_identity())
    if not user:
        flash(_t(ui_lang, "auth.flash.login_required"), "error")
        return redirect(url_for("public.login", ui_lang=ui_lang), 303)

    old_password = request.form.get("old_password", "")
    new_password = request.form.get("new_password", "")
    confirm_password = request.form.get("confirm_password", "")

    error_message = _password_validation_error(
        ui_lang,
        new_password=new_password,
        confirm_password=confirm_password,
    )
    if error_message:
        flash(error_message, "error")
        return _render_account_password_page(user=user, status_code=400)

    try:
        auth_services.change_user_password(
            str(user.id),
            current_password=old_password,
            new_password=new_password,
            require_current_password=not user.must_reset_password,
        )
    except ValueError as exc:
        if str(exc) == "current_password":
            flash(_t(ui_lang, "auth.account_password.error.current_password"), "error")
            return _render_account_password_page(user=user, status_code=400)
        raise
    flash(_t(ui_lang, "auth.account_password.success"), "success")
    return redirect(url_for("auth.account_page", ui_lang=ui_lang), 303)


@blueprint.post("/change-password")
@jwt_required()
def change_password() -> Response:
    ui_lang = _resolve_auth_ui_lang(request.referrer)
    payload = request.get_json(silent=True) or request.form
    old_password = (payload.get("oldPassword") or "") if payload else ""
    new_password = (payload.get("newPassword") or "") if payload else ""
    confirm_password = (
        (payload.get("confirmPassword") or new_password) if payload else new_password
    )

    user = auth_services.get_user_by_id(get_jwt_identity())
    if not user:
        return jsonify({"ok": False, "message": _t(ui_lang, "auth.flash.login_required")}), 401

    error_message = _password_validation_error(
        ui_lang,
        new_password=new_password,
        confirm_password=confirm_password,
    )
    if error_message:
        return jsonify({"ok": False, "message": error_message}), 400

    try:
        auth_services.change_user_password(
            str(user.id),
            current_password=old_password,
            new_password=new_password,
            require_current_password=not user.must_reset_password,
        )
    except ValueError as exc:
        if str(exc) == "current_password":
            return jsonify({"ok": False, "message": _t(ui_lang, "auth.account_password.error.current_password")}), 400
        raise
    return jsonify({"ok": True, "message": _t(ui_lang, "auth.account_password.success")}), 200


@blueprint.get("/password/forgot")
def password_forgot_page() -> Response:
    return _render_password_forgot_page()


@blueprint.post("/password/forgot")
@limiter.limit("5 per minute")
def password_forgot_submit() -> Response:
    email = auth_services.normalize_email(request.form.get("email", ""))
    ui_lang = _resolve_auth_ui_lang(request.referrer)
    if not email:
        flash(_t(ui_lang, "auth.password_forgot.error.email_required"), "error")
        return _render_password_forgot_page(status_code=400, email=email)

    _forgot_password_response(email, ui_lang)
    flash(_t(ui_lang, "auth.password_forgot.success"), "success")
    return _render_password_forgot_page(email=email, submitted=True)


@blueprint.post("/reset-password/request")
@limiter.limit("5 per minute")
def password_forgot_api() -> Response:
    payload = request.get_json(silent=True) or {}
    email = auth_services.normalize_email(str(payload.get("email") or ""))
    ui_lang = _resolve_auth_ui_lang(request.referrer)
    if not email:
        return jsonify({"ok": False, "message": _t(ui_lang, "auth.password_forgot.error.email_required")}), 400
    _forgot_password_response(email, ui_lang)
    return _json_ok({"message": _t(ui_lang, "auth.password_forgot.success")})


@blueprint.get("/password/reset")
def password_reset_page() -> Response:
    token = request.args.get("token") or ""
    token_status = "missing"
    if token:
        _, token_status = auth_services.inspect_reset_token(token)
    return _render_password_reset_page(token=token, token_status=token_status)


@blueprint.post("/password/reset")
@limiter.limit("10 per minute")
def password_reset_submit() -> Response:
    token = (request.form.get("token") or "").strip()
    new_password = request.form.get("new_password", "")
    confirm_password = request.form.get("confirm_password", "")
    ui_lang = _resolve_auth_ui_lang(request.referrer)

    error_message = _password_validation_error(
        ui_lang,
        new_password=new_password,
        confirm_password=confirm_password,
    )
    if error_message:
        flash(error_message, "error")
        return _render_password_reset_page(status_code=400, token=token, token_status="ok")

    reset_token, status = auth_services.verify_and_use_reset_token(token)
    if not reset_token or status != "ok":
        flash(_t(ui_lang, f"auth.password_reset.error.{status}"), "error")
        return _render_password_reset_page(status_code=400, token=token, token_status=status)

    auth_services.update_user_password(
        str(reset_token.user_id),
        auth_services.hash_password(new_password),
    )
    flash(_t(ui_lang, "auth.password_reset.success"), "success")
    return redirect(url_for("public.login", ui_lang=ui_lang), 303)


@blueprint.post("/reset-password/confirm")
@limiter.limit("10 per minute")
def password_reset_api() -> Response:
    payload = request.get_json(silent=True) or {}
    token = str(payload.get("resetToken") or "").strip()
    new_password = str(payload.get("newPassword") or "")
    confirm_password = str(payload.get("confirmPassword") or new_password)
    ui_lang = _resolve_auth_ui_lang(request.referrer)

    error_message = _password_validation_error(
        ui_lang,
        new_password=new_password,
        confirm_password=confirm_password,
    )
    if error_message:
        return jsonify({"ok": False, "message": error_message}), 400

    reset_token, status = auth_services.verify_and_use_reset_token(token)
    if not reset_token or status != "ok":
        return jsonify({"ok": False, "message": _t(ui_lang, f"auth.password_reset.error.{status}")}), 400

    auth_services.update_user_password(
        str(reset_token.user_id),
        auth_services.hash_password(new_password),
    )
    return _json_ok({"message": _t(ui_lang, "auth.password_reset.success")})


@blueprint.get("/login", endpoint="login")
def login_form() -> Response:
    next_url = _safe_next(request.args.get("next") or request.referrer)
    target_kwargs: dict[str, str] = {}
    if next_url:
        target_kwargs["next"] = next_url
    ui_lang = _resolve_auth_ui_lang(next_url, request.referrer)
    if ui_lang:
        target_kwargs["ui_lang"] = ui_lang
    target = url_for("public.login", **target_kwargs)
    return redirect(target, 303)


@blueprint.post("/login", endpoint="login_post")
@limiter.limit("5 per minute")
def login_post() -> Response:
    email = auth_services.normalize_email(request.form.get("email", ""))
    password = request.form.get("password", "")
    next_raw = (
        request.form.get("next")
        or request.args.get("next")
        or session.pop(RETURN_URL_SESSION_KEY, None)
    )
    next_url = _safe_next(next_raw)
    ui_lang = _resolve_auth_ui_lang(next_url, request.referrer)

    if not email:
        flash(_t(ui_lang, "auth.login.error.email_required"), "error")
        return _render_login_page(status_code=400, next_url=next_url, email=email)

    user = auth_services.find_user_by_email(email)
    if not user or not auth_services.verify_password(password, user.password_hash):
        auth_services.on_failed_login(user)
        flash(_t(ui_lang, "auth.login.error.invalid_credentials"), "error")
        return _render_login_page(status_code=401, next_url=next_url, email=email)

    status = auth_services.check_account_status(user)
    if not status.ok:
        flash(_t(ui_lang, f"auth.login.error.{status.code}"), "error")
        return _render_login_page(status_code=403, next_url=next_url, email=email)

    auth_services.on_successful_login(user)
    access_token = auth_services.create_access_token_for_user(user)
    target = next_url or _default_post_login_target(ui_lang, user=user)
    response = make_response(redirect(target, 303))
    set_access_cookies(response, access_token)
    response.headers["Cache-Control"] = "no-store, private"
    return response


@blueprint.route("/logout_any", methods=["GET", "POST"])
@blueprint.route("/logout", methods=["GET", "POST"])
def logout_any() -> Response:
    response = make_response(redirect(url_for("public.landing_page"), 303))
    unset_jwt_cookies(response)
    session.pop(RETURN_URL_SESSION_KEY, None)
    return response
