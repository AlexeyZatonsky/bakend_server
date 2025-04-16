from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_async_session

from ..auth.dependencies import get_current_user
from ..auth.schemas import UserReadSchema

from .service import ChannelService
from .schemas import ChannelReadSchema
from .repository import ChannelRepository




async def get_channel_service(session: AsyncSession = Depends(get_async_session)):
    repository = ChannelRepository(session)
    return ChannelService(repository)


async def get_current_channel(
    channel_id: str,
    user: UserReadSchema = Depends(get_current_user),
    service: ChannelService = Depends(get_channel_service),
) -> ChannelReadSchema:
    channel = await service.repository.get_by_id(channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")

    channel_data = ChannelReadSchema.model_validate(channel)

    if channel_data.owner_id != user.id:
        raise HTTPException(status_code=403, detail="You are not the owner of this channel")

    return channel_data