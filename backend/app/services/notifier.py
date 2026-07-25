from __future__ import annotations

import smtplib
from email.message import EmailMessage

from app.config import get_settings


def send_email(subject: str, body: str, recipient: str | None = None) -> tuple[str, str | None]:
    settings = get_settings()
    if not settings.smtp_enabled:
        return "skipped", None

    message = EmailMessage()
    message["From"] = "SitePulse <noreply@sitepulse.local>"
    message["To"] = recipient or settings.default_notification_email
    message["Subject"] = subject
    message.set_content(body)

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as smtp:
            if settings.smtp_use_tls:
                smtp.starttls()
            if settings.smtp_username and settings.smtp_password:
                smtp.login(settings.smtp_username, settings.smtp_password)
            smtp.send_message(message)
        return "sent", None
    except OSError as exc:
        return "failed", str(exc)
