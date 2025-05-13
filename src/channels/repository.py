from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from ..core.AbstractRepository import AbstractRepository
from ..core.Enums.ExtensionsEnums import ImageExtensionsEnum

from .models import ChannelsORM

import logging
from ..core.log import configure_logging

logger = logging.getLogger(__name__)
configure_logging()


class ChannelRepository(AbstractRepository[ChannelsORM]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, ChannelsORM)


    async def get_by_id(self, entity_id: str) -> Optional[ChannelsORM]:
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
        
    async def set_avatar_extension(self, channel_id: str, extension: ImageExtensionsEnum) -> None:
        """Устанавливает расширение аватара канала"""
        logger.debug(f"Передано в avatar_ext: {extension} ({type(extension)}), name={getattr(extension, 'name', None)}, value={getattr(extension, 'value', None)}")

        await self.session.execute(
            update(ChannelsORM)
            .where(ChannelsORM.id == channel_id)
            .values(avatar_ext = extension)
        )
        await self.session.commit()