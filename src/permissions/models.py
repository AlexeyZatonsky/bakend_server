from sqlalchemy import Column, ForeignKey, UUID
from sqlalchemy.dialects.postgresql import ENUM as PgEnum
import uuid

from enum import Enum

from ..auth.models import Users
from ..database import Base


class AccessLevelEnum(Enum):
    HIGH_MODERATOR = "HIGH_MODERATOR"
    MODERATOR = "MODERATOR"
    STUDENT = "STUDENT"


class UsersPermission(Base):
    __tablename__ = "users_permissions"

    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    course_id = Column(UUID(as_uuid=True), ForeignKey('courses.id', ondelete='CASCADE'), primary_key=True)
    access_level = Column(
        PgEnum
        (
            AccessLevelEnum, 
            name="access_level_enum", 
            create_type=False,
            values_callable=lambda e: [field.value for field in e]
        ),
        nullable=False,
        default=AccessLevelEnum.MODERATOR)

