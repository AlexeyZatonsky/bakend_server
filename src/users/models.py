from datetime import datetime
from sqlalchemy import Column, Integer, MetaData, String, TIMESTAMP, Boolean
from sqlalchemy.ext.declarative import declarative_base
import uuid


users_metadata = MetaData()

Base = declarative_base(metadata=users_metadata)


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False)
    username = Column(String(255), nullable=False)
    registrated_at = Column(TIMESTAMP, default=datetime.utcnow)
    is_verified = Column(Boolean, default=False, nullable=False)
    hashed_password = Column(String, nullable=False)