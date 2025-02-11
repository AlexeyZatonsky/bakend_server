from pydantic import  BaseModel, HttpUrl ,Field, ConfigDict

from uuid import UUID, uuid4
from datetime import datetime




class CategoryRead(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)

class CategoryCreate(BaseModel):
    name: str = Field(max_length=255)



class TagRead(BaseModel):
    id: int
    name: str
    
    model_config = ConfigDict(from_attributes=True)

class TagCreate(BaseModel):
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

    model_config = ConfigDict(from_attributes=True)

class VidoeUpload(BaseModel):
    title: str = Field(max_length=255)
    description: str = Field(max_length=1000)
    category_id: str = '1'


class AboutVideo(BaseModel):
    id: UUID
    title: str
    description: str
    path: str
    upload_date: datetime
    views: int
    likes: int
    dislikes: int
    user_id: UUID
    category_id: int

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra = {
            "example": {
                "id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
                "title": "My Video",
                "description": "Video description",
                "path": "/videos/my-video.mp4",
                "upload_date": "2024-03-14T12:00:00",
                "views": 0,
                "likes": 0,
                "dislikes": 0,
                "user_id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
                "category_id": 1
            }
        }
    )


class BaseVideoTag(BaseModel):
    video_id: UUID
    tag_id: int

    model_config = ConfigDict(from_attributes=True)



