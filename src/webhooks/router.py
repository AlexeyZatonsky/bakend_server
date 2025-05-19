from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, status, Depends
from uuid import UUID
from pathlib import Path
from urllib.parse import unquote_plus

from ..settings.config import WEBHOOK_ENV

from ..auth.service import AuthService
from ..auth.dependencies import get_auth_service

from ..channels.service import ChannelService
from ..channels.dependencies import get_channel_service

from ..videos.service import VideoService
from ..videos.dependencies import get_video_service

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



@router.post("/channel_avatar")
async def channel_avatar_uploaded_webhook(
    payload: MinioWebhookPayloadSchema,
    request: Request,
    webhooks_service: WebhooksService = Depends(get_webhooks_service),
    channel_service: ChannelService = Depends(get_channel_service),
):
    await webhooks_service.channel_avatar_uploaded(payload, request, channel_service)
    logger.debug("Вызван вебхук channel_avata")

@router.post("/video")
async def video_uploaded_webhook(
    payload: MinioWebhookPayloadSchema,
    request: Request,
    ws: WebhooksService = Depends(get_webhooks_service),
    vs: VideoService    = Depends(get_video_service),
):
    return await ws.video_uploaded(payload, request, vs)


@router.post("/video_preview")
async def video_preview_uploaded_webhook(
    payload: MinioWebhookPayloadSchema,
    request: Request,
    ws: WebhooksService = Depends(get_webhooks_service),
    vs: VideoService    = Depends(get_video_service),
):
    return await ws.video_preview_uploaded(payload, request, vs)
