import uuid
from datetime import datetime, UTC

from sqlalchemy import Boolean, String, Integer, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship


from ..database import Base

from ..auth.models import UsersORM
from ..channels.models import ChannelsORM
from ..courses_structure.models import CoursesStructureORM

class CoursesORM(Base):
    __tablename__ = "courses"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    channel_id: Mapped[str] = mapped_column(String, ForeignKey(ChannelsORM.id, ondelete="CASCADE"))
    owner_id: Mapped[UUID] = mapped_column(UUID, ForeignKey(UsersORM.id, ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(255))
    is_public: Mapped[bool] = mapped_column(Boolean, default=True)
    student_count: Mapped[int] = mapped_column(Integer, default=0)
    preview: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now(UTC), onupdate=datetime.now(UTC))

    structure: Mapped["CoursesStructureORM"] = relationship(
        "CoursesStructureORM",
        back_populates="course",
        cascade="all, delete-orphan",
        uselist=False
    )
