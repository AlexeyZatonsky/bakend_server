import logging
import sys
import random
from uuid import UUID
from datetime import datetime, timedelta, UTC
from typing import Optional

from jose import JWTError, jwt
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from .schemas import (
    UserCreateSchema,
    UserReadSchema,
    TokenSchema,
    TokenDataSchema
)
from ..settings.config import settings
from .repository import AuthRepository
from passlib.context import CryptContext

# Логирование
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def __init__(self, session: AsyncSession):
        self.repository = AuthRepository(session)
        self.secret_key = settings.SECRET_AUTH
        self.algorithm = "HS256"
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Проверяет пароль пользователя."""
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Генерирует хеш пароля."""
        return pwd_context.hash(password)

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Создаёт JWT-токен."""
        to_encode = data.copy()
        expire = datetime.now(UTC) + (expires_delta or timedelta(minutes=self.access_token_expire_minutes))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    async def authenticate_user(self, email: str, password: str) -> Optional[UserReadSchema]:
        """Аутентифицирует пользователя по email и паролю."""
        result = await self.repository.get_user_by_email(email)
        if not result:
            logger.info(f"Authentication failed: user not found (email={email})")
            return None

        user, secret_info = result
        if not self.verify_password(password, secret_info.hashed_password):
            logger.info(f"Authentication failed: invalid password (email={email})")
            return None

        return UserReadSchema.from_orm(user, secret_info)

    async def create_user(self, user_data: UserCreateSchema) -> UserReadSchema:
        """Создаёт нового пользователя."""
        if await self.repository.get_user_by_email(user_data.email):
            logger.warning(f"User creation failed: email already exists ({user_data.email})")
            raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered")

        username = user_data.email.split('@')[0]
        if await self.repository.get_user_by_username(username):
            username = f"{username}_{random.randint(1000, 9999)}"

        hashed_password = self.get_password_hash(user_data.password)
        user = await self.repository.create_user(user_data, hashed_password, username)

        result = await self.repository.get_user_by_email(user_data.email)
        if not result:
            logger.error("User creation failed: user not retrievable after creation")
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to create user")

        user, secret_info = result
        return UserReadSchema.from_orm(user, secret_info)

    async def get_current_user(self, token: str) -> UserReadSchema:
        """Получает текущего пользователя из JWT-токена."""
        credentials_exception = HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            email: str = payload.get("sub")
            if email is None:
                logger.error("Token payload error: email not found")
                raise credentials_exception

            result = await self.repository.get_user_by_email(email)
            if not result:
                logger.error(f"User not found (email={email})")
                raise credentials_exception

            user, secret_info = result
            return UserReadSchema.from_orm(user, secret_info)

        except JWTError as e:
            logger.error(f"JWTError: {str(e)}")
            raise credentials_exception
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise credentials_exception

    async def update_user(self, user_id: UUID, update_data: dict) -> UserReadSchema:
        """Обновляет данные пользователя."""
        user = await self.repository.update_user(user_id, update_data)
        if not user:
            logger.warning(f"User update failed: user not found (id={user_id})")
            raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
        secret_info = await self.repository.secret_repo.get_by_id(user_id)
        return UserReadSchema.from_orm(user, secret_info)

    async def delete_user(self, user_id: UUID) -> bool:
        """Удаляет пользователя по его идентификатору."""
        success = await self.repository.delete_user(user_id)
        if not success:
            logger.warning(f"User deletion failed: user not found (id={user_id})")
            raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
        logger.info(f"User deleted successfully (id={user_id})")
        return True
