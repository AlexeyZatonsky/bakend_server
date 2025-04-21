from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


from fastapi import HTTPException

from .models import PermissionsEnum
from .repository import PermissionRepository
from .schemas import PermissionCreateSchema, PermissionReadSchema
from .exceptions import PermissionsHTTPExceptions


class PermissionsService:
    def __init__(self, repository: PermissionRepository, http_exceptions: PermissionsHTTPExceptions):
        self.repository = repository
        self.http_exceptions = http_exceptions

    async def get_course_permission_for_user(self, user_id: UUID, course_id: UUID) -> Optional[PermissionReadSchema]:
        permission_entity = await self.repository.get_by_id(user_id, course_id)
        if permission_entity is None: 
            return None
        
        return PermissionReadSchema.model_validate(permission_entity)


