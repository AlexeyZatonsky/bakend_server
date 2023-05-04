from pydantic import BaseModel, EmailStr, constr

from uuid import UUID, uuid4
from datetime import datetime



class BaseUser(BaseModel):
    id: UUID
    email: EmailStr
    username: constr(regex="^[A-Za-z0-9-_]+$", to_lower=True, strip_whitespace=True)
    registrated_at: datetime
    is_verified: bool | None = False
    hashed_password: str