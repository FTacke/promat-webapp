from __future__ import annotations

import smtplib
import ssl
from dataclasses import dataclass
from datetime import datetime, timezone
from email.message import EmailMessage
from typing import Callable

from flask import current_app

from ..auth.models import AccessRequest
from ..auth.services import access_request_contact_email, access_request_subject, normalize_email
from ..extensions.sqlalchemy_ext import get_session


@dataclass(frozen=True)
class AccessRequestNotificationMessage:
    request_id: str
    from_address: str
    to_address: str
    reply_to: str | None
    subject: str
    body: str


def _email_domain(email: str) -> str:
    normalized = normalize_email(email)
    return normalized.partition("@")[2] or "unknown"


def _header_safe_email(email: str | None) -> str | None:
    normalized = normalize_email(email or "")
    if not normalized or any(character in normalized for character in {"\r", "\n"}):
        return None
    local_part, separator, domain_part = normalized.partition("@")
    if separator != "@" or not local_part or not domain_part or "." not in domain_part:
        return None
    return normalized


def _mail_enabled() -> bool:
    return bool(current_app.config.get("AUTH_ACCESS_REQUEST_MAIL_ENABLED"))


def _from_address() -> str:
    return str(current_app.config.get("AUTH_ACCESS_REQUEST_FROM_EMAIL") or "").strip()


def _update_request_status(request_id: str, status: str) -> None:
    with get_session() as session:
        access_request = session.get(AccessRequest, request_id)
        if access_request is None:
            return
        access_request.status = status
        access_request.updated_at = datetime.now(timezone.utc)


def _build_notification_body(access_request: AccessRequest) -> str:
    submitted_at = access_request.created_at
    if submitted_at.tzinfo is None:
        submitted_at = submitted_at.replace(tzinfo=timezone.utc)

    return "\n".join(
        [
            f"Request ID: {access_request.id}",
            f"Status: {access_request.status}",
            f"Submitted at: {submitted_at.isoformat()}",
            f"UI language: {access_request.ui_lang or '-'}",
            f"Requested path: {access_request.requested_path or '-'}",
            "",
            f"Name: {access_request.last_name}, {access_request.first_name}",
            f"Email: {access_request.email}",
            f"Institution: {access_request.institution}",
            f"Role / function: {access_request.role_or_function}",
            "",
            "Purpose:",
            access_request.purpose,
            "",
            f"Consent confirmed: {'yes' if access_request.consent_confirmed else 'no'}",
        ]
    )


def build_access_request_notification_message(
    access_request: AccessRequest,
) -> AccessRequestNotificationMessage:
    from_address = _from_address()
    if not from_address:
        raise RuntimeError(
            "AUTH_ACCESS_REQUEST_FROM_EMAIL is required when access-request mail delivery is enabled."
        )

    to_address = access_request_contact_email()
    if not to_address:
        raise RuntimeError(
            "AUTH_ACCESS_REQUEST_EMAIL is required when access-request mail delivery is enabled."
        )

    reply_to = None
    if current_app.config.get("AUTH_ACCESS_REQUEST_REPLY_TO_ENABLED"):
        reply_to = _header_safe_email(access_request.email)

    return AccessRequestNotificationMessage(
        request_id=str(access_request.id or ""),
        from_address=from_address,
        to_address=to_address,
        reply_to=reply_to,
        subject=access_request_subject(),
        body=_build_notification_body(access_request),
    )


def _smtp_send(message: AccessRequestNotificationMessage) -> None:
    host = str(current_app.config.get("AUTH_ACCESS_REQUEST_SMTP_HOST") or "").strip()
    if not host:
        raise RuntimeError(
            "AUTH_ACCESS_REQUEST_SMTP_HOST is required when access-request mail delivery is enabled."
        )

    port = int(current_app.config.get("AUTH_ACCESS_REQUEST_SMTP_PORT") or 587)
    username = str(current_app.config.get("AUTH_ACCESS_REQUEST_SMTP_USERNAME") or "").strip()
    password = str(current_app.config.get("AUTH_ACCESS_REQUEST_SMTP_PASSWORD") or "")
    use_tls = bool(current_app.config.get("AUTH_ACCESS_REQUEST_SMTP_USE_TLS"))
    use_ssl = bool(current_app.config.get("AUTH_ACCESS_REQUEST_SMTP_USE_SSL"))
    timeout = int(current_app.config.get("AUTH_ACCESS_REQUEST_SMTP_TIMEOUT_SECONDS") or 10)

    email_message = EmailMessage()
    email_message["From"] = message.from_address
    email_message["To"] = message.to_address
    email_message["Subject"] = message.subject
    if message.reply_to:
        email_message["Reply-To"] = message.reply_to
    email_message.set_content(message.body)

    ssl_context = ssl.create_default_context()
    if use_ssl:
        with smtplib.SMTP_SSL(host, port, timeout=timeout, context=ssl_context) as smtp:
            if username:
                smtp.login(username, password)
            smtp.send_message(email_message)
        return

    with smtplib.SMTP(host, port, timeout=timeout) as smtp:
        if use_tls:
            smtp.starttls(context=ssl_context)
        if username:
            smtp.login(username, password)
        smtp.send_message(email_message)


def deliver_access_request_notification(access_request: AccessRequest) -> bool:
    if not _mail_enabled():
        current_app.logger.info(
            "Access request notification skipped | request_id=%s | status=%s | mail_delivery=%s",
            access_request.id,
            access_request.status,
            "disabled",
        )
        return False

    message = build_access_request_notification_message(access_request)
    sender: Callable[[AccessRequestNotificationMessage], None] | None = current_app.config.get(
        "AUTH_ACCESS_REQUEST_MAIL_SENDER"
    )

    try:
        if callable(sender):
            sender(message)
        else:
            _smtp_send(message)
    except Exception as exc:  # noqa: BLE001
        _update_request_status(message.request_id, "notification_failed")
        access_request.status = "notification_failed"
        current_app.logger.warning(
            "Access request notification failed | request_id=%s | status=%s | email_domain=%s | reply_to_set=%s | error_type=%s",
            access_request.id,
            access_request.status,
            _email_domain(access_request.email),
            bool(message.reply_to),
            type(exc).__name__,
        )
        return False

    _update_request_status(message.request_id, "notified")
    access_request.status = "notified"
    current_app.logger.info(
        "Access request notification sent | request_id=%s | status=%s | email_domain=%s | reply_to_set=%s",
        access_request.id,
        access_request.status,
        _email_domain(access_request.email),
        bool(message.reply_to),
    )
    return True