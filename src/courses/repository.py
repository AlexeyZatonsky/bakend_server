from uuid import UUID
from typing import List, Optional

from sqlalchemy import update,select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import CoursesORM

from ..core.AbstractRepository import AbstractRepository
from ..core.Enums.PermissionsEnum import PermissionsEnum
from ..core.Enums.ExtensionsEnums import ImageExtensionsEnum

from ..permissions.models import PermissionsORM

import logging
from ..core.log import configure_logging

logger = logging.getLogger(__name__)
configure_logging()


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
        """Создание нового курса + добавление нового пользователя как owner в permissions orm"""
        
        self.session.add(entity)
        await self.session.flush() 

        permission = PermissionsORM(
            user_id = entity.owner_id,
            course_id = entity.id,
            access_level = PermissionsEnum.OWNER,
            expiration_date = None
        )
        self.session.add(permission)

        await self.session.commit()
        await self.session.refresh(entity)
        return entity

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

    async def set_preview_extension(self, course_id: UUID, extension: ImageExtensionsEnum):
        """Устанавливает расширение превью канала"""
        logger.debug(f"Передано в preview_ext: {extension} ({type(extension)}), name={getattr(extension, 'name', None)}, value={getattr(extension, 'value', None)}")

        await self.session.execute(
            update(CoursesORM)
            .where(CoursesORM.id == course_id)
            .values(preview_ext = extension)
        )
        await self.session.commit()