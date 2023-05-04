from pydantic import BaseModel, Field

from uuid import UUID, uuid4



class BaseChannel(BaseModel): 
    id: UUID
    title: str
    user_id: UUID