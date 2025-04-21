from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


from ..core.AbstractRepository import AbstractRepository

from .models import PermissionsEnum, PermissionsORM



class PermissionRepository(AbstractRepository[PermissionsORM]):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: UUID, course_id: UUID) -> Optional[PermissionsORM]:
        return await super().get_by_id(user_id + course_id)

    async def get_all(self, limit: int = 20) -> List[PermissionsORM]:
        return await super().get_all(limit)

    async def create(self, entity: PermissionsORM) -> PermissionsORM:
        return await super().create(entity)

    async def delete(self, entity: PermissionsORM) -> None:
        await super().delete(entity)
