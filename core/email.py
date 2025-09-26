from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from core.config import config
import logging
import asyncio

logger = logging.getLogger(__name__)

def get_mail_conf():
    if not config.SMTP_ENABLED:
        logger.warning("SMTP отключен, отправка писем невозможна")
        return None
    return ConnectionConfig(
        MAIL_USERNAME=config.SMTP_USER,
        MAIL_PASSWORD=config.SMTP_PASSWORD,
        MAIL_FROM=config.SMTP_FROM,
        MAIL_PORT=config.SMTP_PORT,
        MAIL_SERVER=config.SMTP_HOST,
        MAIL_STARTTLS=(config.SMTP_PORT == 587),
        MAIL_SSL_TLS=(config.SMTP_PORT == 465),
        USE_CREDENTIALS=True,
        VALIDATE_CERTS=True
    )

fm = FastMail(get_mail_conf()) if config.SMTP_ENABLED else None

async def send_email(to_email: str, subject: str, body: str):
    """Асинхронная отправка email через SMTP."""
    if not config.SMTP_ENABLED or fm is None:
        logger.info(f"Отправка письма на {to_email} отклонена, так как SMTP отключен")
        return
    logger.info(f"Начало отправки письма на {to_email}, тема: {subject}")
    message = MessageSchema(
        subject=subject,
        recipients=[to_email],
        body=body,
        subtype=MessageType.plain
    )
    try:
        await fm.send_message(message)
        logger.info(f"Письмо успешно отправлено на {to_email}")
    except Exception as e:
        logger.error(f"Ошибка при отправке письма на {to_email}: {str(e)}", exc_info=True)
        raise