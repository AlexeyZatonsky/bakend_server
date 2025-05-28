from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, HttpUrl
from typing import List

from ..core.Enums.MIMETypeEnums import ImageMimeEnum, VideoMimeEnum


class BaseUploadRequestSchema(BaseModel):
    file_name: str = Field(alias="fileName")
    model_config = ConfigDict(populate_by_name=True)


class UserAvatarUploadRequestSchema(BaseUploadRequestSchema):
    content_type: ImageMimeEnum = Field(alias="contentType")


class ChannelAvatarUploadRequestSchema(BaseUploadRequestSchema):
    content_type: ImageMimeEnum = Field(alias="contentType")


class ChannelPreviewUploadRequestSchema(BaseUploadRequestSchema):
    content_type: ImageMimeEnum = Field(alias="contentType")


class CoursePreviewUploadRequestSchema(BaseUploadRequestSchema):
    content_type: ImageMimeEnum = Field(alias="contentType")



class VideoUploadRequestSchema(BaseModel):
    file_name: str
    content_type: VideoMimeEnum


class VideoPreviewUploadRequestSchema(BaseModel):
    file_name: str
    content_type: ImageMimeEnum


class BaseUploadResponseSchema(BaseModel):
    upload_url: HttpUrl
    key: str
    public_url: HttpUrl


class UserAvatarUploadResponseSchema(BaseUploadResponseSchema):
    pass


class ChannelAvatarUploadResponseSchema(BaseUploadResponseSchema):
    pass


class ChannelPreviewUploadResponseSchema(BaseUploadResponseSchema):
    pass


class CoursePreviewUploadResponseSchema(BaseUploadResponseSchema):
    pass


class VideoUploadResponseSchema(BaseUploadResponseSchema):
    video_id: UUID


class VideoPreviewUploadResponseSchema(BaseUploadResponseSchema):
    pass
