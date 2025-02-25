from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional

class ChannelBase(BaseModel):
    unique_name: str = Field(min_length=1, max_length=255)
    avatar: Optional[str] = None
    subscribers_count: int = Field(default=0)

class ChannelCreate(ChannelBase):
    pass

class ChannelRead(ChannelBase):
    owner_id: UUID

    class Config:
        from_attributes = True