from uuid import UUID
from typing import List, Optional

from sqlalchemy import update,select
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


class CourseStructureRepository(AbstractRepository[CoursesStructureORM]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, CoursesStructureORM)

    async def get_by_id(self, entity_id: UUID) -> Optional[CoursesStructureORM]:
        """Получение структурыкурса по его UUID"""
        return await super().get_by_id(entity_id)

    async def get_all(self, limit: int = 20) -> List[CoursesStructureORM]:
        """Не имплементировано"""
        return await NotImplementedError()

    async def create(self, entity: CoursesStructureORM) -> CoursesStructureORM:
        """Создание новой структуры курса"""
        return await super().create(entity)

    async def delete(self, entity: CoursesStructureORM) -> Optional[CoursesStructureORM]:
        """Удаление существующей структуры курса"""
        await super().delete(entity)

    async def update_structure(
        self,
        old_entity: CoursesStructureORM,
        new_entity: CoursesStructureORM
    ) -> Optional[CoursesStructureORM]:
        query = (
            update(self.model)
            .where(self.model.course_id == old_entity.course_id)
            .values(course_structure=new_entity.structure)
            .returning(self.model)
        )
        result = await self.session.execute(query)

        await self.session.commit()
        return result.scalar_one_or_none()