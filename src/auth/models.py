from sqlalchemy import Column, MetaData, String, Boolean, UUID
from sqlalchemy.ext.declarative import declarative_base
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID
import uuid

# Импортируем Base из database.py
from ..database import Base

class Users(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    email = Column(String, nullable=False)
    username = Column(String(255), nullable=False)
    hashed_password = Column(String(length=1024), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)