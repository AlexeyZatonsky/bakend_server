from datetime import datetime, UTC
import uuid
from enum import Enum

from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import ENUM as PgEnum, UUID

from ..database import Base

from ..auth.models import UsersORM
from ..courses.models import CoursesORM



class AccessLevelEnum(Enum):
    HIGH_MODERATOR = "HIGH_MODERATOR"
    MODERATOR = "MODERATOR"
    STUDENT = "STUDENT"


class UsersPermissionsORM(Base):
    __tablename__ = "users_permissions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey(UsersORM.id, ondelete='CASCADE'), primary_key=True
    )

    course_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey(CoursesORM.id, ondelete='CASCADE'), primary_key=True
    )

    access_level: Mapped[AccessLevelEnum] = mapped_column(
        PgEnum
        (
            AccessLevelEnum, 
            name="access_level_enum", 
            create_type=False,
            values_callable=lambda e: [field.value for field in e]
        ),
        nullable=False,
        default=AccessLevelEnum.STUDENT
    )

    #TODO: Как быть с владельцем курса, он должен иметь постоянное право владеть курсом
    expiration_date: Mapped[datetime | None]
    
