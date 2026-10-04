from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from urllib.parse import urlsplit

from flask import current_app

from ..branding import BRANDING
from ..i18n import normalize_supported_ui_language, translate


@dataclass(frozen=True)
class AuthMailPreview:
    recipient: str
    subject: str
    body: str
    reset_link: str
    ui_lang: str
    purpose: str


def resolve_mail_ui_language(raw_value: object) -> str:
    if raw_value is None:
        return "de"
    return normalize_supported_ui_language(str(raw_value).strip().lower()) or "de"


def recipient_display_name(user: Any) -> str:
    first_name = str(getattr(user, "first_name", "") or "").strip()
    last_name = str(getattr(user, "last_name", "") or "").strip()
    return " ".join(part for part in (first_name, last_name) if part).strip()


def _t(ui_lang: str, key: str, **kwargs: object) -> str:
    return translate(ui_lang, key, **kwargs)


def build_password_link(raw_token: str, ui_lang: str) -> str:
    """Absolute password-reset/invitation link on the configured canonical origin.

    The origin comes only from ``PROMAT_PUBLIC_BASE_URL`` (validated at startup). Request headers such as
    ``Host`` or ``X-Forwarded-Host`` are never consulted, so a forged header cannot redirect the link, and the
    path is built from a fresh URL adapter so a forged ``X-Forwarded-Prefix`` cannot alter it either.
    """
    base_url = str(current_app.config.get("PROMAT_PUBLIC_BASE_URL") or "").rstrip("/")
    parts = urlsplit(base_url)
    if parts.scheme not in {"http", "https"} or not parts.netloc:
        # Never fall back to the request host: configuration is validated in load_config() at startup.
        raise RuntimeError("PROMAT_PUBLIC_BASE_URL is not configured; refusing to build an external link.")
    adapter = current_app.url_map.bind(parts.netloc, script_name="/", url_scheme=parts.scheme)
    path = adapter.build(
        "auth.password_reset_page",
        {"token": raw_token, "ui_lang": ui_lang},
        force_external=False,
    )
    return f"{base_url}{path}"


def build_auth_mail_preview(
    *,
    user: Any,
    raw_token: str,
    ui_lang: str,
    purpose: str,
    contact_email: str | None = None,
    admin_note: str | None = None,
) -> AuthMailPreview:
    mail_ui_lang = resolve_mail_ui_language(ui_lang)
    reset_link = build_password_link(raw_token, mail_ui_lang)
    expiry_days = int(current_app.config.get("AUTH_RESET_TOKEN_EXP_DAYS", 14))
    key_prefix = "auth.mail.invite" if purpose == "invite" else "auth.mail.reset"
    display_name = recipient_display_name(user)
    greeting_key = "auth.mail.greeting_named" if display_name else "auth.mail.greeting_generic"

    lines = [
        _t(mail_ui_lang, greeting_key, display_name=display_name),
        "",
        _t(mail_ui_lang, f"{key_prefix}.intro", app_name=BRANDING["app_display_name"]),
        "",
        _t(mail_ui_lang, f"{key_prefix}.link_intro"),
        reset_link,
    ]

    normalized_note = (admin_note or "").strip()
    if purpose == "invite" and normalized_note:
        lines.extend(["", _t(mail_ui_lang, "auth.mail.invite.note_label"), normalized_note])

    if purpose == "reset":
        lines.extend(["", _t(mail_ui_lang, "auth.mail.reset.expiry", expiry_days=expiry_days)])

    if purpose == "invite":
        lines.extend(
            [
                "",
                _t(
                    mail_ui_lang,
                    "auth.mail.invite.outro",
                    contact_email=contact_email or "",
                ),
            ]
        )

    return AuthMailPreview(
        recipient=str(getattr(user, "email", "") or ""),
        subject=_t(mail_ui_lang, f"{key_prefix}.subject", app_name=BRANDING["app_display_name"]),
        body="\n".join(lines),
        reset_link=reset_link,
        ui_lang=mail_ui_lang,
        purpose=purpose,
    )
