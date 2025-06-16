from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_async_session

from ..auth.dependencies import get_current_user
from ..auth.schemas import UserReadSchema

from .service import ChannelService
from .schemas import ChannelReadSchema
from .repository import ChannelRepository
from .exceptions import ChannelsHTTPExceptions



async def get_channel_service(session: AsyncSession = Depends(get_async_session)):
    repository = ChannelRepository(session)
    http_exceptions = ChannelsHTTPExceptions()
    return ChannelService(repository, http_exceptions)

async def get_channel_exceptions() -> ChannelsHTTPExceptions:
    channels_http_exceptions = ChannelsHTTPExceptions()
    return channels_http_exceptions

async def get_current_channel(
    channel_id: str,
    user: UserReadSchema = Depends(get_current_user),
    service: ChannelService = Depends(get_channel_service),
) -> ChannelReadSchema:
    channel = await service.repository.get_by_id(channel_id)
    if not channel:
        raise service.http_exceptions.not_found_404()

    channel_data = ChannelReadSchema.model_validate(channel)

    if channel_data.owner_id != user.id:
        raise service.http_exceptions.forbidden_403()

    return channel_data