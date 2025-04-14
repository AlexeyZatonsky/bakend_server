from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException, status

from ..auth.schemas import UserReadSchema

from ..courses.models import CoursesORM
from ..channels.schemas import ChannelReadSchema

from .repository import CourseRepository, CourseStructureRepository
from .schemas import (
    CourseCreateSchema, CourseUpdateSchema, CourseReadSchema


)



#TODO: Метод, для просмотра курсов, на которых пользователь обучается

class CourseService:
    def __init__(self, repository: CourseRepository):
        self.repository = repository
   

    async def create(
            self, 
            course_data: CourseCreateSchema, 
            channel_data: ChannelReadSchema,
            user_data: UserReadSchema,
        ) -> CourseReadSchema | HTTPException:


        if await self.repository.get_by_name_and_channel_id(channel_data.id, course_data.name) is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="There's already a course with that name on your channel."
            )
        
        #TODO: подключение aws - создавать директорию для курса.
        
        new_course = CoursesORM(**course_data.model_dump(), channel_id=channel_data.id)
        saved_course = await self.repository.create(new_course)
        return CourseReadSchema.model_validate(saved_course)


    async def get_all(self, limit: int = 20) -> List[CourseReadSchema]:
        courses = await self.repository.get_all(limit)
        return [CourseReadSchema.model_validate(course) for course in courses]
    
    async def get_courses_by_cahnnel(self, channel_data : ChannelReadSchema) -> List[CourseReadSchema]:
        courses = await self.repository.get_by_channel_id(channel_data.id)
        return[CourseReadSchema.model_validate(course) for course in courses]

    async def delete_course(
        self, 
        user_data: UserReadSchema, 
        channel_data: ChannelReadSchema, 
        course_id: UUID
    ) -> None:
        

        if user_data.id != channel_data.owner_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to delete this course."
            )


        course = await self.repository.get_by_id(course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )

        if course.channel_id != channel_data.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This course does not belong to the specified channel."
            )

        await self.repository.delete(course)
        





class CourseStructureService:
    def __init__(self, repository: CourseStructureRepository):
        self.repository = repository


    async def create(self): pass