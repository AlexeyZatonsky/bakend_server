from uuid import UUID
from pathlib import Path

from fastapi import APIRouter, Depends, status

from ..auth.schemas import UserReadSchema
from ..auth.dependencies import get_current_user

from ..channels.schemas import ChannelReadSchema
from ..channels.dependencies import get_current_channel

from ..videos.dependencies import get_video_service, validate_video_access
from ..videos.service import VideoService
from ..videos.schemas import VideoDataReadSchema

from ..courses.schemas import CourseReadSchema
from ..courses.dependencies import get_current_course_with_owner_validate

from .schemas import (
    UserAvatarUploadRequestSchema, UserAvatarUploadResponseSchema,
    ChannelAvatarUploadRequestSchema, ChannelAvatarUploadResponseSchema,
    ChannelPreviewUploadRequestSchema, ChannelPreviewUploadResponseSchema,
    CoursePreviewUploadRequestSchema, CoursePreviewUploadResponseSchema,
    VideoUploadRequestSchema, VideoUploadResponseSchema,
    VideoPreviewUploadRequestSchema, VideoPreviewUploadResponseSchema,
)
from .service import StorageService
from .dependencies import get_storage_service
from .strategies import ObjectKind
from .access_policies import AccessPolicy

router = APIRouter(prefix="/upload", tags=["Storage"])


@router.post("/avatar", response_model=UserAvatarUploadResponseSchema, status_code=status.HTTP_201_CREATED)
async def upload_user_avatar(
    payload: UserAvatarUploadRequestSchema,
    user: UserReadSchema = Depends(get_current_user),
    storage: StorageService = Depends(get_storage_service),
):
    presign = await storage.generate_upload_urls(
        owner_id=user.id,
        object_kind=ObjectKind.PROFILE_AVATAR,
        content_type=payload.content_type,
        source_filename=payload.file_name,
        access=AccessPolicy.PUBLIC_READ,
    )
    return UserAvatarUploadResponseSchema(**presign)


@router.post("/channel_avatar", response_model=ChannelAvatarUploadResponseSchema, status_code=status.HTTP_201_CREATED)
async def upload_channel_avatar(
    payload: ChannelAvatarUploadRequestSchema,
    channel: ChannelReadSchema = Depends(get_current_channel),
    storage: StorageService = Depends(get_storage_service),
):
    presign = await storage.generate_upload_urls(
        owner_id=channel.owner_id,
        object_kind=ObjectKind.CHANNEL_AVATAR,
        content_type=payload.content_type,
        source_filename=payload.file_name,
        access=AccessPolicy.PUBLIC_READ,
        channel_id=channel.id,
    )
    return ChannelAvatarUploadResponseSchema(**presign)


@router.post("/channel_preview", response_model=ChannelPreviewUploadResponseSchema, status_code=status.HTTP_201_CREATED)
async def upload_channel_preview(
    payload: ChannelPreviewUploadRequestSchema,
    channel: ChannelReadSchema = Depends(get_current_channel),
    storage: StorageService = Depends(get_storage_service),
):
    presign = await storage.generate_upload_urls(
        owner_id=channel.owner_id,
        object_kind=ObjectKind.CHANNEL_PREVIEW,
        content_type=payload.content_type,
        source_filename=payload.file_name,
        access=AccessPolicy.PUBLIC_READ,
        channel_id=channel.id,
    )
    return ChannelPreviewUploadResponseSchema(**presign)


@router.post("/course_preview", response_model=CoursePreviewUploadResponseSchema, status_code=status.HTTP_201_CREATED)
async def upload_course_preview(
    payload: CoursePreviewUploadRequestSchema,
    course: CourseReadSchema = Depends(get_current_course_with_owner_validate),
    storage: StorageService = Depends(get_storage_service),
):
    presign = await storage.generate_upload_urls(
        owner_id=course.owner_id,
        object_kind=ObjectKind.COURSE_PREVIEW,
        content_type=payload.content_type,
        source_filename=payload.file_name,
        access=AccessPolicy.PUBLIC_READ,
        channel_id=course.channel_id,
        course_id=course.id
    )
    return CoursePreviewUploadResponseSchema(**presign)


@router.post("/video", response_model=VideoUploadResponseSchema, status_code=status.HTTP_201_CREATED)
async def upload_video(
    payload: VideoUploadRequestSchema,
    channel: ChannelReadSchema = Depends(get_current_channel),
    videos: VideoService = Depends(get_video_service),
    storage: StorageService = Depends(get_storage_service),
):
    video_obj = await videos.create_initial_video(user_id=channel.owner_id, channel_id=channel.id)
    presign = await storage.generate_upload_urls(
        owner_id=channel.owner_id,
        object_kind=ObjectKind.VIDEO,
        content_type=payload.content_type,
        source_filename=payload.file_name,
        access=AccessPolicy.PUBLIC_READ,
        channel_id=channel.id,
        video_id=video_obj.id,
    )
    return VideoUploadResponseSchema(video_id=video_obj.id, **presign)


@router.post("/video_preview", response_model=VideoPreviewUploadResponseSchema, status_code=status.HTTP_201_CREATED)
async def upload_video_preview(
    payload: VideoPreviewUploadRequestSchema,
    video_data: VideoDataReadSchema = Depends(validate_video_access),
    storage: StorageService = Depends(get_storage_service),
):
    presign = await storage.generate_upload_urls(
        owner_id=video_data.user_id,
        object_kind=ObjectKind.VIDEO_PREVIEW,
        content_type=payload.content_type,
        source_filename=payload.file_name,
        access=AccessPolicy.PUBLIC_READ,
        channel_id=video_data.channel_id,
        video_id=video_data.id,
    )
    return VideoPreviewUploadResponseSchema(**presign)
