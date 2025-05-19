from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from ..database import get_async_session

from ..auth.schemas import UserReadSchema
from ..auth.dependencies import get_current_user

from .service import VideoService
from .repository import VideoRepository
from .exceptions import VideoHTTPExceptions
from .schemas import VideoDataReadSchema

async def get_video_service(
    session: AsyncSession = Depends(get_async_session)
) -> VideoService:
    repository = VideoRepository(session)
    http_exceptions = VideoHTTPExceptions()
    return VideoService(repository, http_exceptions)




async def validate_video_access(
    video_id: UUID,
    user: UserReadSchema = Depends(get_current_user),
    service: VideoService = Depends(get_video_service),
) -> VideoDataReadSchema:
    video = await service.repository.video_data_repo.get_by_id(video_id)
    if not video:
        raise service.http_exceptions.not_found_404()
    
    video_data = VideoDataReadSchema.model_validate(video)
    
    if video_data.user_id != user.id:
        raise service.http_exceptions.forbidden_403()
    
    return video_data
