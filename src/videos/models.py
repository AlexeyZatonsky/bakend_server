import uuid
from datetime import datetime, UTC

from sqlalchemy import ForeignKey, Integer, String, Table,  DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from ..database import Base

from ..auth.models import UsersORM
from ..courses.models import CoursesORM
from ..channels.models import ChannelsORM



class CategoryORM(Base):
    __tablename__ = 'category'
    id: Mapped[int] = mapped_column(Integer, primary_key=True) 
    name: Mapped[str] = mapped_column(String(255), nullable=False) 

class TagORM(Base):
    __tablename__ = 'tag'
    id: Mapped[int] = mapped_column(Integer, primary_key=True) 
    name: Mapped[str] = mapped_column(String(255), nullable=False) 

class VideoORM(Base):
    __tablename__ = 'video'
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), default=uuid.uuid4, primary_key=True
    )

    course_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey(CoursesORM.id, ondelete='CASCADE'), nullable=True
    )
    channel_id: Mapped[str] = mapped_column(
        String(255), ForeignKey(ChannelsORM.id, ondelete='CASCADE'), nullable=False
    ) 


    preview: Mapped[str] = mapped_column(String(1000), nullable=False) 
    title: Mapped[str] = mapped_column(String(255), nullable=False) 
    description: Mapped[str] = mapped_column(String(1000), nullable=False) 
    url: Mapped[str] = mapped_column(String, nullable=False) 
    is_free: Mapped[bool] = mapped_column(Boolean, default=True) 
    is_public: Mapped[bool] = mapped_column(Boolean, default=True) 
    timeline: Mapped[int] = mapped_column(Integer, default=0) 
    upload_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(UTC)) 

class VideoMetadatasORM(Base):
    __tablename__ = 'video_metadatas'

    video_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey(VideoORM.id, ondelete='CASCADE'), primary_key=True
    ) 

    views: Mapped[int] = mapped_column(Integer, default=0) 
    likes: Mapped[int] = mapped_column(Integer, default=0) 
    dislikes: Mapped[int] = mapped_column(Integer, default=0) 
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(UTC)) 



class VideoTagOrm(Base):
    __tablename__ = "video_tag"

    video_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey(VideoORM.id, ondelete='CASCADE'), primary_key=True
    )
    tag_id: Mapped[Integer] = mapped_column(
        Integer, ForeignKey(TagORM.id, ondelete='CASCADE'), primary_key=True
    )


