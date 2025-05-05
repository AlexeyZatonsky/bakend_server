from uuid import UUID
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession


from ..database import get_async_session

from ..auth.dependencies import get_current_user
from ..auth.schemas import UserReadSchema

from ..permissions.service import PermissionsService
from ..permissions.dependencies import get_permissions_service

from ..channels.dependencies import get_channel_service
from ..channels.service import ChannelService

from .exceptions import CourseStructureHTTPExceptions
from .repository import CourseStructureRepository
from .service import CourseStructureService




async def get_course_structure_service(session: AsyncSession = Depends(get_async_session)) -> CourseStructureService:
    repository = CourseStructureRepository(session)
    exceptions = CourseStructureHTTPExceptions()
    return CourseStructureService(repository, exceptions)
