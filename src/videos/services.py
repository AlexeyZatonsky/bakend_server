from fastapi import Depends
from sqlalchemy.ext.asyncio import  AsyncSession

from .models import Video, Tag, Category, video_tag