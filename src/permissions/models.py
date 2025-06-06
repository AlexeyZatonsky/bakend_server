from datetime import datetime, UTC
import uuid
from enum import Enum

from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import ENUM as PgEnum, UUID

from ..database import Base

from ..auth.models import UsersORM
from ..courses.models import CoursesORM

from ..core.Enums.PermissionsEnum import PermissionsEnum



class PermissionsORM(Base):
    __tablename__ = "permissions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(UsersORM.id, ondelete="CASCADE"),
        primary_key=True
    )
    course_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(CoursesORM.id, ondelete="CASCADE"),
        primary_key=True
    )

    access_level: Mapped[PermissionsEnum] = mapped_column(
        PgEnum(
            PermissionsEnum,
            name="access_level_enum",
            values_callable=lambda e: [f.value for f in e],
        ),
        nullable=False,
        default=PermissionsEnum.STUDENT
    )

    granted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.now(UTC)
    )
    expiration_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
