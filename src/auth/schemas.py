from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict, validator
from uuid import UUID
from typing import Optional

# Добавляем схему для логина
class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str

class UserBaseSchema(BaseModel):
    """Базовая схема пользователя"""
    username: str = Field(..., min_length=3, max_length=255, description="Имя пользователя")
    avatar: Optional[str] = Field(None, max_length=1000, description="URL аватара пользователя")
    is_verified: bool = Field(default=False, description="Статус верификации пользователя")
    is_active: bool = Field(default=True, description="Активность пользователя")

class UserReadSchema(BaseModel):
    """Схема для чтения данных пользователя"""
    id: UUID
    username: str
    avatar: str | None = None
    is_verified: bool = False
    is_active: bool = True
    email: str  # Добавляем email для создания токена
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            UUID: str
        }

class UserCreateSchema(BaseModel):
    """Схема для создания пользователя"""
    email: EmailStr = Field(..., description="Email пользователя")
    password: str = Field(..., min_length=8, description="Пароль пользователя")

    @validator('password')
    def validate_password_strength(cls, v):
        if not any(char.isdigit() for char in v):
            raise ValueError('Пароль должен содержать хотя бы одну цифру')
        if not any(char.isupper() for char in v):
            raise ValueError('Пароль должен содержать хотя бы одну заглавную букву')
        return v

class UserUpdateSchema(BaseModel):
    """Схема для обновления данных пользователя"""
    username: Optional[str] = Field(None, min_length=3, max_length=255)
    avatar: Optional[str] = Field(None, max_length=1000)
    phone_number: Optional[str] = Field(None, max_length=15)
    INN: Optional[str] = Field(None, max_length=12)
    organization_name: Optional[str] = Field(None, max_length=255)
    is_verified: Optional[bool] = None
    is_active: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)

class TokenSchema(BaseModel):
    """Схема токена доступа"""
    access_token: str = Field(..., description="JWT токен доступа")
    token_type: str = Field(default="bearer", description="Тип токена")

class TokenDataSchema(BaseModel):
    """Схема данных токена"""
    email: Optional[EmailStr] = None
    user_id: Optional[UUID] = None
