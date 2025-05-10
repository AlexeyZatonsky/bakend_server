from uuid import UUID
from typing import Optional, List, Tuple

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from sqlalchemy.dialects.postgresql import UUID

from .models import UsersORM, SecretInfoORM
from .schemas import UserCreateSchema

from ..core.AbstractRepository import AbstractRepository
from ..core.Enums.ExtensionsEnums import ImageExtensionsEnum

import logging
from ..core.log import configure_logging
logger = logging.getLogger(__name__)
configure_logging()


class UserRepository(AbstractRepository[UsersORM]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, UsersORM)

    async def get_by_id(self, entity_id: UUID) -> Optional[UsersORM]:
        """Получение пользователя по UUID"""
        return await super().get_by_id(entity_id)

    async def get_all(self, limit: int = 20) -> List[UsersORM]:
        """Получение списка пользователей с лимитом"""
        return await super().get_all(limit)

    async def create(self, entity: UsersORM) -> UsersORM:
        """Создание пользователя"""
        return await super().create(entity)

    async def delete(self, entity: UsersORM) -> None:
        """Удаление пользователя"""
        await super().delete(entity)

    async def get_user_by_username(self, username: str) -> Optional[UsersORM]:
        """Получение пользователя по username"""
        query = select(UsersORM).where(UsersORM.username == username)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def set_avatar_extension(self, user_id: UUID, extension: ImageExtensionsEnum) -> None:
        logger.debug(f"Передано в avatar_ext: {extension} ({type(extension)}), name={getattr(extension, 'name', None)}, value={getattr(extension, 'value', None)}")

        await self.session.execute(
            update(UsersORM)
            .where(UsersORM.id == user_id)
            .values(avatar_ext = extension.value)
        )
        await self.session.commit()


class SecretInfoRepository(AbstractRepository[SecretInfoORM]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, SecretInfoORM)

    async def get_by_id(self, entity_id: UUID) -> Optional[SecretInfoORM]:
        """Получение секретной информации по UUID пользователя"""
        return await super().get_by_id(entity_id)

    async def get_all(self, limit: int = 20) -> List[SecretInfoORM]:
        """Получение списка секретных данных пользователей с лимитом"""
        return await super().get_all(limit)

    async def create(self, entity: SecretInfoORM) -> SecretInfoORM:
        """Создание секретной информации"""
        return await super().create(entity)

    async def delete(self, entity: SecretInfoORM) -> None:
        """Удаление секретной информации"""
        await super().delete(entity)

    async def get_by_email(self, email: str) -> Optional[SecretInfoORM]:
        """Получение секретной информации по email"""
        query = select(self.model).where(self.model.email == email)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    


class AuthRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)
        self.secret_repo = SecretInfoRepository(session)

    async def create_user(
        self, user_data: UserCreateSchema, hashed_password: str, username: str
    ) -> UsersORM:
        """
        Создание нового пользователя с его секретной информацией.
        В рамках одной транзакции создаются обе записи.
        """
        user = UsersORM(username=username, is_verified=False, is_active=True)
        self.session.add(user)
        await self.session.flush()  # flush чтобы получить user.id до commit'а

        secret_info = SecretInfoORM(
            id=user.id,
            email=user_data.email,
            hashed_password=hashed_password
        )
        self.session.add(secret_info)

        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_user_by_email(self, email: str) -> Optional[Tuple[UsersORM, SecretInfoORM]]:
        """
        Получение пользователя и его секретной информации по email.
        Возвращает None, если не найден пользователь или секретные данные.
        """
        secret_info = await self.secret_repo.get_by_email(email)
        if not secret_info:
            return None

        user = await self.user_repo.get_by_id(secret_info.id)
        if not user:
            return None

        return user, secret_info

    async def get_user_with_secret_info(self, user_id: UUID) -> Optional[UsersORM]:
        """Получение пользователя с его секретной информацией по ID"""
        query = (
            select(UsersORM)
            .options(selectinload(UsersORM.secret_info))
            .where(UsersORM.id == user_id)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def update_user(self, user_id: UUID, update_data: dict) -> Optional[UsersORM]:
        """
        Обновление данных пользователя по ID.
        Возвращает обновлённого пользователя или None, если пользователь не найден.
        """
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            return None

        for field, value in update_data.items():
            if hasattr(user, field):
                setattr(user, field, value)

        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update_secret_info(
        self, user_id: UUID, update_data: dict
    ) -> Optional[SecretInfoORM]:
        """
        Обновление секретной информации пользователя по ID.
        Возвращает обновлённую секретную информацию или None, если данные не найдены.
        """
        secret_info = await self.secret_repo.get_by_id(user_id)
        if not secret_info:
            return None

        for field, value in update_data.items():
            if hasattr(secret_info, field):
                setattr(secret_info, field, value)

        await self.session.commit()
        await self.session.refresh(secret_info)
        return secret_info

    async def delete_user(self, user_id: UUID) -> bool:
        """
        Удаление пользователя и его секретной информации по ID.
        Возвращает True при успешном удалении, False, если пользователь не найден.
        """
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            return False

        await self.user_repo.delete(user)
        return True
    
    async def get_user_by_id(self, user_id: UUID):
        user_entity = await self.user_repo.get_by_id(user_id)
        secret_info_entity = await self.secret_repo.get_by_id(user_id)

        return user_entity + secret_info_entity
    
    async def get_all_user_public_data(self, limit:int = 20)->List[UsersORM]:
        return await self.user_repo.get_all(limit)
    

    async def set_avatar_extension(self, user_id: UUID, extension: ImageExtensionsEnum) -> None:
        logger.debug(f"Тип переданного в repositopry extension объекта - {type(extension)}")
        await self.user_repo.set_avatar_extension(user_id, extension)

