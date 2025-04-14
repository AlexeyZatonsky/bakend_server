from uuid import UUID

import logging
from fastapi import HTTPException, status

from ..core.log import configure_logging


from .repository import ChannelRepository
from .models import ChannelsORM
from .schemas import ChannelCreateSchema, ChannelReadSchema

from ..auth.schemas import UserReadSchema


logger = logging.getLogger(__name__)
configure_logging()


class ChannelService:
    def __init__(self, repository: ChannelRepository):
        self.repository = repository
        
    async def validate_owner(self, channel_id: str, user_data: UserReadSchema) -> ChannelReadSchema:
        channel = await self.repository.get_by_id(channel_id)

        if not channel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Channel not found"
            )

        channel_data = ChannelReadSchema.model_validate(channel)

        logger.warning(f"Channel owner: {channel_data.owner_id}, dtype = {type(channel_data.owner_id)}")
        logger.warning(f"Current user: {user_data.id}, dtype = {type(user_data.id)}")

        if channel_data.owner_id != user_data.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not the owner of this channel"
            )
        

        return channel_data

    async def create_channel(self, channel_data: ChannelCreateSchema, user_data: UserReadSchema) -> ChannelReadSchema | HTTPException:
        """
            Создает новый канал
            Args:
                channel_data: Данные для создания канала
                user: Пользователь, который создает канал
            Raises:
                HTTPException: 409 если канал с таким именем уже существует
            Returns:
                ChannelReadSchema: Созданный канал
        """
        
        if await self.repository.get_by_id(channel_data.id) is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Channel with this name already exists"
            )

        new_channel = ChannelsORM(**channel_data.model_dump(), owner_id=user_data.id)
        
        # Сохраняем канал в базу данных
        saved_channel = await self.repository.create(new_channel)
        
        return ChannelReadSchema.model_validate(saved_channel)
    

    async def get_channels(self, limit: int = 20) -> list[ChannelReadSchema]:
        """
        Получает все каналы
        Returns:
            list[ChannelReadSchema]: Список всех каналов
        """
        channels = await self.repository.get_all(limit)
        print("called")
        return [ChannelReadSchema.model_validate(channel) for channel in channels]

    async def get_channel_by_name(self, channel_id: str) -> ChannelReadSchema:
        """
        Получает канал по его имени
        Args:
            channel_id: Имя канала
        Returns:
            ChannelReadSchema: Канал
        """
        channel = await self.repository.get_by_id(channel_id)
        if not channel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Channel not found"
            )
        
        return ChannelReadSchema.model_validate(channel)

    async def get_user_channels(self, owner_id: UUID) -> list[ChannelReadSchema]:
        """
        Получает все каналы пользователя по его ID
        Args:
            owner_id: ID пользователя
        Returns:
            list[ChannelReadSchema]: Список всех каналов пользователя
        """
        channels = await self.repository.get_by_owner(owner_id)
        if not channels:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Channels not found"
            )
        
        return [ChannelReadSchema.model_validate(channel) for channel in channels]
    
    async def get_my_channels(self, user: UserReadSchema) -> list[ChannelReadSchema]:
        """
        Получает все каналы текущего пользователя
        Args:
            user: Текущий пользователь
        Returns:
            list[ChannelReadSchema]: Список всех каналов пользователя
        """
        channels = await self.repository.get_by_owner(user.id)
        if not channels:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="You don't have any channels"
            )
        
        return [ChannelReadSchema.model_validate(channel) for channel in channels]
    
    
    async def delete_channel(self, id: str, user_data: UserReadSchema) -> bool:
        """
        Удаляет канал по его имени
        Args:
            id: Имя канала
            user: Пользователь
        Returns:
            bool: True если канал удален, False если не удален
        """
        channel = await self.repository.get_by_id(id)
        if not channel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail = "Channel not found"
            )
        if channel.owner_id != user_data.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not the owner of this channel"
            )
            
        await self.repository.delete(channel)
        return True 