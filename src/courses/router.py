from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from ..database import get_async_session
from ..auth.dependencies import get_current_user
from ..auth.schemas import UserReadSchema

from .schemas import (
    CourseBaseSchema, CourseReadSchema, CourseCreateSchema, CourseUpdateSchema,
    FullCourseStructureSchema, CourseModuleSchema, CourseSubModuleSchema,
    CourseLessonSchema, LessonHWSchema
)

router = APIRouter(
    prefix="/courses",
    tags=["Courses"]
)