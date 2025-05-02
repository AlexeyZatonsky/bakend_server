from typing import List, Optional
from uuid import UUID


from .schemas import FullStructureReadSchema, FullStructureCreateSchema


from .repository import  CourseStructureRepository


class CourseStructureService:
    def __init__(self, repository: CourseStructureRepository):
        self.repository = repository


    async def create_structure_for_course(course_id: UUID): pass

    async def get_full_structure(course_id: UUID) -> FullStructureReadSchema: pass

    async def open_module(self, course_id: UUID, module_id: UUID): pass

