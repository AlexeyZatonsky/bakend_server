from uuid import UUID
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.AbstractRepository import AbstractRepository
from .models import CoursesORM, CoursesStructureORM




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



class CourseStructureRepository(AbstractRepository[CoursesStructureORM]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, CoursesStructureORM)

