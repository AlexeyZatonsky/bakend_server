import uuid

from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ENUM as PgEnum
from sqlalchemy.orm import Mapped, mapped_column

from ..core.Enums.ExtensionsEnums import ImageExtensionsEnum
from ..database import Base

from ..auth.models import UsersORM



class ChannelsORM(Base):
    __tablename__ = 'channels'

    id : Mapped[str] = mapped_column(String(255), unique=True, primary_key=True)
    
    owner_id : Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey(UsersORM.id, ondelete='CASCADE'), nullable=False
    )
    
    avatar_ext: Mapped[ImageExtensionsEnum] = mapped_column(
        PgEnum(
            ImageExtensionsEnum,
            name="image_extensions_enum",
            value_callable = lambda e: e.value,
            nullable = True
        ),
        nullable=True,
        default=None
    )

    preview_ext: Mapped[ImageExtensionsEnum] = mapped_column(
        PgEnum(
            ImageExtensionsEnum,
            name="image_extensions_enum",
            value_callable = lambda e: e.value,
            nullable = True
        ),
        nullable=True,
        default=None
    )
    
    subscribers_count : Mapped[int] = mapped_column(Integer, default=0, nullable=False)
