from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException, status

from ..channels.service import ChannelService

from ..auth.schemas import UserReadSchema

from ..channels.schemas import ChannelReadSchema
from ..channels.service import ChannelService

from .models import CoursesORM
from .repository import  CourseStructureRepository


class CourseStructureService:
    def __init__(self, repository: CourseStructureRepository):
        self.repository = repository


    async def create(self): pass