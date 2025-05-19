from fastapi import APIRouter, Depends, UploadFile, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List

from ..auth.schemas import UserReadSchema
from ..auth.dependencies import get_current_user

from .dependencies import get_video_service, validate_video_access
from .service import VideoService
from .schemas import VideoDataReadSchema, VideoDataUpdateSchema

import logging
from ..core.log import configure_logging

logger = logging.getLogger(__name__)
configure_logging()


router = APIRouter(
    prefix='/videos',
    tags=['videos']
)


@router.post("/publish/{video_id}", response_model=VideoDataReadSchema)
async def publish_video(
    video_id: UUID,
    payload: VideoDataUpdateSchema,
    service: VideoService = Depends(get_video_service),
):
    return await service.publish_video(video_id, payload)


@router.patch("", response_model=VideoDataReadSchema)
async def update_video(
    new_data: VideoDataUpdateSchema,
    video_data: VideoDataReadSchema = Depends(validate_video_access),
    service: VideoService = Depends(get_video_service),
):
    return await service.update_video(video_data.id, new_data)

@router.get("/my", response_model=List[VideoDataReadSchema], status_code=200)
async def get_my_videos(
    service: VideoService = Depends(get_video_service),
    user: UserReadSchema = Depends(get_current_user),
):
    return await service.get_videos_by_user_id(user.id)


@router.get("/", response_model=List[VideoDataReadSchema], status_code=200)
async def get_videos(
    service: VideoService = Depends(get_video_service),
    # limit: int = Query(default=20, ge=1, le=100),
    # offset: int = Query(default=0, ge=0),
):
    return await service.get_all_video_datas()
