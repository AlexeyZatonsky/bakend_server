from sqlalchemy import Column, Integer, String, Numeric
from sqlalchemy.ext.declarative import declarative_base



Base = declarative_base()


class TableData(Base):
    __tablename__ = 'Test'

    id = Column(Integer, primary_key=True)
    description = Column(String)