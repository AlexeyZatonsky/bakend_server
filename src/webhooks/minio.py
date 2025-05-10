from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, status, Depends
from uuid import UUID
from pathlib import Path
from urllib.parse import unquote_plus

from ..settings.config import WEBHOOK_ENV

from ..auth.service import AuthService
from ..auth.dependencies import get_auth_service
from ..core.Enums.TypeReferencesEnums import ImageTypeReferenceEnum, InvalidUploadMimeError

from .schemas import MinioWebhookPayloadSchema

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
    auth_service: AuthService = Depends(get_auth_service)
):
    logger.debug("Вызван webhook /minio/avatar/POST")

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

            key = unquote_plus(rec.s3.object.key)
            prefix, filename = key.split("/", 1)
            if prefix != "other":
                continue

            ext = Path(filename).suffix.lstrip(".").lower()

            logger.debug(f"Тип полученный из minio  {ext}")
            img_type = ImageTypeReferenceEnum.from_ext(ext)

            await auth_service.set_avatar_extension(user_id, img_type.mime)
            logger.debug("set_image_extension(%s, %s) выполнен", user_id, img_type)

        except Exception as e:
            logger.warning("Webhook record skipped: %r (%s)", rec, e)
            raise

    return {"status": "ok"}

