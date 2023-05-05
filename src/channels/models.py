from sqlalchemy import Column, ForeignKey, Integer, MetaData, String, UUID
from sqlalchemy.ext.declarative import declarative_base
import uuid

from ..auth.models import User
from ..auth.models import users_metadata


channels_metadata = MetaData()

Base = declarative_base(metadata=users_metadata)


class Channel(Base):
    __tablename__ = 'channel'

    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    title = Column(String(255), nullable=False)
    user_id = Column(UUID(as_uuid=True) , ForeignKey(User.id))
 