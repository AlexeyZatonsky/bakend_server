import os, aiofiles
from fastapi import Depends, File
from fastapi import UploadFile, BackgroundTasks, HTTPException

from sqlalchemy.ext.asyncio import  AsyncSession
from sqlalchemy import select

from .models import Video, Tag, Category, video_tag
from ..channels.models import Channel
from ..channels.schemas import  ChannelRead
from .schemas import CategoryRead, CategoryCreate, \
TagRead, TagCreate, VidoeUpload, AboutVideo, BaseVideoTag

from ..database import get_async_session

from ..auth.base_config import current_user
from ..auth.models import Users




class BaseVideoServices:
    def __init__(self,
                 session: AsyncSession=(Depends(get_async_session)),
                 current_user: Users=Depends(current_user)):
        self.session = session
        self.current_user = current_user

        self.video_folder='media'
    
    async def _get_channel(self) -> Channel:
        operation = await self.session.execute(
        select(Channel)
        .where(Channel.user_id == self.current_user.id)
        )
    
        result = operation.scalar_one_or_none()
        
        if not result:
            raise HTTPException(status_code=425, detail="You don't have a channel")
        
        return result

            
    @staticmethod
    async def write_video(file_path: str, video_file: UploadFile):
        async with aiofiles.open(file_path, "wb") as buffer:
            data = await video_file.read()
            await buffer.write(data)

    async def video_upload(self, 
    title: str,
    description: str,
    category_id: str,
    video_file: UploadFile):
        
        channel = await self._get_channel()

        channel_folder = f'{self.video_folder}/{channel.id}'
        if not os.path.lexists(channel_folder):
            os.makedirs(channel_folder)
        
        file_path = f'{channel_folder}/{title}.mp4'
        if os.path.exists(f'{channel_folder}/{title}'):
            raise HTTPException(status_code=405, detail="A video with that name already exists")

        if not video_file.content_type.startswith('video'):
            raise HTTPException(status_code=418, detail="This file is not a video")
           
        await self.write_video(file_path, video_file)

        operation = Video(title = title,
                          description=description,
                          path = file_path,
                          user_id = self.current_user.id,
                          category_id = int(category_id)
        )
        self.session.add(operation)
        await self.session.commit()

        return operation
    

    async def video_read_about(self, video_data: AboutVideo) -> AboutVideo:
        pass

    async def video_remove(self, title:str):

        search_video = await self.session.execute(
            select(Video)
            .where(Video.title == title)
        )
        video = search_video.scalar_one_or_none()
        
        if not video:
            raise HTTPException(status_code=408, detail='a video with that name does not exist')        

        await self.session.delete(video)
        await self.session.commit()

        file_path = video.path

        if os.path.exists(file_path):
            os.remove(file_path)

        return {'message': 'Video removed successfully'}



    async def category_create(self, category_data: CategoryCreate) -> CategoryRead:
        operation = Category(name = category_data.name)
        self.session.add(operation)
        await self.session.commit()
        return operation 

    async def category_read(self) -> list[Category]:
        operation = await self.session.execute(
            select(Category)
        )
        result = operation.scalars()
        
        return result

    async def category_remove(self): pass



    async def tag_create(self, tag_data: TagCreate) -> Tag:
        operation = Tag(name = tag_data.name)
        self.session.add(operation)
        await self.session.commit()
        return operation  

    async def tag_read(self, tag_data: TagRead):
        pass

    async def tag_remove(self): pass
