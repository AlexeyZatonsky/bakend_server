from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta, UTC
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging
import sys
import random

from .schemas import UserCreateSchema, UserReadSchema, TokenDataSchema
from ..settings.config import settings
from .repository import AuthRepository

# Настраиваем логирование
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Создаем обработчик для вывода в консоль
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)

# Создаем форматтер для логов
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

# Добавляем обработчик к логгеру
logger.addHandler(console_handler)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = AuthRepository(session)
        self.secret_key = settings.SECRET_AUTH
        self.algorithm = "HS256"
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Проверка пароля"""
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Хеширование пароля"""
        return pwd_context.hash(password)

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Создание JWT токена"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(UTC) + expires_delta
        else:
            expire = datetime.now(UTC) + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    async def authenticate_user(self, email: str, password: str) -> Optional[UserReadSchema]:
        """Аутентификация пользователя"""
        result = await self.repository.get_user_by_email(email)
        if not result:
            return None
            
        user, secret_info = result
            
        if not self.verify_password(password, secret_info.hashed_password):
            return None
            
        # Создаем словарь с данными для валидации
        user_data = {
            "id": user.id,
            "username": user.username,
            "avatar": user.avatar,
            "is_verified": user.is_verified,
            "is_active": user.is_active,
            "email": secret_info.email,
            "created_at": user.created_at,
            "updated_at": user.updated_at
        }
        return UserReadSchema.model_validate(user_data)

    async def create_user(self, user_data: UserCreateSchema) -> UserReadSchema:
        """Создание нового пользователя"""
        # Проверяем, существует ли пользователь с таким email
        existing_user = await self.repository.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )

        # Генерируем username из email (берем часть до @)
        username = user_data.email.split('@')[0]
        
        # Проверяем, существует ли пользователь с таким username
        existing_username = await self.repository.get_user_by_username(username)
        if existing_username:
            # Если username занят, добавляем случайное число
            username = f"{username}_{random.randint(1000, 9999)}"

        # Создаем пользователя
        hashed_password = self.get_password_hash(user_data.password)
        user = await self.repository.create_user(user_data, hashed_password, username)
        
        # Получаем пользователя и его секретную информацию для валидации
        result = await self.repository.get_user_by_email(user_data.email)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )
            
        user, secret_info = result
        user_data = {
            "id": user.id,
            "username": user.username,
            "avatar": user.avatar,
            "is_verified": user.is_verified,
            "is_active": user.is_active,
            "email": secret_info.email,
            "created_at": user.created_at,
            "updated_at": user.updated_at
        }
        return UserReadSchema.model_validate(user_data)

    async def get_current_user(self, token: str) -> UserReadSchema:
        """Получение текущего пользователя по токену"""
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            logger.info("Starting token validation")
            logger.info(f"Token to validate: {token[:10]}...")  # Логируем только начало токена
            
            # Декодируем токен
            try:
                payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
                logger.info(f"Token decoded successfully. Payload: {payload}")
            except JWTError as e:
                logger.error(f"JWT decode error: {str(e)}")
                raise credentials_exception
                
            email: str = payload.get("sub")
            if email is None:
                logger.error("Token payload does not contain email")
                raise credentials_exception
            logger.info(f"Token decoded successfully for email: {email}")
                
            # Получаем пользователя
            result = await self.repository.get_user_by_email(email)
            if not result:
                logger.error(f"User not found for email: {email}")
                raise credentials_exception
                
            user, secret_info = result
            logger.info(f"User found: {user.username}")
            user_data = {
                "id": user.id,
                "username": user.username,
                "avatar": user.avatar,
                "is_verified": user.is_verified,
                "is_active": user.is_active,
                "email": secret_info.email,
                "created_at": user.created_at,
                "updated_at": user.updated_at
            }
            return UserReadSchema.model_validate(user_data)
            
        except JWTError as e:
            logger.error(f"JWT validation error: {str(e)}")
            raise credentials_exception
        except Exception as e:
            logger.error(f"Unexpected error in get_current_user: {str(e)}")
            raise credentials_exception

    async def update_user(self, user_id: str, update_data: dict) -> UserReadSchema:
        """Обновление данных пользователя"""
        user = await self.repository.update_user(user_id, update_data)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return UserReadSchema.model_validate(user)

    async def delete_user(self, user_id: str) -> bool:
        """Удаление пользователя"""
        success = await self.repository.delete_user(user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return True 