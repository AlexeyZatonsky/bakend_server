from fastapi import Request
from uuid import UUID
from urllib.parse import unquote_plus
from pathlib import Path
from typing import Callable, Awaitable

from ..core.Enums.TypeReferencesEnums import ImageTypeReference
from ..auth.service     import AuthService
from ..channels.service import ChannelService
from ..videos.service   import VideoService

from ..settings.config  import WEBHOOK_ENV
from .schemas           import MinioWebhookPayloadSchema
from ..aws.upload_key   import UploadKey
from ..aws.strategies   import ObjectKind

import logging
from ..core.log import configure_logging

logger = logging.getLogger(__name__)
configure_logging()

ParsedHandler = Callable[[UploadKey, str], Awaitable[None]]


class WebhooksService:
    # ---------- helpers ----------
    @staticmethod
    def _check_token(request: Request) -> None:
        if request.headers.get("X-Minio-Webhook-Token") != WEBHOOK_ENV.MINIO_WEBHOOK_TOKEN:
            logger.debug("Неверный X-Minio-Webhook-Token")
            raise PermissionError("Invalid webhook token")

    async def _process(
        self,
        *,
        payload: MinioWebhookPayloadSchema,
        request: Request,
        allowed_kind: ObjectKind,
        handler: ParsedHandler,
    ) -> dict:
        self._check_token(request)

        for rec in payload.Records:
            try:
                user_id = UUID(rec.s3.bucket.name)
                raw_key = unquote_plus(rec.s3.object.key)

                parsed = UploadKey.from_s3(user_id=user_id, key=raw_key)
                if parsed is None or parsed.kind != allowed_kind:
                    logger.debug("Пропуск: %s", raw_key)
                    continue

                mime = ImageTypeReference.from_ext(parsed.ext).mime if parsed.kind in {
                    ObjectKind.PROFILE_AVATAR,
                    ObjectKind.CHANNEL_AVATAR,
                } else f"video/{parsed.ext}"  # простая эвристика для видео

                await handler(parsed, mime)

            except Exception as exc:
                logger.warning("Запись webhook пропущена (%s): %s", rec, exc)

        return {"status": "ok"}

    # ---------- avatar ----------
    async def avatar_uploaded(self, payload, request, auth_service: AuthService):
        return await self._process(
            payload=payload,
            request=request,
            allowed_kind=ObjectKind.PROFILE_AVATAR,
            handler=lambda k, m: auth_service.set_avatar_extension(k.user_id, m),
        )

    async def channel_avatar_uploaded(self, payload, request, channel_service: ChannelService):
        async def _h(k: UploadKey, mime: str):
            await channel_service.set_avatar_extension(channel_id=k.channel_id, mime=mime)

        return await self._process(
            payload=payload,
            request=request,
            allowed_kind=ObjectKind.CHANNEL_AVATAR,
            handler=_h,
        )

    # ---------- video ----------
    async def video_uploaded(self, payload, request, video_service: VideoService):
        async def _h(k: UploadKey, mime: str):
            await video_service.process_video_upload(
                owner_id=k.user_id,
                video_id=k.video_id,
                ext=k.ext,
                mime=mime,
            )

        return await self._process(
            payload=payload,
            request=request,
            allowed_kind=ObjectKind.VIDEO,
            handler=_h,
        )

    async def video_preview_uploaded(self, payload, request, video_service: VideoService):
        async def _h(k: UploadKey, mime: str):
            await video_service.process_preview_upload(
                owner_id=k.user_id,
                video_id=k.video_id,
                ext=k.ext,
                mime=mime,
            )

        return await self._process(
            payload=payload,
            request=request,
            allowed_kind=ObjectKind.VIDEO_PREVIEW,
            handler=_h,
        )
