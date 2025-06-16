from fastapi import Request
from uuid import UUID
from urllib.parse import unquote_plus
from pathlib import Path
from typing import Callable, Awaitable

from ..core.Enums.TypeReferencesEnums import ImageTypeReference
from ..auth.service     import AuthService
from ..channels.service import ChannelService
from ..videos.service   import VideoService
from ..courses.service  import CourseService

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
            #raise PermissionError("Invalid webhook token")

    async def _process(
        self,
        *,
        payload: MinioWebhookPayloadSchema,
        request: Request,
        allowed_kind: ObjectKind,
        handler: ParsedHandler,
    ) -> dict[str, str]:
        """Общий разбор записей MinIO и вызов *handler* для подходящих объектов."""
        self._check_token(request)

        for record in payload.Records:
            try:
                user_id: UUID = UUID(record.s3.bucket.name)
                raw_key: str = unquote_plus(record.s3.object.key)

                upload_key: UploadKey | None = UploadKey.from_s3(
                    user_id=user_id, key=raw_key
                )
                if upload_key is None or upload_key.kind is not allowed_kind:
                    logger.debug("Пропуск: %s", raw_key)
                    continue

                mime_type: str = self._guess_mime(upload_key)
                await handler(upload_key, mime_type)

            except Exception as exc:  # noqa: BLE001
                logger.warning(
                    "Запись webhook пропущена (%s): %s", record, exc, exc_info=True
                )

        return {"status": "ok"}


    @staticmethod
    def _guess_mime(upload_key: UploadKey) -> str:
        """Получить MIME‑тип по расширению и ObjectKind."""
        if upload_key.kind in {
            ObjectKind.PROFILE_AVATAR,
            ObjectKind.CHANNEL_AVATAR,
            ObjectKind.CHANNEL_PREVIEW,
            ObjectKind.COURSE_PREVIEW,
            ObjectKind.VIDEO_PREVIEW,
        }:
            return ImageTypeReference.from_ext(upload_key.ext).mime

        if upload_key.kind is ObjectKind.VIDEO:
            return mimetypes.types_map.get(f".{upload_key.ext}", "video/mp4")

        return "application/octet-stream"



    async def avatar_uploaded(
        self,
        payload: MinioWebhookPayloadSchema,
        request: Request,
        auth_service: AuthService,
    ) -> dict[str, str]:
        """Webhook for user avatar."""

        async def _handler(upload_key: UploadKey, mime_type: str) -> None:
            await auth_service.set_avatar_extension(upload_key.user_id, mime_type)

        return await self._process(
            payload=payload,
            request=request,
            allowed_kind=ObjectKind.PROFILE_AVATAR,
            handler=_handler,
        )

    async def channel_avatar_uploaded(
        self,
        payload: MinioWebhookPayloadSchema,
        request: Request,
        channel_service: ChannelService,
    ) -> dict[str, str]:
        """Webhook for channel avatar."""
        logger.debug("Вызван вебхук channel_avatar_uploaded")

        async def _handler(upload_key: UploadKey, mime_type: str) -> None:
            await channel_service.set_avatar_extension(
                channel_id=upload_key.channel_id, mime=mime_type
            )

        return await self._process(
            payload=payload,
            request=request,
            allowed_kind=ObjectKind.CHANNEL_AVATAR,
            handler=_handler,
        )

    # Previews -----------------------------------------------------------
    async def channel_preview_uploaded(
        self,
        payload: MinioWebhookPayloadSchema,
        request: Request,
        channel_service: ChannelService,
    ) -> dict[str, str]:
        async def _handler(upload_key: UploadKey, mime_type: str) -> None:
            await channel_service.set_preview_extension(
                channel_id=upload_key.channel_id, mime=mime_type
            )

        return await self._process(
            payload=payload,
            request=request,
            allowed_kind=ObjectKind.CHANNEL_PREVIEW,
            handler=_handler,
        )

    async def course_preview_uploaded(
        self,
        payload: MinioWebhookPayloadSchema,
        request: Request,
        course_service: CourseService,
    ) -> dict[str, str]:
        async def _handler(upload_key: UploadKey, mime_type: str) -> None:
            await course_service.set_preview_extension(
                course_id=upload_key.course_id, mime=mime_type
            )

        return await self._process(
            payload=payload,
            request=request,
            allowed_kind=ObjectKind.COURSE_PREVIEW,
            handler=_handler,
        )

    # Videos -------------------------------------------------------------
    async def video_uploaded(
        self,
        payload: MinioWebhookPayloadSchema,
        request: Request,
        video_service: VideoService,
    ) -> dict[str, str]:
        async def _handler(upload_key: UploadKey, mime_type: str) -> None:
            await video_service.process_video_upload(
                owner_id=upload_key.user_id,
                video_id=upload_key.video_id,
                ext=upload_key.ext,
                mime=mime_type,
            )

        return await self._process(
            payload=payload,
            request=request,
            allowed_kind=ObjectKind.VIDEO,
            handler=_handler,
        )

    async def video_preview_uploaded(
        self,
        payload: MinioWebhookPayloadSchema,
        request: Request,
        video_service: VideoService,
    ) -> dict[str, str]:
        async def _handler(upload_key: UploadKey, mime_type: str) -> None:
            await video_service.set_preview_extension(
                video_id=upload_key.video_id,
                mime=mime_type,
            )

        return await self._process(
            payload=payload,
            request=request,
            allowed_kind=ObjectKind.VIDEO_PREVIEW,
            handler=_handler,
        )
