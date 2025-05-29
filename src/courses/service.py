import logging
from ..core.log import configure_logging

from typing import List
from uuid import UUID

from ..channels.service import ChannelService
from ..channels.schemas import ChannelReadSchema
from ..channels.service import ChannelService

from ..core.Enums.MIMETypeEnums import ImageMimeEnum
from ..core.Enums.ExtensionsEnums import ImageExtensionsEnum
from ..core.Enums.TypeReferencesEnums import ImageTypeReference

from .models import CoursesORM
from .repository import CourseRepository
from .schemas import CourseCreateSchema, CourseUpdateSchema, CourseReadSchema
from .exceptions import CoursesHTTPExceptions


logger = logging.getLogger(__name__)
configure_logging()




class CourseService:
    def __init__(self, repository: CourseRepository, http_exceptions: CoursesHTTPExceptions):
        self.repository = repository
        self.http_exceptions = http_exceptions

    async def create(self, course_data: CourseCreateSchema, channel: ChannelReadSchema) -> CourseReadSchema:
        if await self.repository.get_by_name_and_channel_id(channel.id, course_data.name):
            raise self.http_exceptions.conflict_409()

        new_course = CoursesORM(**course_data.model_dump(), owner_id=channel.owner_id, channel_id=channel.id)
        saved_course = await self.repository.create(new_course)
        return CourseReadSchema.model_validate(saved_course)

    async def delete_course(self, course_id: UUID) -> None:
        course_orm = await self.repository.get_by_id(course_id)
        await self.repository.delete(course_orm)

    async def update_course(self, course: CourseReadSchema, update_data: CourseUpdateSchema) -> None:
        course_orm = self.repository.get_by_id(course.id)
        if course_orm is None:
            raise self.http_exceptions.not_found_404()
        
        if update_data.name is not None:
            await self.repository.update_name(course.id, update_data.name)

        if update_data.is_public is not None:
            await self.repository.update_is_public(course.id, update_data.is_public)


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
    

    async def get_course_by_id(self, course_id:UUID) -> CourseReadSchema:
        course_orm = await self.repository.get_by_id(course_id)
        if course_orm is None: 
            raise self.http_exceptions.not_found_404()
        
        return CourseReadSchema.model_validate(course_orm)
    
    async def set_preview_extension(
           self,
            course_id: UUID,
            mime: ImageMimeEnum,    
    ) -> None:
        image_type_ref = ImageTypeReference.from_mime(mime) 
        image_type: ImageExtensionsEnum = image_type_ref.ext
        return await self.repository.set_preview_extension(course_id, image_type)

    async def get_my_courses(self, user_id: UUID) -> List[CourseReadSchema]:
        courses = await self.repository.get_by_user_id(user_id)
        
        if not courses:
            raise self.http_exceptions.not_found_404()
        
        return [CourseReadSchema.model_validate(course) for course in courses]

    

