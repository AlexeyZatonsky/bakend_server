import logging
import sys
import random
from uuid import UUID
from datetime import datetime, timedelta, UTC
from typing import Optional, Dict, Any

from jose import JWTError, jwt
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from .schemas import (
    UserCreateSchema,
    UserReadSchema,
    TokenSchema,
    TokenDataSchema,
    UserUpdateSchema
)
from ..settings.config import settings
from .repository import AuthRepository
from .models import UsersORM, SecretInfoORM
from passlib.context import CryptContext

# Логирование
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
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
        """Проверяет соответствие пароля хешу"""
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Хеширует пароль"""
        return pwd_context.hash(password)

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Создает JWT токен доступа"""
        to_encode = data.copy()
        expire = datetime.now(UTC) + (expires_delta or timedelta(minutes=self.access_token_expire_minutes))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def _generate_username_from_email(self, email: str) -> str:
        """Генерирует имя пользователя на основе email"""
        username_base = email.split('@')[0]
        random_suffix = random.randint(1000, 9999)
        return f"{username_base}_{random_suffix}"

    def _schema_from_user(self, user: UsersORM, secret_info: SecretInfoORM) -> UserReadSchema:
        """Создает схему UserReadSchema из ORM объектов"""
        return UserReadSchema.from_orm(user, secret_info)

    async def authenticate_user(self, email: str, password: str) -> Optional[UserReadSchema]:
        """Аутентифицирует пользователя по email и паролю"""
        result = await self.repository.get_user_by_email(email)
        if result:
            user, secret_info = result
            if self.verify_password(password, secret_info.hashed_password):
                logger.info(f"User found: {user.username}")
                return self._schema_from_user(user, secret_info)
        return None

    async def create_user(self, user_data: UserCreateSchema) -> UserReadSchema:
        """Создает нового пользователя"""
        # Проверяем, существует ли пользователь с таким email
        if await self.repository.get_user_by_email(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists"
            )
        
        # Генерируем имя пользователя из email
        username = self._generate_username_from_email(user_data.email)
        
        # Хешируем пароль
        hashed_password = self.get_password_hash(user_data.password)
        
        # Создаем пользователя
        user = await self.repository.create_user(user_data, hashed_password, username)
        
        # Получаем созданного пользователя и его секретную информацию
        result = await self.repository.get_user_by_email(user_data.email)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )
            
        user, secret_info = result
        return self._schema_from_user(user, secret_info)

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
            
            return self._schema_from_user(user, secret_info)
            
        except JWTError as e:
            logger.error(f"JWT validation error: {str(e)}")
            raise credentials_exception
        except Exception as e:
            logger.error(f"Unexpected error in get_current_user: {str(e)}")
            raise credentials_exception

    async def update_user(self, user_id: str, update_data: Dict[str, Any]) -> UserReadSchema:
        """Обновляет данные пользователя"""
        # Разделяем данные на основные данные пользователя и секретные данные
        user_data = {}
        secret_info_data = {}
        
        for key, value in update_data.items():
            if key in ['username', 'avatar', 'is_verified', 'is_active']:
                user_data[key] = value
            elif key in ['phone_number', 'INN', 'organization_name']:
                secret_info_data[key] = value
        
        # Обновляем данные пользователя
        if user_data:
            updated_user = await self.repository.update_user(UUID(user_id), user_data)
            if not updated_user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
        
        # Обновляем секретные данные пользователя
        if secret_info_data:
            updated_secret_info = await self.repository.update_secret_info(UUID(user_id), secret_info_data)
            if not updated_secret_info:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User secret info not found"
                )
        
        # Получаем обновлённого пользователя
        result = await self.repository.get_user_by_id(UUID(user_id))
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found after update"
            )
            
        # Получаем секретную информацию пользователя
        secret_info = await self.repository.secret_repo.get_by_id(UUID(user_id))
        if not secret_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User secret info not found after update"
            )
            
        return self._schema_from_user(result, secret_info)

    async def delete_user(self, user_id: str) -> bool:
        """Удаляет пользователя"""
        success = await self.repository.delete_user(UUID(user_id))
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return True
