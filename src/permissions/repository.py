from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


from ..core.AbstractRepository import AbstractRepository

from .models import PermissionsEnum, PermissionsORM

import logging
from ..core.log import configure_logging


logger = logging.getLogger(__name__)
configure_logging()

class PermissionRepository(AbstractRepository[PermissionsORM]):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: UUID, course_id: UUID) -> Optional[PermissionsORM]:
        stmt = (
            select(PermissionsORM)
            .where(
                PermissionsORM.user_id == user_id and
                PermissionsORM.course_id == course_id
            ).limit(1)
        )
        logger.debug("Выполняется метод слоя Repository для получения прав пользователя")
        res = await self.session.execute(stmt)
        logger.debug("Выполнен запрос на получение прав")
        return res.scalar_one_or_none()

    async def get_all(self, limit: int = 20) -> List[PermissionsORM]:
        return await super().get_all(limit)

    async def create(self, entity: PermissionsORM) -> PermissionsORM:
        return await super().create(entity)

    async def delete(self, entity: PermissionsORM) -> None:
        await super().delete(entity)

    async def get_all_by_user(self, user_id: UUID) -> List[PermissionsORM]:
        stmt = select(PermissionsORM).where(PermissionsORM.user_id == user_id)
        res = await self.session.execute(stmt)
        return list(res.scalars().all())