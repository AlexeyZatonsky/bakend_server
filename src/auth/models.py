from sqlalchemy import Column, String, Boolean, UUID, ForeignKey
from sqlalchemy.orm import relationship
import uuid

from ..database import Base

class Users(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    username = Column(String(255), nullable=False, unique=True)
    avatar = Column(String(1000), nullable=True)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

class SecretInfo(Base):
    __tablename__ = 'secret_info'

    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String(1024), nullable=False)
    phone_number = Column(String, unique=True, nullable=True)
    INN = Column(String, unique=True, nullable=True)
    organization_name = Column(String, nullable=True)

