from datetime import datetime, UTC
from sqlalchemy import String, Boolean, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
import uuid

from ..database import Base


class UsersORM(Base):
    """Модель пользователя"""
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        default=uuid.uuid4, 
        primary_key=True
    )
    username: Mapped[str] = mapped_column(
        String(255), 
        nullable=False,
        unique=True
    )
    avatar: Mapped[str | None] = mapped_column(
        String(1000), 
        nullable=True
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean, 
        default=False
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, 
        default=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False
    )


class SecretInfoORM(Base):
    """Модель секретной информации пользователя"""
    __tablename__ = 'secret_info'
    
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey(UsersORM.id, ondelete='CASCADE'), 
        primary_key=True
    )
    email: Mapped[str] = mapped_column(
        String(320), 
        unique=True, 
        nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(
        String(256), 
        nullable=False
    )
    phone_number: Mapped[str | None] = mapped_column(
        String(15), 
        unique=True, 
        nullable=True
    )
    INN: Mapped[str | None] = mapped_column(
        String(12), 
        unique=True, 
        nullable=True
    )
    organization_name: Mapped[str | None] = mapped_column(
        String(255), 
        nullable=True
    )