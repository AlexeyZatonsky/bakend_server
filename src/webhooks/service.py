from fastapi import Request
from uuid import UUID
from urllib.parse import unquote_plus
from typing import Callable, Awaitable

from ..core.Enums.TypeReferencesEnums import ImageTypeReference, InvalidUploadMimeError

from ..auth.service import AuthService
from ..channels.service import ChannelService

from ..settings.config import WEBHOOK_ENV

from .schemas import MinioWebhookPayloadSchema

from ..aws.upload_key import UploadKey
from ..aws.strategies import ObjectKind

import logging
from ..core.log import configure_logging

logger = logging.getLogger(__name__)
configure_logging()


ParsedHandler = Callable[[UploadKey, str], Awaitable[None]]

class WebhooksService:
    def __init__(self) -> None:
        pass

    def check_token(self, request: Request) -> None:
        token = request.headers.get("X-Minio-Webhook-Token")
        expected = WEBHOOK_ENV.MINIO_WEBHOOK_TOKEN
        if token != expected:
            logger.debug("Токен Webhook MINIO не валиден: %r != %r", token, expected)
            # raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid webhook token")
        logger.debug("Токен Webhook MINIO прошёл валидацию")


    async def process_webhook(
        self,
        *,
        payload: MinioWebhookPayloadSchema,
        request: Request,
        allowed_kind: ObjectKind,
        handler: ParsedHandler
    ) -> dict:
        self.check_token(request)

        for rec in payload.Records:
            try:
                bucket = rec.s3.bucket.name
                user_id = UUID(bucket)
                raw_key = unquote_plus(rec.s3.object.key)

                parsed_key = UploadKey.from_s3(user_id=user_id, key=raw_key)
                if parsed_key is None or parsed_key.kind != allowed_kind:
                    logger.debug("Пропущен ключ: %s", raw_key)
                    continue

                img_type = ImageTypeReference.from_ext(parsed_key.ext)
                await handler(parsed_key, img_type.mime)

            except Exception as e:
                logger.warning("Webhook record skipped: %r (%s)", rec, e)
                raise

        return {"status": "ok"}

    async def avatar_uploaded(
        self,
        payload: MinioWebhookPayloadSchema,
        request: Request,
        auth_service: AuthService
    ) -> dict:
        return await self.process_webhook(
            payload=payload,
            request=request,
            allowed_kind=ObjectKind.PROFILE_AVATAR,
            handler=lambda key, mime: auth_service.set_avatar_extension(key.user_id, mime)
        )


    async def channel_avatar_uploaded(
        self,
        payload: MinioWebhookPayloadSchema,
        request: Request,
        channel_service: ChannelService
    ) -> dict:
        async def handle_channel_avatar(key: UploadKey, mime: str):
            assert key.channel_id is not None, f"Отсутствует channel_id в ключе: {key.key}"
            await channel_service.set_avatar_extension(channel_id=key.channel_id, mime=mime)

        return await self.process_webhook(
            payload=payload,
            request=request,
            allowed_kind=ObjectKind.CHANNEL_AVATAR,
            handler=handle_channel_avatar
        )


