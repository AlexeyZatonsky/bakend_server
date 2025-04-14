from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException, status

from ..channels.service import ChannelService

from ..auth.schemas import UserReadSchema

from ..channels.schemas import ChannelReadSchema
from ..channels.service import ChannelService

from .models import CoursesORM
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
    
    async def get_courses_by_channel(self, channel_data : ChannelReadSchema) -> List[CourseReadSchema]:
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
        
        #TODO: Удаление материалов курса из aws
        await self.repository.delete(course)


    async def update_course(
    self,
    course_id: UUID,
    update_data: CourseUpdateSchema
    ) -> CourseReadSchema:
        course = await self.repository.get_by_id(course_id)
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")

        for field, value in update_data.model_dump(exclude_unset=True).items():
            setattr(course, field, value)

        await self.repository.session.commit()
        await self.repository.session.refresh(course)

        return CourseReadSchema.model_validate(course)

    
    async def get_all_public_courses(self, limit: int = 20) -> List[CourseReadSchema]:
        all_courses = await self.repository.get_all(limit)
        public_courses = [course for course in all_courses if course.is_public]
        return [CourseReadSchema.model_validate(course) for course in public_courses]

    async def get_courses_by_user(self, user_id: UUID, channel_service: ChannelService) -> List[CourseReadSchema]:
        channels_list: List[ChannelReadSchema] = await channel_service.get_user_channels(user_id)
        courses: list[CoursesORM] = []

        for channel in channels_list:
            courses = await self.repository.get_by_channel_id(channel.id)
            courses.extend(courses)

        return [CourseReadSchema.model_validate(course) for course in courses]
    
    async def get_courses_by_channel(
        self, 
        channel_id: str
    ) -> List[CourseReadSchema]:
        courses = await self.repository.get_by_channel_id(channel_id)
        return [CourseReadSchema.model_validate(course) for course in courses]





class CourseStructureService:
    def __init__(self, repository: CourseStructureRepository):
        self.repository = repository


    async def create(self): pass