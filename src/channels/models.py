from sqlalchemy import Column, ForeignKey, Integer, MetaData, String, UUID
from sqlalchemy.ext.declarative import declarative_base
import uuid

from ..auth.models import Users
from ..database import Base


channels_metadata = MetaData()

class Channels(Base):
    __tablename__ = 'channels'

    unique_name = Column(String(255), unique=True, primary_key=True)
    owner_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    avatar = Column(String(1000), nullable=True)
    subscribers_count = Column(Integer, default=0, nullable=False)
