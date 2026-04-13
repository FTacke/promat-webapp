"""Admin routes for PROMAT."""

from __future__ import annotations

from datetime import date, datetime, time, timezone
from urllib.parse import parse_qs, unquote, urlparse

from flask import Blueprint, current_app, jsonify, render_template, request, url_for
from flask_jwt_extended import jwt_required

from ..auth import Role
from ..auth import services as auth_services
from ..auth.decorators import require_role
from ..branding import BRANDING
from ..i18n import resolve_ui_language, translate

blueprint = Blueprint("admin", __name__, url_prefix="/admin")


def _resolve_admin_ui_lang() -> str:
    raw_value = request.values.get("ui_lang") or request.args.get("ui_lang")
    if not raw_value:
        for candidate in (request.referrer, request.path):
            if not candidate:
                continue
            parsed = urlparse(unquote(candidate))
            query_value = (parse_qs(parsed.query).get("ui_lang") or [""])[0]
            if query_value:
                raw_value = query_value
                break
            path = parsed.path or str(candidate)
            if not path.startswith("/"):
                continue
            raw_value = path.lstrip("/").split("/", 1)[0]
            if raw_value:
                break
    return resolve_ui_language(raw_value)


def _t(ui_lang: str, key: str, **kwargs: object) -> str:
    return translate(ui_lang, key, **kwargs)


def _parse_access_expires_on(raw_value: str | None):
    value = (raw_value or "").strip()
    if not value:
        return None
    parsed = date.fromisoformat(value)
    return datetime.combine(parsed, time(23, 59, 59), tzinfo=timezone.utc)


def _build_password_link(raw_token: str, ui_lang: str) -> str:
    return url_for(
        "auth.password_reset_page",
        token=raw_token,
        ui_lang=ui_lang,
        _external=True,
    )


def _build_mail_preview(
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
    lines.extend(["", _t(ui_lang, f"{key_prefix}.outro", contact_email=auth_services.access_request_contact_email())])
    return {
        "recipient": user_email,
        "subject": _t(ui_lang, f"{key_prefix}.subject", app_name=BRANDING["app_display_name"]),
        "body": "\n".join(lines),
        "reset_link": reset_link,
    }


def _mail_preview_payload(*, user, ui_lang: str, purpose: str, admin_note: str | None = None) -> dict[str, str]:
    raw_token, reset_token = auth_services.create_reset_token_for_user(user)
    preview = _build_mail_preview(
        user_email=user.email or "",
        raw_token=raw_token,
        ui_lang=ui_lang,
        purpose=purpose,
        admin_note=admin_note,
    )
    current_app.logger.info(
        "Prepared admin %s message for %s | subject=%s | body=%s",
        purpose,
        preview["recipient"],
        preview["subject"],
        preview["body"].replace("\n", " | "),
    )
    return {
        "inviteLink": preview["reset_link"],
        "inviteExpiresAt": reset_token.expires_at.isoformat(),
        "inviteMailRecipient": preview["recipient"],
        "inviteMailSubject": preview["subject"],
        "inviteMailBody": preview["body"],
    }


@blueprint.get("")
@blueprint.get("/dashboard")
@jwt_required()
@require_role(Role.ADMIN)
def dashboard():
    return render_template("pages/admin_dashboard.html"), 200


@blueprint.get("/users/page")
@jwt_required()
@require_role(Role.ADMIN)
def users_page():
    return render_template(
        "auth/admin_users.html",
        auth_ui_lang=_resolve_admin_ui_lang(),
    ), 200


@blueprint.get("/users")
@jwt_required()
@require_role(Role.ADMIN)
def users_list():
    include_inactive = (request.args.get("include_inactive") or "").strip().lower() in {"1", "true", "yes"}
    search_query = request.args.get("q") or ""
    items = [
        auth_services.serialize_user_for_admin(user)
        for user in auth_services.list_users(
            include_inactive=include_inactive,
            search_query=search_query,
        )
    ]
    return jsonify({"items": items}), 200


@blueprint.post("/users")
@jwt_required()
@require_role(Role.ADMIN)
def users_create():
    ui_lang = _resolve_admin_ui_lang()
    payload = request.get_json(silent=True) or {}
    email = auth_services.normalize_email(str(payload.get("email") or ""))
    role = str(payload.get("role") or Role.USER.value)
    access_expires_on = str(payload.get("access_expires_on") or "")
    invite_note = str(payload.get("invite_note") or "").strip()

    if role not in {member.value for member in Role}:
        return jsonify({"ok": False, "error": _t(ui_lang, "auth.admin_users.error.role_invalid")}), 400

    try:
        user = auth_services.create_user(
            email=email,
            role=role,
            is_active=True,
            access_expires_at=_parse_access_expires_on(access_expires_on),
        )
    except ValueError as exc:
        code = str(exc)
        return jsonify({"ok": False, "error": _t(ui_lang, f"auth.admin_users.error.{code}")}), 400

    preview_payload = _mail_preview_payload(
        user=user,
        ui_lang=ui_lang,
        purpose="invite",
        admin_note=invite_note,
    )
    return jsonify({"ok": True, **preview_payload, "user": auth_services.serialize_user_for_admin(user)}), 201


@blueprint.get("/users/<user_id>")
@jwt_required()
@require_role(Role.ADMIN)
def users_detail(user_id: str):
    user = auth_services.get_user_by_id(user_id)
    if not user:
        return jsonify({"error": "user_not_found"}), 404
    return jsonify(auth_services.serialize_user_for_admin(user)), 200


@blueprint.patch("/users/<user_id>")
@jwt_required()
@require_role(Role.ADMIN)
def users_update(user_id: str):
    ui_lang = _resolve_admin_ui_lang()
    payload = request.get_json(silent=True) or {}
    role = str(payload.get("role") or "")
    if role and role not in {member.value for member in Role}:
        return jsonify({"ok": False, "error": _t(ui_lang, "auth.admin_users.error.role_invalid")}), 400

    try:
        user = auth_services.update_user_admin(
            user_id,
            email=auth_services.normalize_email(str(payload.get("email") or "")),
            role=role or None,
            is_active=payload.get("is_active") if "is_active" in payload else None,
            access_expires_at=(
                _parse_access_expires_on(str(payload.get("access_expires_on") or ""))
                if "access_expires_on" in payload
                else auth_services._UNSET
            ),
        )
    except KeyError:
        return jsonify({"ok": False, "error": "user_not_found"}), 404
    except ValueError as exc:
        code = str(exc)
        return jsonify({"ok": False, "error": _t(ui_lang, f"auth.admin_users.error.{code}")}), 400

    return jsonify({"ok": True, "user": auth_services.serialize_user_for_admin(user)}), 200


@blueprint.post("/users/<user_id>/reset-password")
@jwt_required()
@require_role(Role.ADMIN)
def users_reset_password(user_id: str):
    ui_lang = _resolve_admin_ui_lang()
    user = auth_services.get_user_by_id(user_id)
    if not user:
        return jsonify({"ok": False, "error": "user_not_found"}), 404
    if not user.email:
        return jsonify({"ok": False, "error": _t(ui_lang, "auth.admin_users.error.email_required")}), 400

    user = auth_services.mark_user_for_password_reset(user_id)
    preview_payload = _mail_preview_payload(
        user=user,
        ui_lang=ui_lang,
        purpose="reset",
    )
    return jsonify({"ok": True, **preview_payload, "user": auth_services.serialize_user_for_admin(user)}), 200