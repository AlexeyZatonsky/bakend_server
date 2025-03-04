import pytest 
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from src.channels.models import Channels
from src.channels.schemas import ChannelCreate, ChannelRead
from src.auth.models import Users
from src.auth.schemas import UserCreate, UserLogin, UserRead
from conftest import UserTestData




@pytest.fixture
def channel_test_data(test_user_data: UserTestData) -> ChannelCreate:
    """Фикстура с тестовыми данными для канала"""
    return ChannelCreate(
        unique_name=test_user_data.test_channel_name,
        avatar=test_user_data.test_channel_avatar
    )


@pytest_asyncio.fixture
async def authenticated_user(
    ac: AsyncClient,
    user_data_model: UserCreate,
    user_login_data: UserLogin
) -> Users:
    """
    Фикстура создает пользователя, логинит его и возвращает объект пользователя.
    Область видимости - только для текущего теста.
    """
    # Регистрация пользователя
    register_response = await ac.post("/auth/register", json=user_data_model.model_dump())
    assert register_response.status_code == 201
    user_data = UserRead.model_validate(register_response.json())
    
    # Логин пользователя
    login_form_data = {
        "username": user_login_data.email,
        "password": user_login_data.password
    }
    login_response = await ac.post("/auth/login", data=login_form_data)
    assert login_response.status_code == 200
    assert "access_token" in login_response.cookies
    
    return user_data


@pytest.mark.asyncio(loop_scope="session")
async def test_create_channel(
    authenticated_user: Users,
    channel_test_data: ChannelCreate,
    ac: AsyncClient,
    session: AsyncSession
):
    """
    Тестирует создание нового канала.
    Проверяет:
    - Успешное создание канала
    - Корректность данных в БД
    - Привязку к пользователю
    """
    response = await ac.post(
        "/channels",
        json=channel_test_data.model_dump()
    )
    
    assert response.status_code == 201
    channel_data = ChannelRead.model_validate(response.json())
    assert channel_data.unique_name == channel_test_data.unique_name
    assert channel_data.owner_id == authenticated_user.id
    
    # Проверяем запись в БД
    db_channel = await session.execute(
        select(Channels)
        .where(Channels.unique_name == channel_test_data.unique_name)
    )
    db_channel = db_channel.scalar_one()
    assert db_channel.owner_id == authenticated_user.id


@pytest.mark.asyncio(loop_scope="session")
async def test_create_duplicate_channel(
    authenticated_user: Users,
    channel_test_data: ChannelCreate,
    ac: AsyncClient
):
    """
    Тестирует попытку создания канала с уже существующим именем.
    Проверяет:
    - Успешное создание первого канала
    - Ошибку 409 при попытке создать канал с тем же именем
    - Корректное сообщение об ошибке
    """
    # Создаем первый канал
    response = await ac.post(
        "/channels",
        json=channel_test_data.model_dump()
    )
    assert response.status_code == 201
    
    # Пытаемся создать канал с тем же именем
    response = await ac.post(
        "/channels",
        json=channel_test_data.model_dump()
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "Channel with this name already exists"


@pytest_asyncio.fixture(autouse=True)
async def clean_channels(session: AsyncSession):
    """
    Автоматически очищает таблицу каналов до и после каждого теста.
    Использует каскадное удаление для связанных записей.
    """
    await session.execute(delete(Channels))
    await session.commit()
    yield
    await session.execute(delete(Channels))
    await session.commit()



