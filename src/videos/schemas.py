from pydantic import  BaseModel, HttpUrl ,Field

from uuid import UUID, uuid4
from datetime import datetime




class ReadCategory(BaseModel):
    id: int
    name: str

class CreateCategory(BaseModel):
    name: str = Field(max_length=255)



class ReadTag(BaseModel):
    id: int
    name: str

class CreateTag(BaseModel):
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


class UploadVideo(BaseModel):
    title: str = Field(max_length=255)
    description: str = Field(max_length=1000)

class AboutVideo(BaseModel):
    id: UUID
    title: str
    description: str
    url: str
    upload_date: datetime
    views: int
    likes: int
    dislikes: int
    user_id: UUID
    category_id: int | None = 0


class BaseVideoTag(BaseModel):
    video_id: UUID
    tag_id: int  
 


