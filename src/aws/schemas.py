from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
from typing import List
from pydantic import HttpUrl

from ..core.Enums.MIMETypeEnums import  ImageMimeEnum, VideoMimeEnum



class BaseUploadRequestSchema(BaseModel):
    file_name: str = Field(alias="fileName", description="Имя файла с расширением")
    model_config = ConfigDict(populate_by_name=True)


class UserAvatarUploadRequestSchema(BaseUploadRequestSchema):
    content_type: ImageMimeEnum = Field(alias="contentType")


class ChannelAvatarUploadRequestSchema(BaseUploadRequestSchema):
    pass

class VideoUploadRequestSchema(BaseModel):
    """Схема запроса на получение URL для загрузки видео"""
    file_name: str = Field(..., description="Имя загружаемого файла")
    content_type: VideoMimeEnum = Field(..., description="MIME-тип контента")

    model_config = ConfigDict(
        title="Запрос на загрузку видео",
        json_schema_extra={
            "example": {
                "file_name": "lecture.mp4",
                "content_type": "video/mp4",
            }
        }
    )





class BaseUploadResponseSchema(BaseModel):
    upload_url: str
    key: str
    public_url: str


class UserAvatarUploadResponseSchema(BaseUploadResponseSchema):
    pass

class ChannelAvatarUploadResponseSchema(BaseUploadResponseSchema):
    pass

class VideoUploadResponseSchema(BaseModel):
    """Схема ответа с URL для загрузки видео"""
    upload_url: HttpUrl = Field(..., description="URL для загрузки видео")
    key: str = Field(..., description="Ключ объекта в хранилище")
    public_url: HttpUrl = Field(..., description="Публичный URL для доступа к видео")
    video_id: UUID = Field(..., description="Идентификатор созданного видео")
    
    model_config = ConfigDict(
        title="Ответ на запрос загрузки видео",
        json_schema_extra={
            "example": {
                "upload_url": "https://s3.example.com/upload/key",
                "key": "123e4567-e89b-12d3-a456-426614174000/videos/video.mp4",
                "public_url": "http://example.com/123e4567-e89b-12d3-a456-426614174000/videos/video.mp4",
                "video_id": "123e4567-e89b-12d3-a456-426614174000" 
            }
        }
    )

class VideoPreviewUploadRequestSchema(BaseModel):
    """Схема запроса на получение URL для загрузки превью видео"""
    file_name: str = Field(..., description="Имя загружаемого файла")
    content_type: str = Field(..., description="MIME-тип контента")
    video_id: UUID = Field(..., description="Идентификатор видео")
    
    model_config = ConfigDict(
        title="Запрос на загрузку превью видео",
        json_schema_extra={
            "example": {
                "file_name": "preview.jpg",
                "content_type": "image/jpeg",
                "video_id": "123e4567-e89b-12d3-a456-426614174000",
            }
        }
    )

class VideoPreviewUploadResponseSchema(BaseModel):
    """Схема ответа с URL для загрузки превью видео"""
    upload_url: HttpUrl = Field(..., description="URL для загрузки превью")
    key: str = Field(..., description="Ключ объекта в хранилище")
    public_url: HttpUrl = Field(..., description="Публичный URL для доступа к превью")
    
    model_config = ConfigDict(
        title="Ответ на запрос загрузки превью видео",
        json_schema_extra={
            "example": {
                "upload_url": "https://s3.example.com/upload/key",
                "key": "123e4567-e89b-12d3-a456-426614174000/videos/preview.jpg",
                "public_url": "http://example.com/123e4567-e89b-12d3-a456-426614174000/videos/preview.jpg"
            }
        }
    )

class VideoDetailsUpdateSchema(BaseModel):
    """Схема для обновления информации о видео после загрузки"""
    video_id: UUID = Field(..., description="Идентификатор видео")
    title: str = Field(..., max_length=255, description="Название видео")
    description: str = Field(..., max_length=1000, description="Описание видео")
    category_id: int = Field(..., description="ID категории видео")
    tags: List[int] = Field([], description="Список ID тегов")
    
    model_config = ConfigDict(
        title="Обновление информации о видео",
        json_schema_extra={
            "example": {
                "video_id": "123e4567-e89b-12d3-a456-426614174000",
                "title": "Введение в Python",
                "description": "Базовый курс по Python для начинающих",
                "category_id": 1,
                "tags": [1, 2, 3]
            }
        }
    )





