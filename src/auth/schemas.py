from pydantic import BaseModel, EmailStr, Field

from uuid import UUID, uuid4

from fastapi_users import schemas


class BaseUser(BaseModel):
    id: UUID
    email: EmailStr
    username: str = Field(min_length=3, max_length=255)
    is_verified: bool | None = False
    


class UserRead(schemas.BaseUser[UUID]):
    id: UUID
    email: EmailStr
    username: str = Field(min_length=3, max_length=255)
    is_verified: bool | None = False
    

    class Config:
        orm_mode = True

class UserCreate(schemas.BaseUserCreate):
    id: UUID
    username: str = Field(min_length=3, max_length=255)
    email: EmailStr
    is_verified: bool | None = False
    hashed_password: str