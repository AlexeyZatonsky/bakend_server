from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID

from ..courses.dependencies import get_current_course
from ..courses.schemas import CourseReadSchema

from .dependencies import get_permissions_service
from .schemas import PermissionCreateSchema, PermissionReadSchema
from .service import PermissionsService


router = APIRouter(tags=["Permissions"])


@router.post(
    "/courses/{course_id}/permissions",
    response_model=PermissionReadSchema,
    status_code=status.HTTP_201_CREATED
)
async def grant_permission(
    data: PermissionCreateSchema,
    svc: PermissionsService = Depends(get_permissions_service),
    current_course: CourseReadSchema = Depends(get_current_course)
):
    return await svc.set_user_permission(data)