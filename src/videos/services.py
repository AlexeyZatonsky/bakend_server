from fastapi import Depends
from sqlalchemy.ext.asyncio import  AsyncSession

from .models import Video, Tag, Category, video_tag
from .schemas import ReadCategory, CreateCategory, \
ReadTag, CreateTag, UploadVideo, AboutVideo, BaseVideoTag

from ..database import get_async_session

from ..auth.base_config import current_user




class OperationsVideo:
    def __init__(self,
                 session: AsyncSession=(Depends(get_async_session))):
        self.session = session
    
    
