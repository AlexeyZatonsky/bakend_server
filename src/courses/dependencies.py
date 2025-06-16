import logging
from ..core.log import configure_logging

from uuid import UUID
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_async_session


from ..auth.schemas import UserReadSchema
from ..auth.dependencies import get_current_user

from ..channels.dependencies import get_current_channel, get_channel_service
from ..channels.schemas import ChannelReadSchema
from ..channels.service import ChannelService


from .repository import CourseRepository
from .service import CourseService
from .schemas import CourseReadSchema
from .exceptions import CoursesHTTPExceptions

logger = logging.getLogger(__name__)
configure_logging()




async def get_course_service(session: AsyncSession = Depends(get_async_session)) -> CourseService:
    repository = CourseRepository(session)
    http_exceptions = CoursesHTTPExceptions()
    return CourseService(repository, http_exceptions)


async def get_current_course_with_owner_validate(
    course_id: UUID,
    user: UserReadSchema               = Depends(get_current_user),
    course_service: CourseService      = Depends(get_course_service),
    channel_service: ChannelService    = Depends(get_channel_service),
) -> CourseReadSchema:
    
    course_orm = await course_service.repository.get_by_id(course_id)
    if not course_orm:
        raise course_service.http_exceptions.not_found_404()
    
    channel_orm = await channel_service.repository.get_by_id(course_orm.channel_id)
    if not channel_orm:
        raise channel_service.http_exceptions.not_found_404()

    if channel_orm.owner_id != user.id:
        raise course_service.http_exceptions.forbidden_403()

    logger.debug("get_current_course_with_owner_validate - SUCCESSFULL")

    return CourseReadSchema.model_validate(course_orm)


async def course_is_open(
    course_id: UUID,
    course_service: CourseService = Depends(get_course_service),
) -> bool:
    """
    Проверяет, что курс **открыт** 
    """
    logger.debug("course_is_open")

    # course_DTO = await course_service.get_courses_by_id(course_id)
    # if course_DTO.is_public == False:
    #     return False

    return True