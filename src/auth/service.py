import logging
import sys
import random
from uuid import UUID
from datetime import datetime, timedelta, UTC
from typing import List, Optional, Dict, Any

from jose import JWTError, jwt
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..settings.config import AUTH_ENV

from ..core.Enums.MIMETypeEnums import ImageMimeEnum
from ..core.Enums.ExtensionsEnums import ImageExtensionsEnum
from ..core.Enums.TypeReferencesEnums import ImageTypeReference

from .schemas import (
    UserCreateSchema,
    UserReadSchema,
    UserReadPublicSchema
)
from .repository import AuthRepository
from .exceptions import AuthHTTPExceptions
from passlib.context import CryptContext

import logging
from ..core.log import configure_logging

logger = logging.getLogger(__name__)
configure_logging()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def __init__(self, session: AsyncSession, http_exceptions :AuthHTTPExceptions):
        self.repository = AuthRepository(session)
        self.http_exceptions = http_exceptions
        self.secret_key = AUTH_ENV.SECRET_AUTH
        self.algorithm = "HS256"
        self.access_token_expire_minutes = AUTH_ENV.ACCESS_TOKEN_EXPIRE_MINUTES

        logger.warning("AuthService успешно инициализирован")


    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        expire = datetime.now(UTC) + (expires_delta or timedelta(minutes=self.access_token_expire_minutes))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def _generate_username_from_email(self, email: str) -> str:
        username_base = email.split('@')[0]
        random_suffix = random.randint(1000, 9999)
        return f"{username_base}_{random_suffix}"

    async def authenticate_user(self, email: str, password: str) -> Optional[UserReadSchema]:
        result = await self.repository.get_user_by_email(email)
        if result:
            user, secret_info = result
            if pwd_context.verify(password, secret_info.hashed_password):
                logger.info(f"User found: {user.username}")
                return UserReadSchema.from_orm(user, secret_info)
        return None

    async def create_user(self, user_data: UserCreateSchema) -> UserReadSchema:
        if await self.repository.get_user_by_email(user_data.email):
            raise self.http_exceptions.conflict_409()
        
        username = self._generate_username_from_email(user_data.email)
        
        hashed_password = pwd_context.hash(user_data.password)
        
        user = await self.repository.create_user(user_data, hashed_password, username)
        
        result = await self.repository.get_user_by_email(user_data.email)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )
            
        user, secret_info = result
        return UserReadSchema.from_orm(user, secret_info)

    async def get_current_user(self, token: str) -> UserReadSchema:
        """Получение текущего пользователя по токену"""
        credentials_exception = self.http_exceptions.unauthorized_401("Could not validate credentials")
        
        try: 
            try:
                payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            except JWTError as e:
                logger.error(f"JWT decode error: {str(e)}")
                raise credentials_exception
                
            email: str = payload.get("sub")
            if email is None:
                raise credentials_exception
                
            result = await self.repository.get_user_by_email(email)
            if not result:
                raise credentials_exception
                
            user, secret_info = result
            
            return UserReadSchema.from_orm(user, secret_info)
            
        except JWTError as e:
            logger.error(f"JWT validation error: {str(e)}")
            raise credentials_exception
        except Exception as e:
            logger.error(f"Unexpected error in get_current_user: {str(e)}")
            raise credentials_exception


    async def delete_user(self, user_id: str) -> bool:
        success = await self.repository.delete_user(user_id)
        if not success:
            raise self.http_exceptions.not_found_404()
        return True
    
    async def get_all_users(self, limit: int = 20) -> List[UserReadPublicSchema]:
        entities = await self.repository.get_all_user_public_data(limit)
        return [UserReadPublicSchema.model_validate(user) for user in entities]

    async def set_avatar_extension(
            self,
            user_id: UUID,
            mime: ImageMimeEnum,      
    ) -> None:
        logger.debug(f"ДЛя пользователя {user_id} создаётся запись с типом аватара {mime.value}") 
        
        image_type_ref = ImageTypeReference.from_mime(mime)
        image_type: ImageExtensionsEnum = image_type_ref.ext

        logger.debug(f"Тип преобразован в {image_type.value}")
        logger.debug(f"Тип объекта {type(image_type)}")
        await self.repository.set_avatar_extension(user_id, image_type)


    async def update_username(self, user_id: UUID, username: str) -> None:
        await self.repository.update_username(user_id, username)
    
    async def update_phone_number(self, user_id: UUID, phone_number: str) -> None:
        await self.repository.update_phone_number(user_id, phone_number)
    
    async def update_organization_name(self, user_id: UUID, organization_name: str) -> None:
        await self.repository.update_organization_name(user_id, organization_name)
    
    async def update_INN(self, user_id: UUID, INN: str) -> None:
        await self.repository.update_INN(user_id, INN)
    
    
    

