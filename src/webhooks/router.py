from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, status, Depends
from uuid import UUID
from pathlib import Path
from urllib.parse import unquote_plus

from ..settings.config import WEBHOOK_ENV

from ..auth.service import AuthService
from ..auth.dependencies import get_auth_service

from .service import WebhooksService
from .schemas import MinioWebhookPayloadSchema
from .dependencies import get_webhooks_service

import logging
from ..core.log import configure_logging

logger = logging.getLogger(__name__)
configure_logging()


router = APIRouter(
    prefix="/webhooks/minio",
    tags=["Webhooks"],
    include_in_schema=False,
)




@router.post("/avatar")
async def avatar_uploaded_webhook(
    payload: MinioWebhookPayloadSchema,
    request: Request,
    webhooks_service: WebhooksService = Depends(get_webhooks_service), 
    auth_service: AuthService = Depends(get_auth_service)
):
    logger.debug("Вызван webhook /minio/avatar/POST")

    await webhooks_service.avatar_uploaded(payload, request, auth_service)

