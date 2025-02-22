from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging
import sys

from .models import Users, SecretInfo
from .schemas import UserCreate
from ..settings.config import SECRET_AUTH

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

    def create_access_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=30)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_AUTH, algorithm="HS256")
        logger.info(f"Created access token for user ID: {data.get('sub')}")
        return encoded_jwt

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)

    async def authenticate_user(self, email: str, password: str):
        logger.info(f"Attempting authentication for email: {email}")
        secret_info = await self.session.execute(
            select(SecretInfo).where(SecretInfo.email == email)
        )
        secret_info = secret_info.scalar_one_or_none()
        
        if not secret_info:
            logger.warning(f"Authentication failed: email not found: {email}")
            return None
            
        if not self.verify_password(password, secret_info.hashed_password):
            logger.warning(f"Authentication failed: invalid password for email: {email}")
            return None
            
        user = await self.session.execute(
            select(Users).where(Users.id == secret_info.user_id)
        )
        user = user.scalar_one_or_none()
        logger.info(f"Authentication successful for user: {user.username}")
        return user

    async def register_new_user(self, user_data: UserCreate):
        logger.info(f"Attempting to register new user with email: {user_data.email}")
        
        # Проверка существующего email
        existing_email = await self.session.execute(
            select(SecretInfo).where(SecretInfo.email == user_data.email)
        )
        if existing_email.scalar_one_or_none():
            logger.warning(f"Registration failed: email already exists: {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Создаем пользователя
        user = Users(username=user_data.username)
        self.session.add(user)
        await self.session.flush()

        # Создаем секретную информацию
        secret_info = SecretInfo(
            user_id=user.id,
            email=user_data.email,
            hashed_password=self.get_password_hash(user_data.password)
        )
        self.session.add(secret_info)
        await self.session.commit()
        
        logger.info(f"Successfully registered new user: {user.username} with ID: {user.id}")
        return user 