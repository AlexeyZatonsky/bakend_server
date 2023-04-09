from pydantic import BaseSettings




class Settings(BaseSettings):
    server_host: str = '127.0.0.1'
    server_port: int = 8000
    database_url = 'sqlite:///./database.db'



'''
Valid SQLite URL forms are:
sqlite:///:memory: (or, sqlite://)
sqlite:///relative/path/to/file.db
sqlite:////absolute/path/to/file.db
'''