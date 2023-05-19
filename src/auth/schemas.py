from pydantic import BaseModel, EmailStr, Field

from uuid import UUID, uuid4

from fastapi_users import schemas




class UserRead(schemas.BaseUser[UUID]):
    id: UUID
    email: EmailStr
    username: str = Field(min_length=3, max_length=255)
    hashed_password: str
    is_verified: bool | None = False
    is_active: bool = True
    

    class Config:
        orm_mode = True

class UserCreate(schemas.BaseUserCreate):
    id: UUID | None = None
    email: EmailStr
    username: str = Field(max_length=255)
    password: str
    is_active: bool | None = True
    is_superuser: bool | None = False
    is_verified: bool | None = False