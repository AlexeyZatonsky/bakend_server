import pytest 
from httpx import AsyncClient
from src.database import Base, engine
from src.app import app


