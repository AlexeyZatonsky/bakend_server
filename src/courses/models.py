import uuid
from datetime import datetime, UTC

from sqlalchemy import String, Integer, ForeignKey, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base

from ..channels.models import ChannelsORM


class CoursesORM(Base):
    __tablename__ = "courses"

    id : Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), default=uuid.uuid4, primary_key=True
    )

    channel_name : Mapped[str] = mapped_column(
        String, ForeignKey(ChannelsORM.unique_name, ondelete='CASCADE')
    )

    name : Mapped[str] = mapped_column(String(255))
    student_count : Mapped[int] = mapped_column(Integer, default=0)
    preview : Mapped[str | None] = mapped_column(String(1000), nullable=True)
    created_at : Mapped[datetime] = mapped_column(DateTime, default=datetime.now(UTC), nullable=False)
    
    updated_at : Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC), nullable=False
        )
    
class CoursesStructureORM(Base):
    __tablename__ = "courses_structure"
   
    course_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey(CoursesORM.id, ondelete="CASCADE"), primary_key=True
    )
    structutre: Mapped[JSON] = mapped_column(JSON(), nullable=False)