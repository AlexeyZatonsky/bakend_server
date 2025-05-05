from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Type, Optional, List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import DeclarativeBase


import logging
from ..core.log import configure_logging



logger = logging.getLogger(__name__)
configure_logging()



ModelType = TypeVar("ModelType", bound=DeclarativeBase)

class AbstractRepository(ABC, Generic[ModelType]):
    def __init__(self, session: AsyncSession, model: Type[ModelType]):
        self.session = session
        self.model = model

    # Базовая реализация метода получения по id
    async def get_by_id(self, entity_id: UUID | str) -> Optional[ModelType]:
        query = select(self.model).where(self.model.id == entity_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    # Базовая реализация метода получения всех записей с лимитом
    async def get_all(self, limit: int = 20) -> List[ModelType]:
        query = select(self.model).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()

    # Базовая реализация метода создания записи
    async def create(self, entity: ModelType) -> ModelType:  
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    # Базовая реализация метода удаления записи
    async def delete(self, entity: ModelType) -> None:
        await self.session.delete(entity)
        await self.session.commit()
