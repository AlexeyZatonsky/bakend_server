from uuid import UUID
from typing import List, Optional

from sqlalchemy import update,select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.AbstractRepository import AbstractRepository
from .models import CoursesORM




class CourseRepository(AbstractRepository[CoursesORM]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, CoursesORM)

    async def get_by_id(self, entity_id: UUID) -> Optional[CoursesORM]:
        """Получение курса по его UUID"""
        return await super().get_by_id(entity_id)

    async def get_all(self, limit: int = 20) -> List[CoursesORM]:
        """Получение списка всех курсов с заданным лимитом"""
        return await super().get_all(limit)

    async def create(self, entity: CoursesORM) -> CoursesORM:
        """Создание нового курса"""
        return await super().create(entity)

    async def delete(self, entity: CoursesORM) -> None:
        """Удаление существующего курса"""
        await super().delete(entity)

    async def get_by_channel_id(self, channel_id: str) -> Optional[CoursesORM]:
        """Получение всех кусов определённого канала"""
        query = select(CoursesORM).where(CoursesORM.channel_id == channel_id)
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def get_by_name_and_channel_id(self, channel_id: str, course_name: str) -> Optional[CoursesORM]:
        query = select(CoursesORM).where(
            (CoursesORM.channel_id == channel_id) 
            & 
            (CoursesORM.name == course_name)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
