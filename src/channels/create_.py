from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession


from ..database import get_async_session
from .models import Channel
from .schemas import ChannelCreat, BaseChannel
from ..auth.models import User



router = APIRouter(
    prefix="/Channel",
    tags=['channel']
)


@router.post('/create', response_model=BaseChannel)
async def create_channel(
    schema: BaseChannel,
    session: AsyncSession = Depends(get_async_session)):

    return session

    