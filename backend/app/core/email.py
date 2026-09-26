import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import settings

logger = logging.getLogger(__name__)


def send_email(to: str, subject: str, text: str, html: str | None = None) -> bool:
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        logger.warning("SMTP yapılandırılmamış, e-posta gönderilmedi: %s -> %s", subject, to)
        if settings.ENV == "dev":
            logger.info("E-posta içeriği (dev): %s", text[:500])
        return False

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = f"{settings.EMAIL_FROM_NAME} <{settings.SMTP_USER}>"
    message["To"] = to
    message.attach(MIMEText(text, "plain", "utf-8"))
    if html:
        message.attach(MIMEText(html, "html", "utf-8"))

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_USER, [to], message.as_string())
        return True
    except smtplib.SMTPException:
        logger.exception("E-posta gönderilemedi: %s -> %s", subject, to)
        return False
