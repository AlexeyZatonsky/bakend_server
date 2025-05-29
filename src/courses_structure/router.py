from typing import List
from fastapi import APIRouter, Depends, status, Path, Body
from uuid import UUID


from ..auth.dependencies import get_current_user
from ..auth.schemas import UserReadSchema

from ..core.Enums.PermissionsEnum import PermissionsEnum
from ..permissions.schemas import PermissionReadSchema
from ..permissions.dependencies import require_permission



from .dependencies import get_course_structure_service
from .service import CourseStructureService
from .schemas import FullStructureReadSchema, FullStructureCreateSchema


from ..courses.schemas import CourseReadSchema





router = APIRouter(
    tags=["CourseStructure"],
    prefix="/courses/{course_id}/structure",
)


@router.get(
    "/",
    response_model=FullStructureReadSchema,
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
    response_model=FullStructureReadSchema, 
    status_code=status.HTTP_201_CREATED,
    summary="Используется только для первичного создания структуры"
)
async def create_structure(
    course_id: UUID = Path(..., alias="course_id"),
    _: PermissionReadSchema = Depends(
        require_permission(
            access_level={PermissionsEnum.OWNER, PermissionsEnum.HIGH_MODERATOR},
            skip_if_public=False,
        )
    ),
    structure_data: FullStructureCreateSchema = Body(...),
    service: CourseStructureService = Depends(get_course_structure_service),
):
    return await service.create_structure_for_course(course_id, structure_data.structure)

@router.post(
    "/", 
    response_model=FullStructureReadSchema, 
    status_code=status.HTTP_201_CREATED,
    summary="Исапользуется для обновления структуры"
)
async def update_structure(
    course_id: UUID = Path(..., alias="course_id"),
    _: PermissionReadSchema = Depends(
        require_permission(
            access_level={PermissionsEnum.OWNER, PermissionsEnum.HIGH_MODERATOR},
            skip_if_public=False,
        )
    ),
    structure_data: FullStructureCreateSchema = Body(...),
    service: CourseStructureService = Depends(get_course_structure_service),
):
    return await service.update_structure_for_course(course_id, structure_data.structure)