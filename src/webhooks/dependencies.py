
from .service import WebhooksService




async def get_webhooks_service() -> WebhooksService:
    return WebhooksService