from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from ..database import get_async_session

from ..auth.dependencies import get_current_user
from ..auth.schemas import UserReadSchema

from ..channels.service import ChannelService
from ..channels.repository import ChannelRepository
from ..channels.schemas import ChannelReadSchema

from .repository import CourseRepository, CourseStructureRepository
from .services import CourseService, CourseStructureService

from .schemas import (
    CourseCreateSchema, CourseUpdateSchema, CourseReadSchema


)

router = APIRouter(
    prefix="/channels/{channel_id}/courses",
    tags=["Courses"]
)

def get_course_service(session: AsyncSession = Depends(get_async_session)) -> CourseService:
    repository = CourseRepository(session)
    return CourseService(repository)

def get_course_structure_service(session: AsyncSession = Depends(get_async_session)) -> CourseStructureService:
    repository = CourseStructureRepository(session)
    return CourseStructureService(repository)


def get_channel_service(session: AsyncSession = Depends(get_async_session)) -> ChannelService:
    repository = ChannelRepository(session)
    return ChannelService(repository)


@router.post("", response_model=CourseReadSchema, status_code=status.HTTP_201_CREATED)
async def create_course(
    channel_id: str,
    course_data: CourseCreateSchema,
    user_data: UserReadSchema = Depends(get_current_user),
    course_service: CourseService = Depends(get_course_service),
    channel_service: ChannelService = Depends(get_channel_service),
):
    channel_data = await channel_service.validate_owner(channel_id, user_data.id)
    return await course_service.create(course_data, channel_data, user_data)
