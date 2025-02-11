from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID



class ChannelRead(BaseModel):
    id: UUID
    title: str = Field(min_length=3, max_length=255)
    user_id: UUID

    model_config = ConfigDict(from_attributes=True)
    


class ChannelCreate(BaseModel):
    title: str
    user_id: UUID = None