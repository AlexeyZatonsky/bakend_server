from pydantic import BaseModel, Field


from uuid import UUID



class ChannelRead(BaseModel):
    id: UUID
    title: str = Field(min_length=3, max_length=255)
    user_id: UUID
    class Config:
        orm_mode=True
    


class ChannelCreate(BaseModel):
    title: str
    user_id: UUID = None