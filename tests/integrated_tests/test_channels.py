import pytest 
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from src.channels.models import ChannelsORM
from src.channels.schemas import ChannelCreateSchema, ChannelReadSchema
from src.auth.models import UsersORM
from src.auth.schemas import UserCreateSchema, UserLoginSchema, UserReadSchema
from conftest import UserTestData




@pytest.fixture
def channel_test_data(test_user_data: UserTestData) -> ChannelCreateSchema:
    """Фикстура с тестовыми данными для канала"""
    return ChannelCreateSchema(
        id=test_user_data.test_channel_id,
        avatar=test_user_data.test_channel_avatar
    )


@pytest_asyncio.fixture(scope="function")
async def authenticated_user(
    ac: AsyncClient,
    user_data_model: UserCreateSchema,
    user_login_data: UserLoginSchema
) -> UsersORM:
    """
    Фикстура создает пользователя, логинит его и возвращает объект пользователя.
    Область видимости - только для текущего теста.
    """
    # Регистрация пользователя
    register_response = await ac.post("/auth/register", json=user_data_model.model_dump())
    assert register_response.status_code == 201
    user_data = UserReadSchema.model_validate(register_response.json())
    
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
    authenticated_user: UsersORM,
    channel_test_data: ChannelCreateSchema,
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
    channel_data = ChannelReadSchema.model_validate(response.json())
    assert channel_data.id == channel_test_data.id
    assert channel_data.owner_id == authenticated_user.id
    
    # Проверяем запись в БД
    db_channel = await session.execute(
        select(ChannelsORM)
        .where(ChannelsORM.id == channel_test_data.id)
    )
    db_channel = db_channel.scalar_one()
    assert db_channel.owner_id == authenticated_user.id


@pytest.mark.asyncio(loop_scope="session")
async def test_create_duplicate_channel(
    authenticated_user: UsersORM,
    channel_test_data: ChannelCreateSchema,
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



@pytest.mark.asyncio(loop_scope="session")
async def test_unauthorized_access(
    channel_test_data: ChannelCreateSchema,
    ac: AsyncClient
):
    """
    Тестирует попытку создания канала без авторизации.
    Проверяет:
    - Ошибку 401 при попытке создать канал без авторизации
    """
    response = await ac.post(
        "/channels",
        json=channel_test_data.model_dump()
    )


@pytest.mark.asyncio(loop_scope="session")
async def test_get_all_channels(
    authenticated_user: UsersORM,
    channel_test_data: ChannelCreateSchema,
    ac: AsyncClient,
    session: AsyncSession
):
    """
    Тестирует получение всех каналов.
    Проверяет:
    - Успешное создание нескольких каналов
    - Успешное получение списка всех каналов
    - Корректное количество каналов в ответе
    - Корректность данных каждого канала
    """
    # Создаем несколько тестовых каналов
    test_channels = []
    for i in range(3):
        channel_data = ChannelCreateSchema(
            id=f"{channel_test_data.id}_{i}",
            avatar=channel_test_data.avatar
        )
        response = await ac.post("/channels", json=channel_data.model_dump())
        assert response.status_code == 201
        test_channels.append(ChannelReadSchema.model_validate(response.json()))
    
    # Получаем список всех каналов
    response = await ac.get("/channels")
    assert response.status_code == 200
    
    channels = [ChannelReadSchema.model_validate(channel) for channel in response.json()]
    
    # Проверяем количество каналов
    assert len(channels) == len(test_channels)
    
    # Проверяем данные каждого канала
    for test_channel in test_channels:
        matching_channel = next(
            (ch for ch in channels if ch.id == test_channel.id),
            None
        )
        assert matching_channel is not None
        assert matching_channel.owner_id == authenticated_user.id
        assert matching_channel.avatar == test_channel.avatar
        
    # Проверяем записи в БД
    db_channels = await session.execute(
        select(ChannelsORM)
        .where(ChannelsORM.owner_id == authenticated_user.id)
    )
    db_channels = db_channels.scalars().all()
    assert len(db_channels) == len(test_channels)
    
    # Проверяем соответствие данных в БД
    for test_channel in test_channels:
        matching_db_channel = next(
            (ch for ch in db_channels if ch.id == test_channel.id),
            None
        )
        assert matching_db_channel is not None
        assert matching_db_channel.owner_id == authenticated_user.id
        assert matching_db_channel.avatar == test_channel.avatar


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_channel(
    authenticated_user: UsersORM,
    channel_test_data: ChannelCreateSchema,
    ac: AsyncClient,
    session: AsyncSession
):
    """
    Тестирует удаление канала.
    Проверяет:
    - Успешное создание канала
    - Успешное удаление канала (204 No Content)
    - Отсутствие канала в БД после удаления
    """
    # Создаем канал
    create_response = await ac.post(
        "/channels",
        json=channel_test_data.model_dump()
    )
    assert create_response.status_code == 201
    
    # Удаляем канал
    delete_response = await ac.delete(f"/channels/{channel_test_data.id}")
    assert delete_response.status_code == 204
    assert delete_response.content == b""  # Проверяем, что тело ответа пустое
    
    # Проверяем, что канал удален из БД
    db_query = await session.execute(
        select(ChannelsORM)
        .where(ChannelsORM.id == channel_test_data.id)
    )
    assert db_query.scalar_one_or_none() is None


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_nonexistent_channel(
    authenticated_user: UsersORM,
    ac: AsyncClient
):
    """
    Тестирует попытку удаления несуществующего канала.
    Проверяет:
    - Ошибку 404 при попытке удалить несуществующий канал
    - Корректное сообщение об ошибке
    """
    response = await ac.delete("/channels/nonexistent_channel")
    assert response.status_code == 404
    assert response.json()["detail"] == "Channel not found or access denied"


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_channel_unauthorized(
    authenticated_user: UsersORM,
    channel_test_data: ChannelCreateSchema,
    ac: AsyncClient,
    session: AsyncSession
):
    """
    Тестирует попытку удаления канала неавторизованным пользователем.
    Проверяет:
    - Успешное создание канала
    - Ошибку 401 при попытке удалить канал без авторизации
    """
    # Создаем канал
    create_response = await ac.post(
        "/channels",
        json=channel_test_data.model_dump()
    )
    assert create_response.status_code == 201
    
    # Удаляем cookies для симуляции неавторизованного пользователя
    ac.cookies.clear()
    
    # Пытаемся удалить канал
    delete_response = await ac.delete(f"/channels/{channel_test_data.id}")
    assert delete_response.status_code == 401

