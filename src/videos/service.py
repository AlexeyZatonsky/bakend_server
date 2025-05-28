from uuid import UUID, uuid4
from typing import List, Dict

from .repository import VideoRepository
from .exceptions import VideoHTTPExceptions
from .models     import VideoORM
from .schemas    import VideoDataReadSchema, VideoDataUpdateSchema

from ..core.Enums.ExtensionsEnums import VideoExtensionsEnum, ImageExtensionsEnum
from ..core.Enums.MIMETypeEnums import ImageMimeEnum
from ..core.Enums.TypeReferencesEnums import ImageTypeReference


import logging
from ..core.log import configure_logging
logger = logging.getLogger(__name__)
configure_logging()


class VideoService:
    def __init__(self, repository: VideoRepository, http_exc: VideoHTTPExceptions):
        self.repository   = repository
        self.http_exceptions    = http_exc

    # ─── Запросы данных ──────────────────────────────────────────────────────
    async def get_video_data_by_id(self, video_id: UUID) -> VideoDataReadSchema:
        data = await self.repository.video_data_repo.get_by_id(video_id)
        if not data or (not data.is_public):
            raise self.http_exceptions.not_found_404()
        return VideoDataReadSchema.model_validate(data)

    # ─── WEBHOOK: файл видео загружен ────────────────────────────────────────
    async def process_video_upload(
        self,
        user_id: UUID,
        channel_id: str,
        video_id: UUID,
        ext: VideoExtensionsEnum,
        mime: str,
    ) -> None:
        """
        Вызывается из webhook-а после фактической загрузки файла.
        Обновляет URL и mime прямо в БД.
        """
        from ..settings.config import S3_ENV
        url = f"{S3_ENV.public_url}/{user_id}/channels/{channel_id}/{video_id}/video.{ext}"
        await self.repository.upsert_video_file(video_id, url, mime)

    # ─── WEBHOOK: превью загружено ───────────────────────────────────────────
    async def process_preview_upload(
        self,
        user_id: UUID,
        channel_id: str,
        video_id: UUID,
        ext: ImageExtensionsEnum,
        mime: str,
    ) -> None:
        from ..settings.config import S3_ENV
        url = f"{S3_ENV.public_url}/{user_id}/channels/{channel_id}/{video_id}/preview.{ext}"
        await self.repository.upsert_preview_file(video_id, url, mime)

    # ─── Публикация видео после формы ────────────────────────────────────────
    async def publish_video(
        self,
        video_id: UUID,
        data: VideoDataUpdateSchema,
    ) -> VideoDataReadSchema:
        video = await self.repository.video_data_repo.get_by_id(video_id)
        if not video:
            raise self.http_exceptions.not_found_404()

        # здесь могут быть любые проверки прав доступа

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(video, field, value)
        video.is_public = True
        updated = await self.repository.video_data_repo.update(video)
        return VideoDataReadSchema.model_validate(updated)

    # лайки / просмотры (оставлены без изменений) …

    async def create_initial_video(
        self,
        user_id: UUID,
        channel_id: str,
    ) -> VideoORM:
        """
        Генерирует новый video_id, создаёт в БД черновик
        (is_public=False) и возвращает ORM-объект.
        """
        video_id = uuid4()
        return await self.repository.ensure_draft(
            video_id=video_id,
            user_id=user_id,
            channel_id=channel_id,
        )
        
    async def update_video(
        self,
        video_id: UUID,
        data: VideoDataUpdateSchema,
    ) -> VideoDataReadSchema:
        if (data.name != None) : await self.repository.update_video_name(video_id, data.name)
        if (data.description != None) : await self.repository.update_video_description(video_id, data.description)
        if (data.is_free != None) : await self.repository.update_video_is_free(video_id, data.is_free)
        if (data.is_public != None) : await self.repository.update_video_is_public(video_id, data.is_public)
        
        video = await self.repository.get_video_data_by_id(video_id)
        return VideoDataReadSchema.model_validate(video)
    
    
    async def get_videos_by_user_id(self, user_id: UUID) -> List[VideoDataReadSchema]:
        videos = await self.repository.get_videos_by_user_id(user_id)
        logger.debug(f"videos: {videos}")
        return [VideoDataReadSchema.model_validate(video) for video in videos]

    async def get_all_video_datas(self) -> List[VideoDataReadSchema]:
        videos = await self.repository.get_all_video_datas()
        return [VideoDataReadSchema.model_validate(video) for video in videos]

    
    async def set_preview_extension(
           self,
            video_id: UUID,
            mime: ImageMimeEnum,    
    ) -> None:
        image_type_ref = ImageTypeReference.from_mime(mime)
        image_type: ImageExtensionsEnum = image_type_ref.ext
        return await self.repository.set_preview_extension(video_id, image_type)