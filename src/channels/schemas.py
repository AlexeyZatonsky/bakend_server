from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from typing import Optional

class ChannelBase(BaseModel):
    unique_name: str = Field(min_length=1, max_length=255)
    avatar: Optional[str] = None
    

class ChannelCreate(ChannelBase):
    pass

class ChannelRead(ChannelBase):
    owner_id: UUID
    subscribers_count: int = Field(default=0)

    model_config = ConfigDict(from_attributes=True)