from datetime import UTC, datetime
from uuid import UUID
from fastapi import Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_async_session

from ..auth.schemas import UserReadSchema
from ..auth.dependencies import get_current_user

from .permissionsEnum import PermissionsEnum
from .repository import PermissionRepository
from .service import PermissionsService
from .schemas import PermissionReadSchema
from .exceptions import PermissionsHTTPExceptions


async def get_permissions_service(session:AsyncSession = Depends(get_async_session)) -> PermissionsService:
    repository = PermissionRepository(session)
    http_exceptions = PermissionsHTTPExceptions()
    return PermissionsService(repository, http_exceptions)


async def require_permission(
        course_id_param: UUID,
        access_level: PermissionsEnum
):
    async def dependency(
        course_id: UUID = Depends(Path(..., alias=course_id_param)),
        user: UserReadSchema = Depends(get_current_user),
        permissions_service: PermissionsService = Depends(get_permissions_service),
    ) -> PermissionReadSchema:

        perm = await permissions_service.get_course_permission_for_user(user.id, course_id)
        

        if (perm is None) or perm.access_level != access_level:
            raise permissions_service.http_exceptions.forbidden_403()


        if perm.expiration_date and perm.expiration_date < datetime.now(UTC):
            raise permissions_service.http_exceptions.forbidden_403(
                "Your permission has expired"
            ) 
        
        return perm

    return dependency