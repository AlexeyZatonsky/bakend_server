import logging
from ..core.log import configure_logging

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Path, status
from uuid import UUID

from ..courses.dependencies import get_current_course_with_owner_validate
from ..courses.schemas import CourseReadSchema

from .dependencies import get_permissions_service, require_permission
from .schemas import PermissionCreateSchema, PermissionReadSchema
from .service import PermissionsService

logger = logging.getLogger(__name__)
configure_logging()


router = APIRouter(
    tags=["Permissions"],
    prefix="/courses",
)


@router.post(
    "/{course_id}/permissions",
    response_model=PermissionReadSchema,
    status_code=status.HTTP_201_CREATED
)
async def grant_course_permission(

    data: PermissionCreateSchema = Depends(),
    service: PermissionsService = Depends(get_permissions_service),
    current_course: CourseReadSchema = Depends(get_current_course_with_owner_validate)
):
    logger.debug("Провалились внутрь роута")
    return await service.set_user_permission(current_course.id, data)


# @router.get(
#     "/courses/{course_id}/permissions/{access_level}",
#     response_model=PermissionReadSchema,
#     status_code=status.HTTP_202_ACCEPTED
# )
# async def require_permission(
#     service: PermissionsService = Depends(get_permissions_service),
#     permission: PermissionReadSchema = Depends(require_permission(access_level))
# )