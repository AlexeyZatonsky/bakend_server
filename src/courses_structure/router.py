from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID

from ..auth.dependencies import get_current_user
from ..auth.schemas import UserReadSchema


from .dependencies import get_course_structure_service
from .service import CourseStructureService




router = APIRouter(
    tags=["CourseStructure"]
)


