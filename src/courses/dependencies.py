from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_async_session

from ..auth.dependencies import get_current_user
from ..auth.schemas import UserReadSchema

from .repository import CourseRepository, CourseStructureRepository
from .service import CourseService, CourseStructureService





def get_course_service(session: AsyncSession = Depends(get_async_session)) -> CourseService:
    repository = CourseRepository(session)
    return CourseService(repository)

def get_course_structure_service(session: AsyncSession = Depends(get_async_session)) -> CourseStructureService:
    repository = CourseStructureRepository(session)
    return CourseStructureService(repository)
