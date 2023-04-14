from fastapi import  APIRouter
from fastapi import Depends
from fastapi import Response

from ..models import Operation




router = APIRouter(
    prefix='/operations',
)

