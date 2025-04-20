from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException, status

from ..channels.service import ChannelService

from ..auth.schemas import UserReadSchema

from ..channels.schemas import ChannelReadSchema
from ..channels.service import ChannelService

from .models import CoursesORM
from .repository import CourseRepository
from .schemas import CourseCreateSchema, CourseUpdateSchema, CourseReadSchema
from .exeptions import CoursesHTTPExeptions



#TODO_orm: Занести в БД таблицу, которая содержит в себе информацию о том обучается ли пользователь на курсе
#TODO_redis: Сохранять в кэше данные о курсах, если данные меняются каллбэкать запись
#TODO_service: Метод, для просмотра курсов, на которых пользователь обучается
#TODO_Вынести ошибки в отдельный класс

class CourseService:
    def __init__(self, repository: CourseRepository, exeptions: CoursesHTTPExeptions):
        self.repository = repository
        self.exeptions = exeptions

    async def create(self, course_data: CourseCreateSchema, channel: ChannelReadSchema) -> CourseReadSchema:
        if await self.repository.get_by_name_and_channel_id(channel.id, course_data.name):
            raise self.exeptions.not_found_404()

        new_course = CoursesORM(**course_data.model_dump(), channel_id=channel.id)
        saved_course = await self.repository.create(new_course)
        return CourseReadSchema.model_validate(saved_course)

    async def delete_course(self, course: CourseReadSchema) -> None:
        course_orm = CoursesORM(**course.model_dump())
        await self.repository.delete(course_orm)

    async def update_course(self, course: CourseReadSchema, update_data: CourseUpdateSchema) -> CourseReadSchema:
        course_orm = CoursesORM(**course.model_dump())
        for field, value in update_data.model_dump(exclude_unset=True).items():
            setattr(course_orm, field, value)

        await self.repository.session.commit()
        await self.repository.session.refresh(course_orm)
        return CourseReadSchema.model_validate(course_orm)

    async def get_all_public_courses(self, limit: int = 20) -> List[CourseReadSchema]:
        courses = await self.repository.get_all(limit)
        return [CourseReadSchema.model_validate(c) for c in courses if c.is_public]

    async def get_courses_by_user(self, user_id: UUID, channel_service: ChannelService) -> List[CourseReadSchema]:
        channels = await channel_service.get_user_channels(user_id)
        all_courses = []

        for channel in channels:
            courses = await self.repository.get_by_channel_id(channel.id)
            all_courses.extend(courses)

        return [CourseReadSchema.model_validate(course) for course in all_courses]

    async def get_courses_by_channel(self, channel: ChannelReadSchema) -> List[CourseReadSchema]:
        courses = await self.repository.get_by_channel_id(channel.id)
        return [CourseReadSchema.model_validate(course) for course in courses]
    
    async def get_courses_by_id(self, course_id:UUID) -> CourseReadSchema:
        #Проверка на то, обучается ли пользователь на курсе
        #TODO_service: Внести проверку на is_public поле для курса

        course_orm = self.repository.get_by_id(course_id)
        if course_orm is None: 
            raise self.exeptions.not_found_404()
        
        return CourseReadSchema.model_validate(course_orm)