from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID

from ..courses.dependencies import get_current_course_with_owner_validate
from ..courses.schemas import CourseReadSchema

from .dependencies import get_permissions_service, require_permission
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
    current_course: CourseReadSchema = Depends(get_current_course_with_owner_validate)
):
    return await svc.set_user_permission(data)


@router.get(
    "/courses/{course_id}/permissions/{access_level}",
    response_model=PermissionReadSchema,
    status_code=status.HTTP_202_ACCEPTED
)
async def require_permission(
    service: PermissionsService = Depends(get_permissions_service),
    permission: PermissionReadSchema = Depends(require_permission(access_level))
)