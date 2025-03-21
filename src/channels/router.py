from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from ..database import get_async_session
from ..auth.dependencies import get_current_user
from ..auth.schemas import UserReadSchema

from .schemas import ChannelCreateSchema, ChannelReadSchema

from .service import ChannelService

router = APIRouter(
    prefix="/channels",
    tags=["Channels"]
)

async def get_channel_service(session: AsyncSession = Depends(get_async_session)):
    from .repository import ChannelRepository
    repository = ChannelRepository(session)
    return ChannelService(repository)

@router.post("", response_model=ChannelReadSchema, status_code=status.HTTP_201_CREATED)
async def create_channel(
    channel_data: ChannelCreateSchema,
    current_user: UserReadSchema = Depends(get_current_user),
    channel_service: ChannelService = Depends(get_channel_service)
):
    """Создает новый канал"""
    return await channel_service.create_channel(channel_data, current_user)

@router.get("", response_model=list[ChannelReadSchema])
async def get_channels(channel_service: ChannelService = Depends(get_channel_service)):
    """
    Получает список всех каналов.
    Returns:
        list[ChannelRead]: Список всех каналов
    """
    return await channel_service.get_channels()

# Внимание: порядок маршрутов имеет значение!
# Более специфичные маршруты должны идти перед общими

@router.get("/my", response_model=list[ChannelReadSchema])
async def get_my_channels(
    current_user: UserReadSchema = Depends(get_current_user),
    channel_service: ChannelService = Depends(get_channel_service)
):
    """Получает все каналы текущего пользователя"""
    return await channel_service.get_my_channels(current_user)

@router.get("/user/{owner_id}", response_model=list[ChannelReadSchema])
async def get_user_channels(
    owner_id: UUID,
    channel_service: ChannelService = Depends(get_channel_service)
):
    """Получает все каналы указанного пользователя"""
    return await channel_service.get_user_channels(owner_id)

# Общий маршрут для получения канала по имени должен идти после специфичных маршрутов
@router.get("/{unique_name}", response_model=ChannelReadSchema)
async def get_channel(
    unique_name: str,
    channel_service: ChannelService = Depends(get_channel_service)
):
    """Получает канал по его уникальному имени"""
    return await channel_service.get_channel_by_name(unique_name)

@router.delete("/{unique_name}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_channel(
    unique_name: str,
    current_user: UserReadSchema = Depends(get_current_user),
    channel_service: ChannelService = Depends(get_channel_service)
):
    """
    Удаляет канал по его уникальному имени.
    Args:
        unique_name: Уникальное имя канала
        current_user: Текущий пользователь (должен быть владельцем канала)
    Returns:
        204 No Content при успешном удалении
    Raises:
        404: Канал не найден или пользователь не является владельцем
    """
    deleted = await channel_service.delete_channel(unique_name, current_user)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Channel not found or access denied"
        )
