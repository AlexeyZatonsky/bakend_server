from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID

from ..core.Enums.ExtensionsEnums import ImageExtensionsEnum, VideoExtensionsEnum


class BaseVideoDataSchema(BaseModel):
    id: UUID
    user_id: UUID = Field(description="ID пользователя")
    course_id: Optional[UUID] = Field(description="ID курса")
    channel_id: str = Field(description="ID канала")
    
    video_ext: VideoExtensionsEnum = Field(description="Расширение видео")
    preview_ext: Optional[ImageExtensionsEnum] = Field(description="Расширение превью видео")
    
    description: str = Field(description="Описание видео")
    is_free: bool = Field(description="Доступно для всех")
    is_public: bool = Field(description="Публичное видео")
    timeline: int = Field(description="Временная шкала видео")
    upload_date: datetime = Field(description="Дата загрузки видео")
    
    
class VideoDataCreateSchema(BaseVideoDataSchema): pass

class VideoDataReadSchema(BaseVideoDataSchema): 
    model_config = ConfigDict(from_attributes=True)
    

class VideoDataUpdateSchema(BaseModel):
    name: str = Field(description="Название видео")
    description: str = Field(description="Описание видео")
    is_free: bool = Field(description="Доступно для всех", default=True)
    is_public: bool = Field(description="Публичное видео", default=True)
    timeline: int = Field(description="Временная шкала видео")



class TagBaseSchema(BaseModel):
    id: int
    name: str
    
class TagCreateSchema(TagBaseSchema): pass
class TagReadSchema(TagBaseSchema):
    model_config = ConfigDict(from_attributes=True)    

class TagUpdateSchema(TagBaseSchema): pass
    


class VideoTagBaseSchema(BaseModel):
    id: int
    video_id: UUID
    tag_id: int
    

class VideoMetadataBaseSchema(BaseModel):
    id: UUID
    views: int
    likes: int
    dislikes: int 
    updated_at: datetime
    

class VideoMetadataCreateSchema(VideoMetadataBaseSchema): pass
class VideoMetadataReadSchema(VideoMetadataBaseSchema):
    model_config = ConfigDict(from_attributes=True)
    
    





