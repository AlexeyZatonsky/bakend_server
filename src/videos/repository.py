import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .models import VideoORM, VideoMetadatasORM, VideoTagOrm



class VideoRepository:
    def __init__(self, session: AsyncSession):
        self.session = session


    async def get_video_metadatas_by_id(self, video_id: uuid.UUID) -> VideoMetadatasORM | None:
        query = select(VideoMetadatasORM).where(VideoMetadatasORM.video_id == video_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    
    async def get_by_id(self, video_id: uuid.UUID) -> VideoORM | None:
        query = select(VideoORM).where(VideoORM.id == video_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()  
    

    async def create_video(self, video: VideoORM) -> VideoORM:
        self.session.add(video)
        await self.session.commit()
        await self.session.refresh(video)
        return video    
    
    async def get_by_tag(self, tag: str) -> list[VideoORM]:
        query = select(VideoORM).where(VideoORM.tags.contains(tag))
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_all(self, limit: int = 20) -> list[VideoORM]:
        query = select(VideoORM).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()
    

    async def delete(self, video: VideoORM) -> None:
        await self.session.delete(video)
        await self.session.commit() 
