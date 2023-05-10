from pydantic import BaseModel, Field

from uuid import UUID, uuid4



class BaseChannel(BaseModel): 
    id: UUID
    title: str
    user_id: UUID


class ChannelRead(BaseChannel):

    class Config:
        orm_mode=True
    


class ChannelCreat(BaseModel):
    id: UUID
    title: str = Field(min_length=3, max_length=255)
    user_id: UUID