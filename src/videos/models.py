import uuid
from datetime import datetime, UTC

from sqlalchemy import ForeignKey, Integer, String, Table,  DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, ENUM as PgEnum

from ..settings.config import S3_ENV
from ..database import Base

from ..auth.models import UsersORM
from ..courses.models import CoursesORM
from ..channels.models import ChannelsORM
from ..core.Enums.ExtensionsEnums import ImageExtensionsEnum, VideoExtensionsEnum


class CategoryORM(Base):
    __tablename__ = 'categories'
    id: Mapped[int] = mapped_column(Integer, primary_key=True) 
    name: Mapped[str] = mapped_column(String(255), nullable=False) 

class TagORM(Base):
    __tablename__ = 'tags'
    id: Mapped[int] = mapped_column(Integer, primary_key=True) 
    name: Mapped[str] = mapped_column(String(255), nullable=False) 

class VideoORM(Base):
    __tablename__ = 'videos'
    
    id:         Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), default=uuid.uuid4, primary_key=True
    )
    user_id:    Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey(UsersORM.id, ondelete='CASCADE'), nullable=False
    )
    course_id:  Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey(CoursesORM.id, ondelete='CASCADE'), nullable=True
    )
    channel_id: Mapped[str] = mapped_column(
        String(255), ForeignKey(ChannelsORM.id, ondelete='CASCADE'), nullable=False
    ) 


    video_ext: Mapped[VideoExtensionsEnum] = mapped_column(
        PgEnum(
            VideoExtensionsEnum,
            name="video_extensions_enum",
            value_callable = lambda e: e.value,
            nullable = False,
            create_type=False
        ),
        nullable=False,
        default=VideoExtensionsEnum.MP4
    )
    preview_ext: Mapped[ImageExtensionsEnum] = mapped_column(
        PgEnum(
            ImageExtensionsEnum,
            name="image_extensions_enum",
            value_callable = lambda e: e.value,
            nullable = True
        ),
        nullable=True,
        default=None
    )
    name:           Mapped[str] = mapped_column(String(255), nullable=False) 
    description:    Mapped[str] = mapped_column(String(1000), nullable=True) 
    is_free:        Mapped[bool] = mapped_column(Boolean, default=True) 
    is_public:      Mapped[bool] = mapped_column(Boolean, default=True) 
    timeline:       Mapped[int] = mapped_column(Integer, default=0) 
    upload_date:    Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False
    )
    
    @property
    def video_url(self) -> str:
        return (
            f"{S3_ENV.public_url}" \
            f"/{self.user_id}" \
            f"/channels/{self.channel_id}"\
            f"/videos/{self.id}/video.{self.video_ext}"
        )

    @property
    def preview_url(self) -> str | None:
        if not self.preview_ext:
            return None
        return (
            f"{S3_ENV.public_url}" \
            f"/{self.user_id}" \
            f"/channels/{self.channel_id}"\
            f"/videos/{self.id}/preview.{self.preview_ext.value}"
        )


class VideoMetadatasORM(Base):
    __tablename__ = 'video_metadatas'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey(VideoORM.id, ondelete='CASCADE'), primary_key=True
    ) 

    views: Mapped[int] = mapped_column(Integer, default=0) 
    likes: Mapped[int] = mapped_column(Integer, default=0) 
    dislikes: Mapped[int] = mapped_column(Integer, default=0) 
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False
    ) 



class VideoTagOrm(Base):
    __tablename__ = "video_tags"

    video_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey(VideoORM.id, ondelete='CASCADE'), primary_key=True
    )
    tag_id: Mapped[Integer] = mapped_column(
        Integer, ForeignKey(TagORM.id, ondelete='CASCADE'), primary_key=True
    )


class VideoCategoryORM(Base):
    __tablename__ = "video_categories"

    video_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey(VideoORM.id, ondelete='CASCADE'), primary_key=True
    )
    category_id: Mapped[Integer] = mapped_column(
        Integer, ForeignKey(CategoryORM.id, ondelete='CASCADE'), primary_key=True
    )
