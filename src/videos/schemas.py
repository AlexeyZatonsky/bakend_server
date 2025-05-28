from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict, field_serializer
from uuid import UUID

from ..settings.config import S3_ENV

from ..core.Enums.ExtensionsEnums import ImageExtensionsEnum, VideoExtensionsEnum


import logging
from ..core.log import configure_logging

logger = logging.getLogger(__name__)
configure_logging()


class BaseVideoDataSchema(BaseModel):
    id: UUID
    user_id: UUID = Field(description="ID пользователя")
    course_id: Optional[UUID] = Field(description="ID курса")
    channel_id: str = Field(description="ID канала")
    
    video_url: str = Field(description="URL видео")
    preview_url: Optional[str] = Field(description="URL превью видео")
    
    video_ext: VideoExtensionsEnum = Field(description="Расширение видео", exclude=True)
    preview_ext: Optional[ImageExtensionsEnum] = Field(description="Расширение превью видео", exclude=True)
    
    name: str = Field(description="Название видео")
    description: str = Field(description="Описание видео")
    is_free: bool = Field(description="Доступно для всех")
    is_public: bool = Field(description="Публичное видео")
    timeline: int = Field(description="Временная шкала видео")
    upload_date: datetime = Field(description="Дата загрузки видео")
    
    
    
    
class VideoDataCreateSchema(BaseVideoDataSchema): pass

class VideoDataReadSchema(BaseVideoDataSchema): 
    model_config = ConfigDict(from_attributes=True)
    
    @field_serializer("video_url", when_used="json")
    def get_video_url(self, video_url: str) -> str | None:
        logger.debug(f"video_url: {video_url}")
        
        ext_value = self.video_ext.value # mp4
        base_url = S3_ENV.BASE_SERVER_URL
        return f"{base_url}/minio/{self.user_id}/channels/{self.channel_id}/videos/{self.id}/video.{ext_value}"
    
    @field_serializer("preview_url", when_used="json")
    def _get_full_preview_url(self, preview_url) -> str | None:
        logger.debug(f"preview_url: {preview_url}, preview_ext: {self.preview_ext}")
        
        # Если avatar_ext есть, используем его для формирования URL
        if self.preview_ext:
            if isinstance(self.preview_ext, ImageExtensionsEnum):
                ext_value = self.preview_ext.value
            else:
                ext_value = self.preview_ext
            
            base_url = S3_ENV.BASE_SERVER_URL
            return f"{base_url}/minio/{self.user_id}/channels/{self.channel_id}/videos/{self.id}/video_preview.{ext_value}"
        
        return None
    
    

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
    
    





