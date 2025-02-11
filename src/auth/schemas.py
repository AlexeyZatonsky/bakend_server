from pydantic import BaseModel, EmailStr, Field, ConfigDict

from uuid import UUID, uuid4

from fastapi_users import schemas




class UserRead(schemas.BaseUser[UUID]):
    id: UUID
    email: EmailStr
    username: str = Field(min_length=3, max_length=255)
    hashed_password: str
    is_verified: bool | None = False
    is_active: bool = True
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra = {
            "example": {
                "id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
                "email": "user@example.com",
                "username": "johndoe",
                "is_active": True,
                "is_verified": False,
            }
        }
    )

class UserCreate(schemas.BaseUserCreate):
    id: UUID | None = None
    email: EmailStr
    username: str = Field(max_length=255)
    password: str
    is_active: bool | None = True
    is_superuser: bool | None = False
    is_verified: bool | None = False

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "username": "johndoe",
                "password": "strongpassword123"
            }
        }
    )