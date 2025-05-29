from uuid import UUID
from typing import List, Optional

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.AbstractRepository import AbstractRepository
from .models import  CoursesStructureORM



class CourseStructureRepository(AbstractRepository[CoursesStructureORM]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, CoursesStructureORM)

    async def get_by_id(self, entity_id: UUID) -> Optional[CoursesStructureORM]:
        """Получение структурыкурса по его UUID"""
        return await super().get_by_id(entity_id)

    async def get_all(self, limit: int = 20) -> List[CoursesStructureORM]:
        """Не имплементировано"""
        raise await NotImplementedError()

    async def create(self, entity: CoursesStructureORM) -> CoursesStructureORM:
        """Создание новой структуры курса"""
        return await super().create(entity)

    async def delete(self, entity: CoursesStructureORM) -> None:
        """Удаление существующей структуры курса"""
        await super().delete(entity)

    async def update_structure(
        self,
        old_entity: CoursesStructureORM,
        new_entity: CoursesStructureORM
    ) -> Optional[CoursesStructureORM]:
        query = (
            update(self.model)
            .where(self.model.id == old_entity.id)
            .values(structure=new_entity.structure)
            .returning(self.model)
        )
        result = await self.session.execute(query)

        await self.session.commit()
        return result.scalar_one_or_none()