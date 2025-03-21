from uuid import UUID
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.dialects.postgresql import UUID

from .models import UsersORM, SecretInfoORM
from .schemas import UserCreateSchema


class AuthRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(self, user_data: UserCreateSchema, hashed_password: str, username: str) -> UsersORM:
        """Создание нового пользователя"""
        # Создаем пользователя
        user = UsersORM(
            username=username,
            is_verified=False,
            is_active=True
        )
        self.session.add(user)
        await self.session.flush()

        # Создаем секретную информацию
        secret_info = SecretInfoORM(
            user_id=user.id,
            email=user_data.email,
            hashed_password=hashed_password
        )
        self.session.add(secret_info)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_user_by_email(self, email: str) -> Optional[tuple[UsersORM, SecretInfoORM]]:
        """Получение пользователя и его секретной информации по email"""
        # Получаем секретную информацию
        secret_query = select(SecretInfoORM).where(SecretInfoORM.email == email)
        secret_result = await self.session.execute(secret_query)
        secret_info = secret_result.scalar_one_or_none()
        
        if not secret_info:
            return None
            
        # Получаем данные пользователя
        user_query = select(UsersORM).where(UsersORM.id == secret_info.user_id)
        user_result = await self.session.execute(user_query)
        user = user_result.scalar_one_or_none()
        
        if not user:
            return None
            
        return user, secret_info

    async def get_user_by_id(self, user_id: str) -> Optional[UsersORM]:
        """Получение пользователя по ID"""
        query = select(UsersORM).where(UsersORM.id == user_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> Optional[UsersORM]:
        """Получение пользователя по username"""
        query = select(UsersORM).where(UsersORM.username == username)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_user_with_secret_info(self, user_id: str) -> Optional[UsersORM]:
        """Получение пользователя с секретной информацией"""
        query = (
            select(UsersORM)
            .options(selectinload(UsersORM.secret_info))
            .where(UsersORM.id == user_id)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def update_user(self, user_id: str, update_data: dict) -> Optional[UsersORM]:
        """Обновление данных пользователя"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return None

        for field, value in update_data.items():
            if hasattr(user, field):
                setattr(user, field, value)

        await self.session.commit()
        return user

    async def update_secret_info(self, user_id: str, update_data: dict) -> Optional[SecretInfoORM]:
        """Обновление секретной информации пользователя"""
        user = await self.get_user_with_secret_info(user_id)
        if not user or not user.secret_info:
            return None

        for field, value in update_data.items():
            if hasattr(user.secret_info, field):
                setattr(user.secret_info, field, value)

        await self.session.commit()
        return user.secret_info

    async def delete_user(self, user_id: str) -> bool:
        """Удаление пользователя"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return False

        await self.session.delete(user)
        await self.session.commit()
        return True
