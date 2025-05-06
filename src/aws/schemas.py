from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field




class BaseUploadRequestSchema(BaseModel):
    file_name: str = Field(alias="fileName", description="Имя файла с расширением")
    content_type: str = Field(alias="contentType", description="MIME-тип файлов")

    model_config = ConfigDict(populate_by_name=True)


class UserAvatarUploadRequestSchema(BaseUploadRequestSchema):
    user_id: UUID = Field(alias="userID")

class UserAvatarUploadResponseSchema(BaseUploadRequestSchema):
    upload_url: str
    key: str


class UploadURLResponseSchema(BaseModel):
    upload_url: str
    key: str


class ChannelAvatarUploadRequestSchema(BaseUploadRequestSchema):
    channel_id: str = Field(alias="channelID")


class VideoUploadRequestSchema(BaseUploadRequestSchema):
    channel_id: str
    video_id: UUID = Field(alias="videoID")