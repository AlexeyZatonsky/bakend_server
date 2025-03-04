import pytest 
import pytest_asyncio
import asyncio
from httpx import AsyncClient
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr

from src.auth.models import Users, SecretInfo
from src.auth.schemas import UserCreate, UserLogin




TEST_EMAIL = "test@example.com"
TEST_USERNAME = "testuser"
TEST_PASSWORD = "testpassword123"
WRONG_PASSWORD = "wrongpassword"
NONEXISTENT_EMAIL = "nonexistent@example.com"
TEST_CHANNEL_NAME = "test_channel"
TEST_USER_AVATAR = "https://example.com/avatar.png"
TEST_CHANNEL_AVATAR = "https://example.com/channel_avatar.png"

@pytest.mark.skip(reason="Not a test class")
class UserTestData(BaseModel):
    """Тестовые данные для пользователя"""
    test_user_email: EmailStr = TEST_EMAIL
    test_username: str = TEST_USERNAME
    test_password: str = TEST_PASSWORD
    test_wrong_password: str = WRONG_PASSWORD
    test_nonexistent_email: EmailStr = NONEXISTENT_EMAIL
    test_channel_name: str = TEST_CHANNEL_NAME
    test_user_avatar: str = TEST_USER_AVATAR
    test_channel_avatar: str = TEST_CHANNEL_AVATAR


@pytest_asyncio.fixture(autouse=True)
async def clean_tables(session: AsyncSession):    
    """
    Автоматически очищает таблицы до и после каждого теста.
    Использует каскадное удаление: удаление из Users автоматически удалит записи из SecretInfo.
    """
    yield

    await session.execute(delete(Users))
    await session.execute(delete(SecretInfo))
    await session.commit()




@pytest.fixture(scope="session")
def test_user_data() -> UserTestData:
    """Фикстура для получения тестовых данных пользователя"""
    return UserTestData()


@pytest_asyncio.fixture(autouse=True)
async def clean_tables(session: AsyncSession):    
    """
    Автоматически очищает таблицы до и после каждого теста.
    Использует каскадное удаление: удаление из Users автоматически удалит записи из SecretInfo.
    """
    yield

    await session.execute(delete(Users))
    await session.execute(delete(SecretInfo))
    await session.commit()

@pytest.fixture(scope="session")
def user_data_model(test_user_data: UserTestData) -> UserCreate:
    """Создает тестовые данные для регистрации пользователя."""
    return UserCreate(
        email=test_user_data.test_user_email,
        username=test_user_data.test_username,
        password=test_user_data.test_password
    )


@pytest.fixture(scope="session")
def user_login_data(test_user_data: UserTestData) -> UserLogin:
    """Создает тестовые данные для входа пользователя."""
    return UserLogin(
        email=test_user_data.test_user_email,
        password=test_user_data.test_password
    )


@pytest.fixture(scope="session")
def event_loop():
    """Создает event loop для всей тестовой сессии"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()



