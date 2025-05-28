from pydantic import BaseModel, Field, ConfigDict, field_serializer
from uuid import UUID
from typing import Optional

from ..core.Enums.ExtensionsEnums import ImageExtensionsEnum
from ..settings.config import S3_ENV

import logging
from ..core.log import configure_logging

logger = logging.getLogger(__name__)
configure_logging()

class ChannelBaseSchema(BaseModel):
    id: str = Field(min_length=1, max_length=255)
    

class ChannelCreateSchema(ChannelBaseSchema):
    pass

class ChannelReadSchema(ChannelBaseSchema):
    owner_id: UUID
    subscribers_count: int = Field(default=0)

    avatar_ext: Optional[ImageExtensionsEnum] = Field(None, exclude=True)  # Скрытое поле с расширением
    preview_ext: Optional[ImageExtensionsEnum] = Field(None, exclude=True)  # Скрытое поле с расширением
    
    avatar_url: Optional[str] = None  # Публичное поле для URL аватара
    preview_url: Optional[str] = None


    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    
    @field_serializer("avatar_url", when_used="json")
    def _get_full_avatar_url(self, avatar_url) -> str | None:
        logger.debug(f"avatar_url: {avatar_url}, avatar_ext: {self.avatar_ext}")
        
        if self.avatar_ext:
            if isinstance(self.avatar_ext, ImageExtensionsEnum):
                ext_value = self.avatar_ext.value
            else:
                ext_value = self.avatar_ext
            
            base_url = S3_ENV.BASE_SERVER_URL
            return f"{base_url}/minio/{self.owner_id}/channels/{self.id}/channel_avatar.{ext_value}"
        
        return None
    
    @field_serializer("preview_url", when_used="json")
    def _get_full_preview_url(self, preview_url) -> str | None:
        logger.debug(f"preview_url: {preview_url}, preview_ext: {self.preview_ext}")
        
        if self.preview_ext:
            if isinstance(self.preview_ext, ImageExtensionsEnum):
                ext_value = self.preview_ext.value
            else:
                ext_value = self.preview_ext
            
            base_url = S3_ENV.BASE_SERVER_URL
            return f"{base_url}/minio/{self.owner_id}/channels/{self.id}/channel_preview.{ext_value}"
        
        return None