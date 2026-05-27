"""Admin routes for PROMAT."""

from __future__ import annotations

from datetime import date, datetime, time, timezone
from urllib.parse import parse_qs, unquote, urlparse

from flask import Blueprint, current_app, jsonify, redirect, render_template, request, url_for
from flask_jwt_extended import get_jwt_identity, jwt_required

from ..analytics import summarize_analytics
from ..auth import Role
from ..auth import services as auth_services
from ..auth.decorators import require_role
from ..branding import BRANDING
from ..extensions import limiter
from ..i18n import resolve_ui_language, translate
from ..protected_navigation import build_admin_panel, build_protected_content_header
from ..services.mail_delivery import (
    MailConfigurationError,
    MailDeliveryError,
    MailMessage,
    MailValidationError,
    configured_default_reply_to,
    email_domain,
    send_mail,
    validate_email_address,
)
from .public_content import get_language, get_language_label

blueprint = Blueprint("admin", __name__, url_prefix="/admin")


def _recipient_domain(recipient: str) -> str:
    return email_domain(recipient)


def _current_admin_reply_to() -> str:
    admin_user_id = str(get_jwt_identity() or "")
    admin = auth_services.get_user_by_id(admin_user_id) if admin_user_id else None
    try:
        return validate_email_address(getattr(admin, "email", None), "admin reply-to")
    except MailValidationError:
        try:
            fallback = configured_default_reply_to(current_app.config)
        except MailValidationError as exc:
            raise MailConfigurationError("A valid AUTH_MAIL_DEFAULT_REPLY_TO is required.") from exc
        if not fallback:
            raise MailConfigurationError("A valid AUTH_MAIL_DEFAULT_REPLY_TO is required.")
        current_app.logger.warning(
            "Admin invitation reply-to fallback used | admin_user_id=%s | fallback_domain=%s",
            admin_user_id or "unknown",
            _recipient_domain(fallback),
        )
        return fallback


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
    contact_email: str,
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
                contact_email=contact_email,
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


def _mail_preview_payload(
    *, user, ui_lang: str, purpose: str, admin_note: str | None = None
) -> dict[str, str]:
    raw_token, reset_token = auth_services.create_reset_token_for_user(user)
    reply_to = _current_admin_reply_to()
    preview = _build_mail_preview(
        user_email=user.email or "",
        raw_token=raw_token,
        ui_lang=ui_lang,
        purpose=purpose,
        contact_email=reply_to,
        admin_note=admin_note,
    )
    current_app.logger.info(
        "Prepared admin %s message metadata | user_id=%s | recipient_domain=%s | subject_length=%s | body_length=%s",
        purpose,
        getattr(user, "id", "unknown"),
        _recipient_domain(preview["recipient"]),
        len(preview["subject"] or ""),
        len(preview["body"] or ""),
    )
    return {
        "inviteLink": preview["reset_link"],
        "inviteExpiresAt": reset_token.expires_at.isoformat(),
        "inviteMailRecipient": preview["recipient"],
        "inviteMailSubject": preview["subject"],
        "inviteMailBody": preview["body"],
        "inviteReplyTo": reply_to,
    }


def _build_admin_page_context(
    ui_lang: str,
    *,
    active_slug: str,
    title_key: str,
    intro_key: str,
) -> dict[str, object]:
    panel = build_admin_panel(ui_lang, active_slug=active_slug, translate=translate)
    content_header = build_protected_content_header(
        page_name=active_slug,
        title=_t(ui_lang, title_key),
        intro=_t(ui_lang, intro_key),
        ui_lang=ui_lang,
        translate=translate,
        section_label=panel["section_label"],
        current_href=request.path,
    )
    return {
        "auth_ui_lang": ui_lang,
        "ui_lang": ui_lang,
        "promat_panel": panel,
        "render_navigation_drawer": True,
        "shell_class": "app-shell--inner",
        "content_header": content_header,
        "body_class": "page-admin",
        "page_name": None,
    }


@blueprint.get("")
@blueprint.get("/dashboard")
@jwt_required()
@require_role(Role.ADMIN)
def dashboard():
    return redirect(url_for("admin.users_page", ui_lang=_resolve_admin_ui_lang()), 303)


@blueprint.get("/users/page")
@jwt_required()
@require_role(Role.ADMIN)
def users_page():
    ui_lang = _resolve_admin_ui_lang()
    return (
        render_template(
            "auth/admin_users.html",
            **_build_admin_page_context(
                ui_lang,
                active_slug="users",
                title_key="auth.admin_users.heading",
                intro_key="auth.admin_users.intro",
            ),
        ),
        200,
    )


@blueprint.get("/users")
@jwt_required()
@require_role(Role.ADMIN)
def users_list():
    include_inactive = (request.args.get("include_inactive") or "").strip().lower() in {
        "1",
        "true",
        "yes",
    }
    search_query = request.args.get("q") or ""
    sort_by = (request.args.get("sort") or "created_desc").strip().lower()
    items = auth_services.serialize_users_for_admin(
        auth_services.list_users(
            include_inactive=include_inactive,
            search_query=search_query,
            sort_by=sort_by,
        )
    )
    return jsonify({"items": items}), 200


@blueprint.post("/users")
@jwt_required()
@require_role(Role.ADMIN)
@limiter.limit("10 per minute")
def users_create():
    ui_lang = _resolve_admin_ui_lang()
    payload = request.get_json(silent=True) or {}
    first_name = str(payload.get("first_name") or "")
    last_name = str(payload.get("last_name") or "")
    email = auth_services.normalize_email(str(payload.get("email") or ""))
    role = str(payload.get("role") or Role.USER.value)
    access_expires_on = str(payload.get("access_expires_on") or "")
    invite_note = str(payload.get("invite_note") or "").strip()

    if role not in {member.value for member in Role}:
        return jsonify({"ok": False, "error": _t(ui_lang, "auth.admin_users.error.role_invalid")}), 400

    try:
        user = auth_services.create_user(
            first_name=first_name,
            last_name=last_name,
            email=email,
            role=role,
            is_active=True,
            access_expires_at=_parse_access_expires_on(access_expires_on),
            created_by_user_id=get_jwt_identity(),
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
    return jsonify({"ok": True, **preview_payload, "user": auth_services.serialize_users_for_admin([user])[0]}), 201


@blueprint.get("/users/<user_id>")
@jwt_required()
@require_role(Role.ADMIN)
def users_detail(user_id: str):
    user = auth_services.get_user_by_id(user_id)
    if not user:
        return jsonify({"error": "user_not_found"}), 404
    return jsonify(auth_services.serialize_users_for_admin([user])[0]), 200


@blueprint.patch("/users/<user_id>")
@jwt_required()
@require_role(Role.ADMIN)
@limiter.limit("10 per minute")
def users_update(user_id: str):
    ui_lang = _resolve_admin_ui_lang()
    payload = request.get_json(silent=True) or {}
    role = str(payload.get("role") or "")
    if role and role not in {member.value for member in Role}:
        return jsonify({"ok": False, "error": _t(ui_lang, "auth.admin_users.error.role_invalid")}), 400

    try:
        user = auth_services.update_user_admin(
            user_id,
            first_name=(str(payload.get("first_name") or "") if "first_name" in payload else None),
            last_name=(str(payload.get("last_name") or "") if "last_name" in payload else None),
            email=(auth_services.normalize_email(str(payload.get("email") or "")) if "email" in payload else None),
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

    return jsonify({"ok": True, "user": auth_services.serialize_users_for_admin([user])[0]}), 200


@blueprint.post("/users/<user_id>/reset-password")
@jwt_required()
@require_role(Role.ADMIN)
@limiter.limit("10 per minute")
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
    return jsonify({"ok": True, **preview_payload, "user": auth_services.serialize_users_for_admin([user])[0]}), 200


@blueprint.post("/users/<user_id>/send-invite")
@jwt_required()
@require_role(Role.ADMIN)
@limiter.limit("10 per minute")
def users_send_invite(user_id: str):
    ui_lang = _resolve_admin_ui_lang()
    payload = request.get_json(silent=True) or {}
    user = auth_services.get_user_by_id(user_id)
    if not user:
        return jsonify({"ok": False, "error": "user_not_found", "manualFallback": True}), 404
    if not user.email:
        return (
            jsonify(
                {
                    "ok": False,
                    "error": _t(ui_lang, "auth.admin_users.error.email_required"),
                    "manualFallback": True,
                }
            ),
            400,
        )

    recipient = auth_services.normalize_email(str(payload.get("recipient") or user.email or ""))
    if recipient != auth_services.normalize_email(user.email or ""):
        return (
            jsonify(
                {
                    "ok": False,
                    "error": _t(ui_lang, "auth.admin_users.error.recipient_mismatch"),
                    "manualFallback": True,
                }
            ),
            400,
        )

    subject = str(payload.get("subject") or "")
    body = str(payload.get("body") or "")
    try:
        reply_to = _current_admin_reply_to()
        result = send_mail(
            MailMessage(
                to_address=recipient,
                subject=subject,
                body=body,
                reply_to=reply_to,
            )
        )
        if not result.sent:
            raise MailDeliveryError(result.detail or "mail backend disabled")
    except (MailDeliveryError, MailValidationError, MailConfigurationError) as exc:
        current_app.logger.warning(
            "Admin invitation email failed | user_id=%s | recipient_domain=%s | error_type=%s",
            user_id,
            _recipient_domain(recipient),
            type(exc).__name__,
        )
        return (
            jsonify(
                {
                    "ok": False,
                    "error": _t(ui_lang, "auth.admin_users.send_mail_failed"),
                    "manualFallback": True,
                }
            ),
            503,
        )

    current_app.logger.info(
        "Admin invitation email sent | user_id=%s | recipient_domain=%s | reply_to_domain=%s | subject_length=%s | body_length=%s",
        user_id,
        _recipient_domain(recipient),
        _recipient_domain(reply_to),
        len(subject or ""),
        len(body or ""),
    )
    return (
        jsonify(
            {
                "ok": True,
                "message": _t(ui_lang, "auth.admin_users.send_mail_success", reply_to=reply_to),
                "replyTo": reply_to,
            }
        ),
        200,
    )


@blueprint.get("/analytics/page")
@jwt_required()
@require_role(Role.ADMIN)
def analytics_page():
    ui_lang = _resolve_admin_ui_lang()
    period = (request.args.get("period") or "30d").strip().lower()
    if period not in {"7d", "30d", "all"}:
        period = "30d"

    analytics = summarize_analytics(period)
    matrix = analytics["matrix"]
    languages = []
    for slug in ("spanish", "french", "german", "english"):
        language = get_language(slug)
        label = get_language_label(language, ui_lang) if language else slug
        languages.append(
            {
                "slug": slug,
                "label": label,
                "research": matrix.get((slug, "research"), {"page_views": 0, "unique_visitors": 0}),
                "teaching": matrix.get((slug, "teaching"), {"page_views": 0, "unique_visitors": 0}),
            }
        )

    return (
        render_template(
            "pages/admin_analytics.html",
            analytics=analytics,
            analytics_languages=languages,
            analytics_period=period,
            analytics_periods=[
                {"value": "7d", "label": _t(ui_lang, "auth.admin_analytics.period_7d")},
                {"value": "30d", "label": _t(ui_lang, "auth.admin_analytics.period_30d")},
                {"value": "all", "label": _t(ui_lang, "auth.admin_analytics.period_all")},
            ],
            **_build_admin_page_context(
                ui_lang,
                active_slug="analytics",
                title_key="auth.admin_analytics.heading",
                intro_key="auth.admin_analytics.intro",
            ),
        ),
        200,
    )
