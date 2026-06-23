from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable

from flask import current_app

from ..auth.models import AccessRequest
from ..auth.services import access_request_contact_email, access_request_subject
from ..extensions.sqlalchemy_ext import get_session
from .mail_delivery import (
    MailMessage,
    MailValidationError,
    configured_from_email,
    configured_from_name,
    configured_default_reply_to,
    email_domain,
    send_mail,
    validate_email_address,
)


@dataclass(frozen=True)
class AccessRequestNotificationMessage:
    request_id: str
    from_address: str
    from_name: str | None
    to_address: str
    reply_to: str | None
    subject: str
    body: str


def _email_domain(email: str) -> str:
    return email_domain(email)


def _mail_enabled() -> bool:
    return bool(current_app.config.get("AUTH_ACCESS_REQUEST_MAIL_ENABLED"))


def _from_address() -> str:
    return configured_from_email(current_app.config)


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

    to_address = validate_email_address(access_request_contact_email(), "AUTH_ACCESS_REQUEST_EMAIL")
    if not to_address:
        raise RuntimeError(
            "AUTH_ACCESS_REQUEST_EMAIL is required when access-request mail delivery is enabled."
        )

    reply_to = None
    if current_app.config.get("AUTH_ACCESS_REQUEST_REPLY_TO_ENABLED"):
        try:
            reply_to = validate_email_address(access_request.email, "access request reply-to")
        except MailValidationError:
            reply_to = configured_default_reply_to(current_app.config)

    return AccessRequestNotificationMessage(
        request_id=str(access_request.id or ""),
        from_address=from_address,
        from_name=configured_from_name(current_app.config),
        to_address=to_address,
        reply_to=reply_to,
        subject=access_request_subject(),
        body=_build_notification_body(access_request),
    )


def _deliver_with_configured_backend(message: AccessRequestNotificationMessage) -> None:
    result = send_mail(
        MailMessage(
            to_address=message.to_address,
            subject=message.subject,
            body=message.body,
            from_email=message.from_address,
            from_name=message.from_name,
            reply_to=message.reply_to,
        )
    )
    if not result.sent:
        raise RuntimeError(f"mail backend did not send: {result.detail or result.backend}")


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
            _deliver_with_configured_backend(message)
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
    except Exception as exc:  # noqa: BLE001
        try:
            _update_request_status(message.request_id, "notification_failed")
            access_request.status = "notification_failed"
        except Exception:  # noqa: BLE001
            pass
        current_app.logger.warning(
            "Access request notification failed | request_id=%s | status=%s | email_domain=%s | reply_to_set=%s | error_type=%s",
            access_request.id,
            getattr(access_request, "status", "unknown"),
            _email_domain(access_request.email),
            bool(message.reply_to),
            type(exc).__name__,
        )
        return False
