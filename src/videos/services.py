from fastapi import Depends
from sqlalchemy.ext.asyncio import  AsyncSession

from .models import Video, Tag, Category, video_tag
from .schemas import CategoryRead, CategoryCreate, \
TagRead, TagCreate, VidoeUpload, AboutVideo, BaseVideoTag

from ..database import get_async_session

from ..auth.base_config import current_user
from ..auth.models import User




class OperationsVideo:
    def __init__(self,
                 session: AsyncSession=(Depends(get_async_session)),
                 current_user: User=Depends(current_user)):
        self.session = session
        self.current_user = current_user
    
    async def video_upload(self, video_data: VidoeUpload) -> Video:
        pass

    async def video_read_about(self, video_data: AboutVideo):
        pass

    async def video_remove(self): pass



    async def category_create(self, category_data: CategoryCreate) -> Category:
        pass

    async def category_read(self, category_data: CategoryRead):
        pass

    async def category_remove(self): pass



    async def tag_create(self, tag_data: TagCreate) -> Tag:
        pass  

    async def tag_read(self, tag_data: TagRead):
        pass

    async def tag_remove(self): pass