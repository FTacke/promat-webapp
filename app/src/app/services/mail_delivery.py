from __future__ import annotations

import re
import shutil
import smtplib
import ssl
import subprocess
from dataclasses import dataclass
from email.message import EmailMessage
from email.policy import SMTPUTF8
from email.utils import formataddr
from typing import Any

from flask import current_app


_EMAIL_PATTERN = re.compile(
    r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@"
    r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?"
    r"(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+$"
)
_HEADER_FORBIDDEN = {"\r", "\n", "\x00"}


class MailDeliveryError(RuntimeError):
    """Raised when a configured mail backend cannot deliver a message."""


class MailConfigurationError(MailDeliveryError):
    """Raised for missing or unsafe mail configuration."""


class MailValidationError(MailDeliveryError):
    """Raised for unsafe or invalid message data."""


@dataclass(frozen=True)
class MailMessage:
    to_address: str
    subject: str
    body: str
    from_email: str | None = None
    from_name: str | None = None
    reply_to: str | None = None


@dataclass(frozen=True)
class MailDeliveryResult:
    sent: bool
    backend: str
    detail: str | None = None


def email_domain(email: str | None) -> str:
    normalized = (email or "").strip().lower()
    return normalized.partition("@")[2] or "unknown"


def sanitize_header_value(value: str | None, field_name: str, *, required: bool = True) -> str:
    cleaned = (value or "").strip()
    if not cleaned:
        if required:
            raise MailValidationError(f"{field_name} is required.")
        return ""
    if any(character in cleaned for character in _HEADER_FORBIDDEN):
        raise MailValidationError(f"{field_name} contains unsafe header characters.")
    return cleaned


def validate_email_address(value: str | None, field_name: str = "email") -> str:
    email = sanitize_header_value(value, field_name)
    if any(character in email for character in {"<", ">", ",", ";"}):
        raise MailValidationError(f"{field_name} contains unsafe email characters.")
    normalized = email.lower()
    if not _EMAIL_PATTERN.match(normalized):
        raise MailValidationError(f"{field_name} is not a valid email address.")
    return normalized


def configured_from_email(config: Any | None = None) -> str:
    cfg = config or current_app.config
    raw_value = cfg.get("AUTH_MAIL_FROM_EMAIL") or cfg.get("AUTH_ACCESS_REQUEST_FROM_EMAIL")
    return validate_email_address(str(raw_value or ""), "AUTH_MAIL_FROM_EMAIL")


def configured_from_name(config: Any | None = None) -> str:
    cfg = config or current_app.config
    return sanitize_header_value(
        str(cfg.get("AUTH_MAIL_FROM_NAME") or "Pronunciation Matters Administrator"),
        "AUTH_MAIL_FROM_NAME",
        required=False,
    )


def configured_default_reply_to(config: Any | None = None) -> str | None:
    cfg = config or current_app.config
    raw_value = cfg.get("AUTH_MAIL_DEFAULT_REPLY_TO") or cfg.get("AUTH_ACCESS_REQUEST_EMAIL") or ""
    if not str(raw_value or "").strip():
        return None
    return validate_email_address(str(raw_value), "AUTH_MAIL_DEFAULT_REPLY_TO")


def _selected_backend(config: Any) -> str:
    backend = str(config.get("AUTH_MAIL_BACKEND") or "").strip().lower()
    return backend or "smtp"


def _build_email_message(message: MailMessage, config: Any) -> EmailMessage:
    from_email = validate_email_address(message.from_email or configured_from_email(config), "From")
    from_name = sanitize_header_value(
        message.from_name if message.from_name is not None else configured_from_name(config),
        "From display name",
        required=False,
    )
    to_address = validate_email_address(message.to_address, "To")
    subject = sanitize_header_value(message.subject, "Subject")
    body = str(message.body or "")
    if not body:
        raise MailValidationError("Body is required.")

    email_message = EmailMessage(policy=SMTPUTF8)
    email_message["From"] = formataddr((from_name, from_email)) if from_name else from_email
    email_message["To"] = to_address
    email_message["Subject"] = subject
    if message.reply_to:
        email_message["Reply-To"] = validate_email_address(message.reply_to, "Reply-To")
    email_message.set_content(body, charset="utf-8")
    return email_message


def _send_smtp(email_message: EmailMessage, config: Any) -> None:
    host = str(config.get("AUTH_ACCESS_REQUEST_SMTP_HOST") or "").strip()
    if not host:
        raise MailConfigurationError("AUTH_ACCESS_REQUEST_SMTP_HOST is required for smtp mail backend.")

    port = int(config.get("AUTH_ACCESS_REQUEST_SMTP_PORT") or 587)
    username = str(config.get("AUTH_ACCESS_REQUEST_SMTP_USERNAME") or "").strip()
    password = str(config.get("AUTH_ACCESS_REQUEST_SMTP_PASSWORD") or "")
    use_tls = bool(config.get("AUTH_ACCESS_REQUEST_SMTP_USE_TLS"))
    use_ssl = bool(config.get("AUTH_ACCESS_REQUEST_SMTP_USE_SSL"))
    timeout = int(
        config.get("AUTH_ACCESS_REQUEST_SMTP_TIMEOUT_SECONDS")
        or config.get("AUTH_MAIL_TIMEOUT_SECONDS")
        or 10
    )

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


def _send_sendmail(email_message: EmailMessage, config: Any) -> None:
    configured_path = str(config.get("AUTH_MAIL_SENDMAIL_PATH") or "").strip()
    sendmail_path = configured_path or shutil.which("sendmail") or "/usr/sbin/sendmail"
    timeout = int(config.get("AUTH_MAIL_TIMEOUT_SECONDS") or 10)

    result = subprocess.run(
        [sendmail_path, "-i", "-t"],
        input=email_message.as_bytes(policy=SMTPUTF8),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
        check=False,
    )
    if result.returncode != 0:
        raise MailDeliveryError(f"sendmail exited with status {result.returncode}.")


def send_mail(message: MailMessage, *, config: Any | None = None) -> MailDeliveryResult:
    cfg = config or current_app.config
    backend = _selected_backend(cfg)

    if backend == "disabled":
        return MailDeliveryResult(sent=False, backend=backend, detail="disabled")
    if backend not in {"smtp", "sendmail"}:
        raise MailConfigurationError(f"Unsupported mail backend: {backend}")

    test_sender = cfg.get("AUTH_MAIL_SENDER")
    if callable(test_sender):
        test_sender(message)
        return MailDeliveryResult(sent=True, backend=backend, detail="test_sender")

    email_message = _build_email_message(message, cfg)
    if backend == "smtp":
        _send_smtp(email_message, cfg)
        return MailDeliveryResult(sent=True, backend=backend)

    _send_sendmail(email_message, cfg)
    return MailDeliveryResult(sent=True, backend=backend)
