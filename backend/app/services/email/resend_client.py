import httpx

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)

RESEND_API_URL = "https://api.resend.com/emails"


async def send_email(to: str, subject: str, html: str) -> None:
    """Envia um email transacional via Resend.

    Sem RESEND_API_KEY configurada (ex.: ambiente de dev), o envio é apenas
    logado — não falha a request que disparou o email (ex.: esqueci senha
    não deve quebrar por falta de configuração de email)."""
    settings = get_settings()

    if not settings.resend_api_key:
        logger.warning("resend_api_key_not_configured", to=to, subject=subject)
        return

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            RESEND_API_URL,
            headers={"Authorization": f"Bearer {settings.resend_api_key}"},
            json={
                "from": settings.resend_from_email,
                "to": [to],
                "subject": subject,
                "html": html,
            },
        )

    if response.status_code >= 400:
        logger.error("resend_send_failed", status=response.status_code, body=response.text)
        response.raise_for_status()

    logger.info("resend_email_sent", to=to, subject=subject)
