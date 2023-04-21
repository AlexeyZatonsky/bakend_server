from workshop.database.database import engine, Session
from workshop.database.tables import Base



'''def create_db():
    Base.metadata.create_all(bind=engine)'''

def get_session() -> Session:
    session = Session

    try: yield session
    finally: session.close()