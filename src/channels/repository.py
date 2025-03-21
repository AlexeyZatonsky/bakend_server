from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .models import ChannelsORM



class ChannelRepository:
    def __init__(self, session: AsyncSession):
        self.session = session


    async def get_by_name(self, channel_name: str) -> ChannelsORM | None:
        query = select(ChannelsORM).where(ChannelsORM.unique_name == channel_name)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    

    async def create_channel(self, channel: ChannelsORM) -> ChannelsORM:
        self.session.add(channel)
        await self.session.commit()
        await self.session.refresh(channel)
        return channel


    async def get_by_owner(self, owner_id: UUID) -> list[ChannelsORM]:
        query = select(ChannelsORM).where(ChannelsORM.owner_id == owner_id)
        result = await self.session.execute(query)
        return result.scalars().all()
    

    async def get_all(self, limit: int = 20) -> list[ChannelsORM]:
        query = select(ChannelsORM).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()


    async def delete(self, channel: ChannelsORM) -> None:
        await self.session.delete(channel)
        await self.session.commit()
