from uuid import UUID
from typing import Optional, List, Dict, Any
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

from ..core.AbstractRepository import AbstractRepository
from ..core.Enums.ExtensionsEnums import VideoExtensionsEnum, ImageExtensionsEnum

from .models import VideoORM, VideoMetadatasORM, VideoTagOrm, TagORM, CategoryORM
from .schemas import VideoDataUpdateSchema



class VideoDataRepository(AbstractRepository[VideoORM]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, VideoORM)

    async def get_by_id(self, entity_id: UUID) -> Optional[VideoORM]:
        return await super().get_by_id(entity_id)
    
    async def get_all(self, limit: int = 20, offset: int = 0) -> List[VideoORM]:
        query = select(self.model).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def create(self, entity: VideoORM) -> VideoORM:
        return await super().create(entity)
    
    async def delete(self, entity: VideoORM) -> None:
        await super().delete(entity)
        
    async def get_by_channel_id(self, channel_id: UUID, limit: int = 20) -> List[VideoORM]:
        query = select(self.model).where(self.model.channel_id == channel_id).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def update(self, entity: VideoORM) -> VideoORM:
        await self.session.merge(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity
    
    async def upsert_video_file(self, video_id: UUID, url: str, mime: str) -> None:
        video = await self.get_by_id(video_id)
        if video:
            video.url = url
            video.mime = mime
            await self.update(video)
        else:
            await self.create(VideoORM(id=video_id, url=url, mime=mime))

    async def upsert_preview_file(self, video_id: UUID, url: str, mime: str) -> None:
        preview = await self.get_by_id(video_id)
        if preview:
            preview.url = url
            preview.mime = mime
            await self.update(preview)
        else:
            await self.create(VideoORM(id=video_id, url=url, mime=mime))
            
    async def ensure_draft(
        self,
        *,
        video_id: UUID,
        user_id: UUID,
        channel_id: str,
        video_ext: VideoExtensionsEnum = VideoExtensionsEnum.MP4,
    ) -> VideoORM:
        """
        Создаёт «черновик» видео, если его ещё нет,
        с is_public=False и минимальным набором полей.
        """
        existing = await self.get_by_id(video_id)
        if existing:
            return existing

        now = datetime.utcnow()
        draft = VideoORM(
            id=video_id,
            user_id=user_id,
            channel_id=channel_id,
            video_ext=video_ext,
            preview_ext=None,
            name="",
            description="",
            is_free=False,
            is_public=False,
            timeline=0,
            upload_date=now,
        )
        return await self.create(draft)

    async def set_preview_extension(self, video_id: UUID, extension: ImageExtensionsEnum) -> None:
        """
        Обновляет в БД расширение превью для уже существующего видео.
        """
        await self.session.execute(
            update(VideoORM)
            .where(VideoORM.id == video_id)
            .values(preview_ext = extension)
        )
        await self.session.commit()
        
        
    async def update_video_name(self, video_id: UUID, name: str) -> None:
        video = await self.get_by_id(video_id)
        if not video:
            raise ValueError(f"Видео {video_id!r} не найдено")
        video.name = name
        await self.update(video)
        
    async def update_video_description(self, video_id: UUID, description: str) -> None:
        video = await self.get_by_id(video_id)
        if not video:
            raise ValueError(f"Видео {video_id!r} не найдено")
        video.description = description
        await self.update(video)
        
    async def update_video_is_free(self, video_id: UUID, is_free: bool) -> None:
        video = await self.get_by_id(video_id)
        if not video:
            raise ValueError(f"Видео {video_id!r} не найдено")
        video.is_free = is_free
        await self.update(video)
        
    async def update_video_is_public(self, video_id: UUID, is_public: bool) -> None:
        video = await self.get_by_id(video_id)
        if not video:
            raise ValueError(f"Видео {video_id!r} не найдено")
        video.is_public = is_public
        await self.update(video)

    async def get_videos_by_user_id(self, user_id: UUID) -> List[VideoORM]:
        query = select(self.model).where(self.model.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalars().all()


class VideoMetadataRepository(AbstractRepository[VideoMetadatasORM]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, VideoMetadatasORM)

    async def get_by_id(self, entity_id: UUID) -> Optional[VideoMetadatasORM]:
        return await super().get_by_id(entity_id)
    
    async def get_all(self, limit: int = 20, offset: int = 0) -> List[VideoMetadatasORM]:
        query = (
            select(self.model)
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def create(self, entity: VideoMetadatasORM) -> VideoMetadatasORM:
        return await super().create(entity)
    
    async def delete(self, entity: VideoMetadatasORM) -> None:
        await super().delete(entity)
    
    async def increment_views(self, video_id: UUID) -> int:
        """Увеличение счетчика просмотров"""
        metadata = await self.get_by_id(video_id)
        if metadata:
            metadata.views += 1
            await self.session.commit()
            await self.session.refresh(metadata)
            return metadata.views
        return 0
    
    async def add_like(self, video_id: UUID) -> dict:
        """Добавление лайка"""
        metadata = await self.get_by_id(video_id)
        if metadata:
            metadata.likes += 1
            await self.session.commit()
            await self.session.refresh(metadata)
            return {"likes": metadata.likes, "dislikes": metadata.dislikes}
        return {"likes": 0, "dislikes": 0}
    
    async def add_dislike(self, video_id: UUID) -> dict:
        """Добавление дизлайка"""
        metadata = await self.get_by_id(video_id)
        if metadata:
            metadata.dislikes += 1
            await self.session.commit()
            await self.session.refresh(metadata)
            return {"likes": metadata.likes, "dislikes": metadata.dislikes}
        return {"likes": 0, "dislikes": 0}


class TagRepository(AbstractRepository[TagORM]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, TagORM)

    async def get_by_id(self, entity_id: int) -> Optional[TagORM]:
        return await super().get_by_id(entity_id)
    
    async def get_all(self, limit: int = 100, offset: int = 0) -> List[TagORM]:
        query = (
            select(self.model)
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def get_by_name(self, name: str) -> Optional[TagORM]:
        query = select(self.model).where(self.model.name == name)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()


class VideoTagRepository(AbstractRepository[VideoTagOrm]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, VideoTagOrm)
    
    async def get_by_video_id(self, video_id: UUID) -> List[VideoTagOrm]:
        query = select(self.model).where(self.model.video_id == video_id)
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def update_video_tags(self, video_id: UUID, tag_ids: List[int]) -> None:
        """Обновление тегов видео"""
        # Удаляем существующие связи
        await self.session.execute(
            delete(VideoTagOrm)
            .where(VideoTagOrm.video_id == video_id)
        )
        
        # Добавляем новые связи
        for tag_id in tag_ids:
            video_tag = VideoTagOrm(
                video_id=video_id,
                tag_id=tag_id
            )
            self.session.add(video_tag)
        
        await self.session.commit()


class CategoryRepository(AbstractRepository[CategoryORM]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, CategoryORM)
    
    async def get_by_id(self, entity_id: int) -> Optional[CategoryORM]:
        return await super().get_by_id(entity_id)
    
    async def get_all(self, limit: int = 100, offset: int = 0) -> List[CategoryORM]:
        query = (
            select(self.model)
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()


def get_video_data_repository(session: AsyncSession) -> VideoDataRepository:
    return VideoDataRepository(session)

def get_video_metadata_repository(session: AsyncSession) -> VideoMetadataRepository:
    return VideoMetadataRepository(session) 

def get_tag_repository(session: AsyncSession) -> TagRepository:
    return TagRepository(session)

def get_video_tag_repository(session: AsyncSession) -> VideoTagRepository:
    return VideoTagRepository(session)  

def get_category_repository(session: AsyncSession) -> CategoryRepository:
    return CategoryRepository(session)  







class VideoRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.video_data_repo = VideoDataRepository(session)
        self.video_metadata_repo = VideoMetadataRepository(session)
        self.tag_repo = TagRepository(session)
        self.video_tag_repo = VideoTagRepository(session)
        self.category_repo = CategoryRepository(session)

    async def get_video_data_by_id(self, video_id: UUID) -> Optional[VideoORM]:
        return await self.video_data_repo.get_by_id(video_id)
    
    async def get_video_metadata_by_id(self, video_id: UUID) -> Optional[VideoMetadatasORM]:
        return await self.video_metadata_repo.get_by_id(video_id)
    
    async def get_all_video_datas(self, limit: int = 20, offset: int = 0) -> List[VideoORM]:
        return await self.video_data_repo.get_all(limit, offset)

    async def update_video_details(self, entity: VideoORM) -> VideoORM:
        return await self.video_data_repo.update(entity)

    async def increment_views(self, video_id: UUID) -> int:
        return await self.video_metadata_repo.increment_views(video_id)

    async def add_like(self, video_id: UUID) -> dict:
        return await self.video_metadata_repo.add_like(video_id)

    async def add_dislike(self, video_id: UUID) -> dict:
        return await self.video_metadata_repo.add_dislike(video_id)
    
    async def upsert_video_file(self, video_id: UUID, url: str, mime: str) -> None:
        return await self.video_data_repo.upsert_video_file(video_id, url, mime)

    async def upsert_preview_file(self, video_id: UUID, url: str, mime: str) -> None:
        return await self.video_data_repo.upsert_preview_file(video_id, url, mime)


    async def ensure_draft(
        self,
        *,
        video_id: UUID,
        user_id: UUID,
        channel_id: str,
        video_ext: VideoExtensionsEnum = VideoExtensionsEnum.MP4,
    ) -> VideoORM:
        return await self.video_data_repo.ensure_draft(
            video_id=video_id,
            user_id=user_id,
            channel_id=channel_id,
            video_ext=video_ext,
        )
        
    async def set_preview_extension(self, video_id: UUID, extension: str) -> None:
        return await self.video_data_repo.set_preview_extension(video_id, extension)
    
    
    async def update_video_name(self, video_id: UUID, name: str) -> None:
        return await self.video_data_repo.update_video_name(video_id, name)
    
    async def update_video_description(self, video_id: UUID, description: str) -> None:
        return await self.video_data_repo.update_video_description(video_id, description)
    
    async def update_video_is_free(self, video_id: UUID, is_free: bool) -> None:
        return await self.video_data_repo.update_video_is_free(video_id, is_free)
    
    async def update_video_is_public(self, video_id: UUID, is_public: bool) -> None:
        return await self.video_data_repo.update_video_is_public(video_id, is_public)
    
    async def get_videos_by_user_id(self, user_id: UUID) -> List[VideoORM]:
        return await self.video_data_repo.get_videos_by_user_id(user_id)
