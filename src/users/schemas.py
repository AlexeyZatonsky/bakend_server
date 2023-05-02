from pydantic import BaseModel
from pydantic import constr
from pydantic import EmailStr
from datetime import datetime



class BaseUser(BaseModel):
    id: int
    email: EmailStr
    username: constr(regex="^[A-Za-z0-9-_]+$", to_lower=True, strip_whitespace=True)
    registrated_at: datetime
    is_verified: bool | None = False