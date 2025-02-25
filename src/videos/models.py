from sqlalchemy import Column, ForeignKey, Integer, String, Table, UUID, TIMESTAMP, Boolean
import uuid
from datetime import datetime

from ..auth.models import Users
from ..database import Base


class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)

class Tag(Base):
    __tablename__ = 'tag'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)

class Video(Base):
    __tablename__ = 'video'
    
    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    preview = Column(String(1000), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=False)
    url = Column(String, nullable=False)
    is_free = Column(Boolean, default=True)
    is_public = Column(Boolean, default=True)
    course_id = Column(UUID(as_uuid=True), ForeignKey('courses.id', ondelete='CASCADE'), nullable=True)
    channel_name = Column(String(255), ForeignKey('channels.unique_name', ondelete='CASCADE'), nullable=False)
    timeline = Column(Integer, default=0)
    upload_date = Column(TIMESTAMP, default=datetime.utcnow)

class VideoMetadatas(Base):
    __tablename__ = 'video_metadatas'

    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    video_id = Column(UUID(as_uuid=True), ForeignKey('video.id', ondelete='CASCADE'), nullable=False)
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    dislikes = Column(Integer, default=0)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow)

video_tag = Table('video_tag', Base.metadata,
    Column('video_id', UUID(as_uuid=True), ForeignKey('video.id', ondelete='CASCADE')),
    Column('tag_id', Integer, ForeignKey('tag.id', ondelete='CASCADE'))
)
