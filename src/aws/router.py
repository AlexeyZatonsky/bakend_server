from uuid import UUID, uuid4
from pathlib import Path

from fastapi import APIRouter, Depends,status, HTTPException

from ..auth.schemas import UserReadSchema
from ..auth.dependencies import get_current_user

from ..channels.schemas import ChannelReadSchema
from ..channels.dependencies import get_current_channel

from ..videos.schemas import VideoDataReadSchema
from ..videos.dependencies import get_video_service
from ..videos.service import VideoService

from .schemas import (
    UserAvatarUploadRequestSchema, 
    UserAvatarUploadResponseSchema,
    ChannelAvatarUploadRequestSchema,
    ChannelAvatarUploadResponseSchema,
    VideoUploadRequestSchema,
    VideoUploadResponseSchema,
    VideoPreviewUploadRequestSchema,
    VideoPreviewUploadResponseSchema,
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

@router.post(
    "/video",
    response_model=VideoUploadResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Получение ссылки для загрузки видео"
)
async def get_video_upload_url(
    payload: VideoUploadRequestSchema,
    channel: ChannelReadSchema      = Depends(get_current_channel),
    storage: StorageService         = Depends(get_storage_service),
    videos: VideoService            = Depends(get_video_service),
):
    # 1) создаём «черновик» видео в БД (is_public=False) и получаем объект
    video_obj = await videos.create_initial_video(
        user_id=    channel.owner_id,
        channel_id= channel.id,
    )
    video_id = video_obj.id

    # 2) формируем presigned URL
    ext = Path(payload.file_name).suffix.lstrip(".").lower()
    presign = await storage.generate_upload_urls(
        owner_id=        channel.owner_id,
        object_kind=     ObjectKind.VIDEO,
        content_type=    payload.content_type,
        source_filename= payload.file_name,
        access=          AccessPolicy.PUBLIC_READ,
        channel_id=      channel.id,
        video_id=        video_id,
    )

    # 3) возвращаем ответ
    return VideoUploadResponseSchema(
        upload_url= presign["upload_url"],
        key=        presign["key"],
        public_url= presign["public_url"],
        video_id=   video_id,
    )