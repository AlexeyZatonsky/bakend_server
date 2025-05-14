from fastapi import Request
from uuid import UUID
from urllib.parse import unquote_plus

from ..core.Enums.TypeReferencesEnums import ImageTypeReference, InvalidUploadMimeError
from ..auth.service import AuthService
from ..settings.config import WEBHOOK_ENV

from .schemas import MinioWebhookPayloadSchema

from ..aws.upload_key import UploadKey
from ..aws.strategies import ObjectKind

import logging
from ..core.log import configure_logging

logger = logging.getLogger(__name__)
configure_logging()


class WebhooksService:
    def __init__(self) -> None:
        pass

    async def avatar_uploaded(
        self,
        payload: MinioWebhookPayloadSchema,
        request: Request,
        auth_service: AuthService
    ) -> dict:
        token = request.headers.get("X-Minio-Webhook-Token")
        expected = WEBHOOK_ENV.MINIO_WEBHOOK_TOKEN
        if token != expected:
            logger.debug("Токен Webhook MINIO не валиден: %r != %r", token, expected)
            # raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid webhook token")

        logger.debug("Токен Webhook MINIO Прошёл валидацию")

        for rec in payload.Records:
            try:
                bucket = rec.s3.bucket.name
                user_id = UUID(bucket)

                raw_key = unquote_plus(rec.s3.object.key)
                parsed_key = UploadKey.from_s3(user_id=user_id, key=raw_key)
                if parsed_key is None or parsed_key.kind != ObjectKind.PROFILE_AVATAR:
                    logger.debug("Пропущен ключ: %s", raw_key)
                    continue

                logger.debug(f"Тип полученный из minio: {parsed_key.ext}")
                img_type = ImageTypeReference.from_ext(parsed_key.ext)

                await auth_service.set_avatar_extension(parsed_key.user_id, img_type.mime)
                logger.debug("set_avatar_extension(%s, %s) выполнен", parsed_key.user_id, img_type.mime)

            except Exception as e:
                logger.warning("Webhook record skipped: %r (%s)", rec, e)
                raise

        return {"status": "ok"}
