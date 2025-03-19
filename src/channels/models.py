import uuid

from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base

from ..auth.models import UsersORM



class ChannelsORM(Base):
    __tablename__ = 'channels'

    unique_name : Mapped[str] = mapped_column(String(255), unique=True, primary_key=True)
    
    owner_id : Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey(UsersORM.id, ondelete='CASCADE'), nullable=False
    )
    
    avatar : Mapped[str | None] = mapped_column(String(1000), nullable=True)
    subscribers_count : Mapped[str] = mapped_column(Integer, default=0, nullable=False)
