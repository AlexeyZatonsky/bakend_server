from typing import List
from uuid import UUID

from fastapi import HTTPException, status

from ..courses.models import CoursesORM
from ..channels.schemas import ChannelReadSchema

from .repository import CourseRepository, CourseStructureRepository
from .schemas import (
    CourseCreateSchema, CourseUpdateSchema, CourseReadSchema


)





class CourseService:
    def __init__(self, repository: CourseRepository):
        self.repository = repository

    async def create(
            self, 
            course_data: CourseCreateSchema, 
            channel: ChannelReadSchema
        ) -> CourseReadSchema | HTTPException:

        if await self.repository.get_by_channel_id(channel.id) is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="There's already a course with that name on your channel."
            )
        
        new_course = CoursesORM(**course_data.model_dump(), channel_id=channel.id)

        saved_course = await self.repository.create(new_course)

        return CourseReadSchema.model_validate()

    async def get_all(self, limit: int = 20) -> List[CourseReadSchema]:
        courses = await self.repository.get_all(limit)
        return [CourseReadSchema.model_validate(course) for course in courses]





class CourseStructureService:
    def __init__(self, repository: CourseStructureRepository):
        self.repository = repository


    async def create(self): pass