from typing import List
from fastapi import APIRouter, Depends, status, Path, HTTPException
from uuid import UUID


from ..auth.dependencies import get_current_user
from ..auth.schemas import UserReadSchema

from ..permissions.permissionsEnum import PermissionsEnum
from ..permissions.schemas import PermissionReadSchema
from ..permissions.dependencies import require_permission



from .dependencies import get_course_structure_service
from .service import CourseStructureService
from .schemas import StructureCreateSchema, StructureReadSchema


from ..courses.schemas import CourseReadSchema





router = APIRouter(
    tags=["CourseStructure"],
    prefix="/courses/{course_id}/structure",
)


@router.get(
    "/",
    response_model=StructureReadSchema,
    status_code=status.HTTP_200_OK,
)
async def get_course_structure(
    course_id: UUID = Path(..., alias="course_id"),

    _: None | PermissionReadSchema = Depends(
        require_permission(access_level=None, skip_if_public=True)
    ),
    service: CourseStructureService = Depends(get_course_structure_service),
):
    """
    Если курс public → проверка не нужна;  
    если private → у пользователя должно быть **любое** живое право,
    иначе 403.
    """
    return await service.get_full_structure(course_id)


@router.post(
        "/", 
        response_model=StructureReadSchema, 
        status_code=status.HTTP_201_CREATED
)
async def create_structure(
    _: PermissionReadSchema = Depends(
        require_permission(
            access_level={PermissionsEnum.OWNER, PermissionsEnum.HIGH_MODERATOR},
            skip_if_public=False,
        )
    ),
    structure_data: StructureCreateSchema = Depends(),
    service: CourseStructureService = Depends(get_course_structure_service),
): pass