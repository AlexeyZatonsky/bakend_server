from pydantic import  BaseModel, HttpUrl ,Field

from uuid import UUID, uuid4
from datetime import datetime




class BaseCategory(BaseModel):
    id: int
    name: str = Field(max_length=255)


class BaseTag(BaseModel):
    id: int
    name: str = Field(max_length=255)

    

class BaseVideo(BaseModel):
    id: UUID
    title: str = Field(max_length=255)
    description: str = Field(max_length=1000)
    url: HttpUrl
    upload_date: datetime
    views: int | None = 0
    likes: int | None = 0
    dislikes: int | None = 0
    user_id: UUID
    category_id: int


class BaseVideoTag(BaseModel):
    video_id: UUID
    tag_id: int  
 


