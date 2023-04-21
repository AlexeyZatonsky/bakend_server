from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..settings import options



engine = create_engine(
    options.database_url
)

Session = sessionmaker(
    engine,
    autocommit = False,
    autoflush=False
)