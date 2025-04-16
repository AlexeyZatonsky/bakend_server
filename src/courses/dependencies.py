from uuid import UUID
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_async_session


from ..channels.dependencies import get_current_channel
from ..channels.schemas import ChannelReadSchema

from .repository import CourseRepository
from .service import CourseService
from .schemas import CourseReadSchema




async def get_course_service(session: AsyncSession = Depends(get_async_session)) -> CourseService:
    repository = CourseRepository(session)
    return CourseService(repository)


async def get_current_course(
    course_id: UUID,
    channel: ChannelReadSchema = Depends(get_current_channel),
    course_service: CourseService = Depends(get_course_service),
) -> CourseReadSchema:
    course = await course_service.repository.get_by_id(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    if course.channel_id != channel.id:
        raise HTTPException(status_code=403, detail="This course does not belong to this channel")

    return CourseReadSchema.model_validate(course)
