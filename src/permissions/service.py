import logging
from ..core.log import configure_logging

from datetime import UTC, datetime
from typing import List, Optional
from uuid import UUID

from .models import PermissionsORM
from .repository import PermissionRepository
from .schemas import PermissionCreateSchema, PermissionReadSchema
from .exceptions import PermissionsHTTPExceptions
from .permissionsEnum import PermissionsEnum


logger = logging.getLogger(__name__)
configure_logging()


class PermissionsService:
    def __init__(self, repository: PermissionRepository, http_exceptions: PermissionsHTTPExceptions):
        self.repository = repository
        self.http_exceptions = http_exceptions

    async def get_course_permission_for_user(
            self, 
            user_id: UUID, 
            course_id: UUID) -> Optional[PermissionReadSchema]:
        permission_entity = await self.repository.get_by_id(user_id, course_id)
        if permission_entity is None: 
            return None
        
        return PermissionReadSchema.model_validate(permission_entity)


    async def set_user_permission(
        self,
        course_id: UUID,
        data: PermissionCreateSchema
    ) -> PermissionReadSchema:
        
        logger.debug(f"Метод set_user-permission({course_id}, для {data.user_id})")

        """
        Выдает пользователю право на курс до data.expiration_date.
        Если запись уже есть — обновляет её.
        """
        now = datetime.now(UTC)


        entity = await self.repository.get_by_id(data.user_id, course_id)

        if entity:
            entity.access_level    = data.access_level
            entity.granted_at      = now
            entity.expiration_date = data.expiration_date
        else:

            entity = PermissionsORM(
                user_id         = data.user_id,
                course_id       = course_id,
                access_level    = data.access_level,
                granted_at      = now,
                expiration_date = data.expiration_date
            )

            await self.repository.create(entity)


        return PermissionReadSchema.model_validate(entity)

    async def get_all_user_permissions(self, user_id: UUID) -> List[PermissionReadSchema]:
        entities = await self.repository.get_all_by_user(user_id)
        return [PermissionReadSchema.model_validate(entity) for entity in entities]

    
    async def compare_permissions(
        self, 
        user_id: UUID, 
        course_id: UUID, 
        access_level: PermissionsEnum) -> bool:
        
        permission = await self.get_course_permission_for_user(user_id, course_id)
        
        
        return bool(permission) and permission.access_level == access_level