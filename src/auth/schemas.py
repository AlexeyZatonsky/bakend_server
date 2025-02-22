from pydantic import BaseModel, EmailStr, Field, ConfigDict
from uuid import UUID
from typing import Optional

# Добавляем схему для логина
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserRead(BaseModel):
    id: UUID
    username: str
    avatar: Optional[str] = None
    is_verified: bool

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
                "username": "johndoe",
            }
        }
    )

class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=8)

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "username": "johndoe",
                "password": "strongpassword123"
            }
        }
    )
