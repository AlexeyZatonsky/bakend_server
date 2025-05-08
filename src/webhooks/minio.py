from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, status
from uuid import UUID
from pathlib import Path
from urllib.parse import unquote_plus

from ..settings.config import WEBHOOK_ENV

from ..auth.dependencies import set_image_extension
from ..core.Enums.TypeReferencesEnums import ImageTypeReferenceEnum, InvalidUploadMimeError

import logging
from ..core.log import configure_logging

logger = logging.getLogger(__name__)
configure_logging()


router = APIRouter(
    prefix="/webhooks/minio",
    tags=["Webhooks"],
    include_in_schema=False,
)


@router.post(
    "/avatar",
    #status_code=status.HTTP_204_NO_CONTENT, 
)
async def avatar_uploaded_webhook(
    request: Request,
) -> None:
    
    logger.debug(f"Вызван webhook /minio/avatar/POST")

    if request.headers.get("X-Minio-Webhook-Token") != WEBHOOK_ENV.MINIO_WEBHOOK_TOKEN:
        logger.debug("Токен Webhook MINIO не валиден")
        raise HTTPException(status_code=403, detail="Invalid webhook token")

    logger.debug("Токен Webhook MINIO Прошёл валидацию")


    event = await request.json()        
    logger.debug(f"Minio event {event}")
    records = event.get("Records", [])

    for rec in records:
        try:
            key_raw: str = rec["s3"]["object"]["key"]      
            key = unquote_plus(key_raw)                    
            parts = key.split("/", 2)                    

            user_id = UUID(parts[0])                       
            if parts[1] != "other":
                continue                                 

            ext = Path(parts[-1]).suffix.lstrip(".").lower()  
            img_type = ImageTypeReferenceEnum.from_ext(ext)

            await set_image_extension(user_id, img_type.ext)

        except (KeyError, ValueError, InvalidUploadMimeError):
            logger.warning("Webhook record skipped: %s", rec)
            continue
