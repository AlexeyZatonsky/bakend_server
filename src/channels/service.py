from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from fastapi import HTTPException

from .models import Channels
from .schemas import ChannelCreate, ChannelRead
from ..auth.models import Users

class ChannelService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def _unique_channel_name_check(self, channel_name: str) -> bool:
        """
        Проверяет, существует ли канал с таким именем
        Returns:
            bool: True если канал существует, False если не существует
        """
        query = select(Channels).where(Channels.unique_name == channel_name)
        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None

    async def create_channel(self, channel_data: ChannelCreate, user: Users) -> Channels:
        """
        Создает новый канал
        Args:
            channel_data: Данные для создания канала
            user: Пользователь, который создает канал
        Raises:
            HTTPException: 409 если канал с таким именем уже существует
        Returns:
            Channels: Созданный канал
        """
        if await self._unique_channel_name_check(channel_data.unique_name):
            raise HTTPException(
                status_code=409,
                detail="Channel with this name already exists"
            )

        channel = Channels(
            unique_name=channel_data.unique_name,
            owner_id=user.id,
            avatar=channel_data.avatar
        )
        self.session.add(channel)
        await self.session.commit()
        return channel
    
    async def get_channels(self) -> list[Channels]:
        query = select(Channels).limit(20)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_channel(self, channel_name: str) -> Channels:
        query = select(Channels).where(Channels.unique_name == channel_name)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_user_channels(self, owner_id: UUID) -> list[Channels]:
        query = select(Channels).where(Channels.owner_id == owner_id)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def delete_channel(self, unique_name: str, user: Users) -> bool:
        channel = await self.get_channel(unique_name)
        if not channel:
            return False
        if channel.owner_id != user.id:
            return False
            
        await self.session.delete(channel)
        await self.session.commit()
        return True 