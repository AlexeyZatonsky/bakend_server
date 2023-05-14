import os, aiofiles
from fastapi import Depends, File
from fastapi import UploadFile, BackgroundTasks, HTTPException

from sqlalchemy.ext.asyncio import  AsyncSession

from .models import Video, Tag, Category, video_tag
from ..channels.models import Channel
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
        self.video_folder='../../media'
    
    async def _get_channel_id(self):
        operation = (
            self.session
            .query(Channel)
            .filter_by(user_id=self.current_user.id)
            .first()
        )
        return operation

            
    async def write_video(title: str , file:UploadFile):
        async with aiofiles.open(title, "wb") as buffer:
            data = await file.read()
            await buffer.write(data)

    async def video_upload(self, 
    video_data: VidoeUpload,
    video_file: UploadFile) -> Video:
        channel_id = self._get_channel_id
        if not channel_id:
            raise HTTPException(status_code=425, detail="you dont have a channel")

        channel_folder = f'{self.video_folder}/{channel_id}'

        if not os.path.lexists(channel_folder):
            os.mkdir(channel_folder)
        
        if not os.path.exists(f'{channel_folder}/{video_data.title}'):
            file_path = f'{channel_folder}/{video_data.title}.mp4'
        else:       
            raise HTTPException(status_code=405, detail="a video with that name exists")
        
        if video_file.content_type == 'video/mp4':
            await self.write_video(file_path, video_file)
        else:
            raise HTTPException(status_code=418, detail="this file is not mp4")

        operation = Video(title = video_data.title,
                          description=video_data.description,
                          path = f'{channel_folder}/{channel_id}/{video_data.title}.mp4',
                          user_id = self.current_user.id,
                          category_id = video_data.category_id)

        self.session.add(operation)
        await self.session.commit()

        return {'message': 'upload done'}
    

    async def video_read_about(self, video_data: AboutVideo):
        pass

    async def video_remove(self): pass



    async def category_create(self, category_data: CategoryCreate) -> Category:
        operation = Category(name = category_data.name)
        self.session.add(operation)
        await self.session.commit()
        return operation 

    async def category_read(self, category_data: CategoryRead):
        pass

    async def category_remove(self): pass



    async def tag_create(self, tag_data: TagCreate) -> Tag:
        operation = Tag(name = tag_data.name)
        self.session.add(operation)
        await self.session.commit()
        return operation  

    async def tag_read(self, tag_data: TagRead):
        pass

    async def tag_remove(self): pass