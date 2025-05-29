from typing import List, Optional
from uuid import UUID

from .exceptions import CourseStructureHTTPExceptions
from .schemas import FullStructureReadSchema, FullStructureCreateSchema
from .models import CoursesStructureORM
from .repository import  CourseStructureRepository




class CourseStructureService:
    def __init__(self, repository: CourseStructureRepository, 
                 http_exceptions: CourseStructureHTTPExceptions
    ): 
        self.repository = repository
        self.http_exceptions = http_exceptions


    async def create_structure_for_course(
        self,
        course_id: UUID,
        body: FullStructureCreateSchema
    ) -> FullStructureReadSchema:
        orm_obj = CoursesStructureORM(
            id=course_id,
            structure=body.model_dump(mode="python")  # raw dict → JSONB
        )
        if await self.repository.get_by_id(course_id) != None:
            raise self.http_exceptions.conflict_409()

        created = await self.repository.create(orm_obj)
        return FullStructureReadSchema(**created.__dict__)

    async def get_full_structure(
        self,
        course_id: UUID
    ) -> FullStructureReadSchema:
        orm_obj = await self.repository.get_by_id(course_id)

        if not orm_obj:
            raise self.http_exceptions.not_found_404()
        
        return FullStructureReadSchema(**orm_obj.__dict__)
    
    async def update_structure_for_course(
        self,
        course_id: UUID,
        body: FullStructureCreateSchema
    ) -> FullStructureReadSchema:
        orm_obj = CoursesStructureORM(
            id=course_id,
            structure=body.model_dump(mode="python")  # raw dict → JSONB
        )
        if await self.repository.get_by_id(course_id) != None:
            raise self.http_exceptions.conflict_409()

        created = await self.repository.update_structure(orm_obj)
        return FullStructureReadSchema(**created.__dict__)

    async def open_module(self, course_id: UUID, module_id: UUID): pass

