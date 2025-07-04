import logging
from ..core.log import configure_logging

from typing import List
from fastapi import APIRouter, Depends, Path, status
from uuid import UUID

from ..auth.schemas import UserReadSchema
from ..auth.dependencies import get_current_user

from ..courses.dependencies import get_current_course_with_owner_validate
from ..courses.schemas import CourseReadSchema


from .dependencies import get_permissions_service
from .schemas import PermissionCreateSchema, PermissionReadSchema
from .service import PermissionsService

logger = logging.getLogger(__name__)
configure_logging()


router = APIRouter(
    tags=["Permissions"],
)


@router.post(
    "/courses/{course_id}/permissions",
    response_model=PermissionReadSchema,
    status_code=status.HTTP_201_CREATED
)
async def grant_course_permission(
    data: PermissionCreateSchema,
    service: PermissionsService = Depends(get_permissions_service),
    current_course: CourseReadSchema = Depends(get_current_course_with_owner_validate)
):
    return await service.set_user_permission(current_course.id, data)


@router.get(
    "/courses/{course_id}/permissions",
    response_model=PermissionReadSchema,
    status_code=status.HTTP_200_OK
)
async def get_course_permission(
    course_id: UUID = Path(..., alias="course_id"),
    service: PermissionsService = Depends(get_permissions_service),
    current_user: UserReadSchema = Depends(get_current_user),
):
    return await service.get_course_permission_for_user(current_user.id, course_id)


@router.get(
    "/my/permissions",
    response_model=List[PermissionReadSchema],
    status_code=status.HTTP_200_OK
)
async def get_permissions_for_user(
    current_user: UserReadSchema = Depends(get_current_user),
    service: PermissionsService = Depends(get_permissions_service),
):
    return await service.get_all_user_permissions(current_user.id)