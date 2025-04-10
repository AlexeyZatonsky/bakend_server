from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..core.AbstractRepository import AbstractRepository

from .models import ChannelsORM



class ChannelRepository(AbstractRepository[ChannelsORM]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, ChannelsORM)


    async def get_by_id(self, entity_id: UUID) -> Optional[ChannelsORM]:
        """Получение секретной информации по UUID пользователя"""
        return await super().get_by_id(entity_id)

    async def get_all(self, limit: int = 20) -> List[ChannelsORM]:
        """Получение списка секретных данных пользователей с лимитом"""
        return await super().get_all(limit)

    async def create(self, entity: ChannelsORM) -> ChannelsORM:
        """Создание секретной информации"""
        return await super().create(entity)

    async def delete(self, entity: ChannelsORM) -> None:
        """Удаление секретной информации"""
        await super().delete(entity)

    async def get_by_owner(self, owner_id: UUID) -> list[ChannelsORM]:
        query = select(ChannelsORM).where(ChannelsORM.owner_id == owner_id)
        result = await self.session.execute(query)
        return result.scalars().all()