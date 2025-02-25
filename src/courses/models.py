from sqlalchemy import Column, ForeignKey, Integer, MetaData, String, UUID, TIMESTAMP, JSON
from sqlalchemy.ext.declarative import declarative_base
import uuid
from datetime import datetime

from ..auth.models import Users
from ..channels.models import Channels

from ..database import Base

channels_metadata = MetaData()


class Corses(Base):
    __tablename__ = "courses"

    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    channel_id =  Column(String, ForeignKey('channels.unique_name', ondelete='CASCADE'))
    name = Column(String(255))
    student_count = Column(Integer, default=0)
    preview = Column(String(1000), nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow)
    
class CoursesStructure(Base):
    __tablename__ = "courses_structure"
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id", ondelete="CASCADE"), primary_key=True)
    structutre = Column(JSON(), nullable=False)
