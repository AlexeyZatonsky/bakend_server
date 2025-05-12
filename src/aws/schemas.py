from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

from ..core.Enums.MIMETypeEnums import  ImageMimeEnum



class BaseUploadRequestSchema(BaseModel):
    file_name: str = Field(alias="fileName", description="Имя файла с расширением")
    model_config = ConfigDict(populate_by_name=True)


class UserAvatarUploadRequestSchema(BaseUploadRequestSchema):
    content_type: ImageMimeEnum = Field(alias="contentType")

class UserAvatarUploadResponseSchema(BaseModel):
    upload_url: str
    key: str
    public_url: str


class UploadURLResponseSchema(BaseModel):
    upload_url: str
    key: str


class ChannelAvatarUploadRequestSchema(BaseUploadRequestSchema):
    channel_id: str = Field(alias="channelID")


class VideoUploadRequestSchema(BaseUploadRequestSchema):
    channel_id: str
    video_id: UUID = Field(alias="videoID")