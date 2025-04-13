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
    return CourseService(CourseRepository(session), CourseStructureRepository(session))


def get_channel_service(session: AsyncSession = Depends(get_async_session)) -> ChannelService:
    return ChannelService(ChannelRepository(session))


@router.post("", response_model=CourseReadSchema, status_code=201)
async def create_course(
    channel_id: str,
    course_data: CourseCreateSchema,
    user: UserReadSchema = Depends(get_current_user),
    course_service: CourseService = Depends(get_course_service),
    channel_service: ChannelService = Depends(get_channel_service)
):
    # Получаем канал и валидируем владельца
    channel: ChannelReadSchema = await channel_service.get_by_id(channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")

    if channel.owner_id != user.id:
        raise HTTPException(status_code=403, detail="You are not the owner of this channel")

    # Создание курса
    return await course_service.create(course_data, channel)