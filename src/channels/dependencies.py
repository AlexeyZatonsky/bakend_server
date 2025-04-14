from fastapi import Depends
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
    service: ChannelService = Depends(get_channel_service)
) -> ChannelReadSchema:
    return await service.validate_owner(channel_id, user.id)
