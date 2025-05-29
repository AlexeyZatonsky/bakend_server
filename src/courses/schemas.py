from datetime import datetime
from uuid import UUID
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict, field_serializer

from ..settings.config import S3_ENV
from ..core.Enums.ExtensionsEnums import ImageExtensionsEnum


import logging
from ..core.log import configure_logging

logger = logging.getLogger(__name__)
configure_logging()



# Работа с непосредственно самими курсами
class CourseBaseSchema(BaseModel):
    pass
    

class CourseCreateSchema(CourseBaseSchema): 
    name: str = Field(..., min_length=1, max_length=100, description="Название курса")
    is_public: bool = Field(default=True, description="Является ли курс общедоступным")


class CourseUpdateSchema(CourseBaseSchema):
    name: Optional[str] = Field(default = None, min_length=1, max_length=100, description="Название курса")
    is_public: Optional[bool] = Field(default=True, description="Является ли курс общедоступным")


class CourseReadSchema(CourseBaseSchema):
    id: UUID = Field(description="Уникальный идентификатор курса")
    channel_id: str = Field(description="Идентификатор канала, к которому привязан курс")
    owner_id: UUID = Field(description="ID владельца курса")
    name: str = Field(min_length=1, max_length=100, description="Название курса")
    is_public: bool = Field(description="Является ли курс общедоступным")
    student_count: int = Field(description="Количество студентов, записанных на курс")

    preview_url: Optional[str] = None     
    preview_ext: Optional[ImageExtensionsEnum] = Field(None, exclude=True)  # Скрытое поле с расширением


    created_at: datetime = Field(description="Дата и время создания курса")
    updated_at: datetime = Field(description="Дата и время последнего обновления курса")

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("preview_url", when_used="json")
    def _get_full_preview_url(self, preview_url) -> str | None:
        logger.debug(f"preview_url: {preview_url}, preview_ext: {self.preview_ext}")
        
        if self.preview_ext:
            if isinstance(self.preview_ext, ImageExtensionsEnum):
                ext_value = self.preview_ext.value
            else:
                ext_value = self.preview_ext
            
            base_url = S3_ENV.BASE_SERVER_URL
            return f"{base_url}/minio/{self.owner_id}/channels/{self.channel_id}/courses/{self.id}/course_preview.{ext_value}"
        
        return None