from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from uuid import UUID
from typing import Optional, Union, Annotated

from .models import UsersORM, SecretInfoORM

# Добавляем схему для логина
class UserLoginSchema(BaseModel):
    """Схема для логина пользователя"""
    email: EmailStr = Field(..., description="Email пользователя для входа")
    password: str = Field(..., description="Пароль пользователя для входа")

    model_config = ConfigDict(
        title="Данные для входа",
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "password": "StrongPassword123"
            }
        }
    )

class UserBaseSchema(BaseModel):
    """Базовая схема пользователя"""
    username: str = Field(..., min_length=3, max_length=255, description="Имя пользователя")
    avatar: Optional[str] = Field(None, max_length=1000, description="URL аватара пользователя")
    is_verified: bool = Field(default=False, description="Статус верификации пользователя")
    is_active: bool = Field(default=True, description="Активность пользователя")

    model_config = ConfigDict(
        title="Базовая модель пользователя",
        from_attributes=True
    )

class UserReadSchema(BaseModel):
    """Схема для чтения данных пользователя"""
    id: Union[UUID, str] = Field(..., description="Уникальный идентификатор пользователя")
    username: str = Field(..., description="Имя пользователя")
    avatar: Optional[str] = Field(None, description="URL аватара пользователя")
    is_verified: bool = Field(default=False, description="Статус верификации пользователя")
    is_active: bool = Field(default=True, description="Активность пользователя")
    email: str = Field(..., description="Email пользователя")
    created_at: datetime = Field(..., description="Дата и время создания аккаунта")
    updated_at: datetime = Field(..., description="Дата и время последнего обновления аккаунта")

    model_config = ConfigDict(
        title="Данные пользователя",
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "username": "john_doe",
                "avatar": "http://example.com/avatar.jpg",
                "is_verified": True,
                "is_active": True,
                "email": "john@example.com",
                "created_at": "2025-03-21T17:15:22.510000",
                "updated_at": "2025-03-21T17:15:22.510000"
            }
        }
    )

    @staticmethod
    def from_orm(user: UsersORM, secret_info: SecretInfoORM) -> 'UserReadSchema':
        """
        Создаёт схему из ORM моделей пользователя и секретной информации.
        
        Args:
            user: ORM модель пользователя
            secret_info: ORM модель секретной информации пользователя
            
        Returns:
            UserReadSchema: Схема для чтения данных пользователя
        """
        return UserReadSchema(
            id=str(user.id),
            username=user.username,
            avatar=user.avatar,
            is_verified=user.is_verified,
            is_active=user.is_active,
            email=secret_info.email,
            created_at=user.created_at,
            updated_at=user.updated_at
        )

class UserCreateSchema(BaseModel):
    """Схема для создания пользователя"""
    email: EmailStr = Field(..., description="Email пользователя")
    password: Annotated[str, Field(min_length=8, description="Пароль пользователя")]

    model_config = ConfigDict(
        title="Данные для создания пользователя",
        json_schema_extra={
            "example": {
                "email": "new.user@example.com",
                "password": "StrongPassword123"
            }
        }
    )

    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """
        Проверяет надежность пароля
        
        Args:
            v: Пароль для проверки
            
        Returns:
            str: Проверенный пароль
            
        Raises:
            ValueError: Если пароль не соответствует требованиям
        """
        if not any(char.isdigit() for char in v):
            raise ValueError('Пароль должен содержать хотя бы одну цифру')
        if not any(char.isupper() for char in v):
            raise ValueError('Пароль должен содержать хотя бы одну заглавную букву')
        return v

class UserUpdateSchema(BaseModel):
    """Схема для обновления данных пользователя"""
    username: Optional[str] = Field(None, min_length=3, max_length=255, description="Новое имя пользователя")
    avatar: Optional[str] = Field(None, max_length=1000, description="Новый URL аватара пользователя")
    phone_number: Optional[str] = Field(None, max_length=15, description="Номер телефона пользователя")
    INN: Optional[str] = Field(None, max_length=12, description="ИНН пользователя")
    organization_name: Optional[str] = Field(None, max_length=255, description="Название организации пользователя")
    is_verified: Optional[bool] = Field(None, description="Новый статус верификации пользователя")
    is_active: Optional[bool] = Field(None, description="Новый статус активности пользователя")

    model_config = ConfigDict(
        title="Данные для обновления пользователя",
        from_attributes=True,
        json_schema_extra={
            "example": {
                "username": "updated_username",
                "avatar": "http://example.com/new_avatar.jpg",
                "phone_number": "+79123456789",
                "organization_name": "Company Ltd."
            }
        }
    )

class TokenSchema(BaseModel):
    """Схема токена доступа"""
    access_token: str = Field(..., description="JWT токен доступа")
    token_type: str = Field(default="bearer", description="Тип токена")

    model_config = ConfigDict(
        title="Токен доступа",
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }
    )

class TokenDataSchema(BaseModel):
    """Схема данных токена"""
    email: Optional[EmailStr] = Field(None, description="Email пользователя")
    user_id: Optional[UUID] = Field(None, description="ID пользователя")

    model_config = ConfigDict(
        title="Данные токена"
    )
