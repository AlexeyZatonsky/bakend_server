from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession


from ..auth.models import Users
from .models import Channel
from .schemas import ChannelCreate
from ..database import get_async_session
from ..auth.base_config import current_user




router = APIRouter(
    prefix="/Channel",
    tags=['channel']
)



@router.post('/create/', response_model= ChannelCreate, status_code=201)
async def create_channel(
    schema: ChannelCreate,
    session: AsyncSession = Depends(get_async_session),
    current_user: Users = Depends(current_user)
):

    operation = Channel(title=schema.title, user_id=current_user.id)
    session.add(operation)
    await session.commit()
    return {"id": str(operation.id), "title": operation.title, "user_id": str(operation.user_id)}