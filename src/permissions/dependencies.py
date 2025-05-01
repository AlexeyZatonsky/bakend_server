import logging
from ..core.log import configure_logging

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

logger = logging.getLogger(__name__)
configure_logging()




async def get_permissions_service(session:AsyncSession = Depends(get_async_session)) -> PermissionsService:
    logger.debug("get_permissions_service")
    
    repository = PermissionRepository(session)
    http_exceptions = PermissionsHTTPExceptions()
    return PermissionsService(repository, http_exceptions)



def require_permission(
    access_level: PermissionsEnum,
    course_id_param: str = "course_id",
):
    """
    dependency-factory, которую можно вешать на эндпоинты:

    ```python
    permission: PermissionReadSchema = Depends(
        require_permission(PermissionsEnum.OWNER)
    )
    ```
    """

    async def dependency(
        course_id: UUID = Path(..., alias=course_id_param),
        user: UserReadSchema = Depends(get_current_user),
        permissions_service: PermissionsService = Depends(get_permissions_service),
    ) -> PermissionReadSchema:
        
        logger.debug("permissions.dependencies.dependency")

        # 1. получаем запись о правах
        perm = await permissions_service.get_course_permission_for_user(
            user.id, course_id
        )

        # 2. есть ли вообще право?
        if perm is None:
            raise permissions_service.http_exceptions.forbidden_403()

        # 3. проверяем уровень доступа ( str(), потому что use_enum_values=True )
        if perm.access_level != access_level:
            raise permissions_service.http_exceptions.forbidden_403()

        # 4. не просрочено ли?
        if perm.expiration_date and perm.expiration_date < datetime.now(UTC):
            raise permissions_service.http_exceptions.forbidden_403(
                "Your permission has expired"
            )

        logger.debug("get_course_permission_for_user: SUCCESSFULL")

        return perm

    return dependency