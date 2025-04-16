import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..courses.models import CoursesORM


from ..database import Base



class CoursesStructureORM(Base):
    __tablename__ = "courses_structure"

    course_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("courses.id", ondelete="CASCADE"),
        primary_key=True
    )
    structure: Mapped[dict] = mapped_column(JSONB, nullable=False)

    course: Mapped["CoursesORM"] = relationship(
        "CoursesORM",
        back_populates="structure"
    )
