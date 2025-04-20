from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


from ..core.AbstractRepository import AbstractRepository

from .models import AccessLevelEnum, UsersPermissionsORM



class PermissionRepository(AbstractRepository[UsersPermissionsORM]):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, entity_id: UUID) -> Optional[UsersPermissionsORM]:
        return await super().get_by_id(entity_id)

    async def get_all(self, limit: int = 20) -> List[UsersPermissionsORM]:
        return await super().get_all(limit)

    async def create(self, entity: UsersPermissionsORM) -> UsersPermissionsORM:
        return await super().create(entity)

    async def delete(self, entity: UsersPermissionsORM) -> None:
        await super().delete(entity)
