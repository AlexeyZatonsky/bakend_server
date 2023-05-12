from sqlalchemy import ARRAY, Column, ForeignKey, Integer, MetaData, String, Table, UUID, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base

import uuid
from datetime import datetime

from ..auth.models import User




videos_metadata = MetaData()

Base = declarative_base(metadata=videos_metadata)


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
    title = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=False)
    url = Column(String(255), nullable=False)
    upload_date = Column(TIMESTAMP, default=datetime.utcnow)
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    dislikes = Column(Integer, default=0)
    user_id = Column(UUID(as_uuid=True), ForeignKey(User.id))
    category_id = Column(Integer, ForeignKey(Category.id))



video_tag = Table('video_tag', videos_metadata,
    Column('video_id', UUID(as_uuid=True), ForeignKey(Video.id)),
    Column('tag_id', Integer, ForeignKey(Tag.id)),
)
