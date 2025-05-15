from uuid import UUID


from fastapi import APIRouter, Depends,status

from ..auth.schemas import UserReadSchema
from ..auth.dependencies import get_current_user

from ..channels.schemas import ChannelReadSchema
from ..channels.dependencies import get_current_channel

from .schemas import (
    UserAvatarUploadRequestSchema, 
    UserAvatarUploadResponseSchema,
    ChannelAvatarUploadRequestSchema,
    ChannelAvatarUploadResponseSchema    
)
from .service  import StorageService
from .dependencies import get_storage_service
from .strategies import ObjectKind
from .access_policies import AccessPolicy

import logging
from ..core.log import configure_logging

logger = logging.getLogger(__name__)
configure_logging()



router = APIRouter(
    prefix="/upload",
    tags=["Storage"]
)



@router.post(
    "/avatar",
    response_model=UserAvatarUploadResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Получение ссылки для загрузки аватара пользователя"
)
async def get_user_profile_preview_url(
    payload: UserAvatarUploadRequestSchema,
    user_data: UserReadSchema = Depends(get_current_user),
    storage_service: StorageService = Depends(get_storage_service) 
):
    logger.debug("Вызван upload/avatar")
    presign = await storage_service.generate_upload_urls(
        owner_id=user_data.id,
        object_kind=ObjectKind.PROFILE_AVATAR,
        content_type=payload.content_type,
        source_filename=payload.file_name,
        access=AccessPolicy.PUBLIC_READ,
    )

    return UserAvatarUploadResponseSchema(
        upload_url=presign["upload_url"], 
        key=presign["key"],
        public_url=presign["public_url"]
    )


@router.post(
    "/channel_avatar",
    response_model=ChannelAvatarUploadResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Получение ссылки для загрузки аватара канала"
)
async def get_channel_upload_url(
    payload: UserAvatarUploadRequestSchema,
    channel_data: ChannelReadSchema = Depends(get_current_channel),
    storage_service: StorageService = Depends(get_storage_service)
):
    logger.debug(f"Вызван upload/channel_avatar для канала {channel_data.id}")
    presign = await storage_service.generate_upload_urls(
        owner_id=channel_data.owner_id,
        object_kind=ObjectKind.CHANNEL_AVATAR,
        content_type=payload.content_type,
        source_filename=payload.file_name,
        access=AccessPolicy.PUBLIC_READ,
        channel_id=channel_data.id
    )

    return ChannelAvatarUploadResponseSchema(
        upload_url=presign["upload_url"], 
        key=presign["key"],
        public_url=presign["public_url"]
    )
