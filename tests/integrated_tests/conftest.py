import pytest 
import pytest_asyncio

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

@pytest.mark.skip(reason="Not a test class")
class UserTestData(BaseModel):
    """Тестовые данные для пользователя"""
    email: EmailStr = "test@example.com"
    username: str = "testuser"
    password: str = "testpassword123"
    wrong_password: str = "wrongpassword"
    nonexistent_email: EmailStr = "nonexistent@example.com"

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
        email=test_user_data.email,
        username=test_user_data.username,
        password=test_user_data.password
    )


@pytest.fixture(scope="session")
def user_login_data(test_user_data: UserTestData) -> UserLogin:
    """Создает тестовые данные для входа пользователя."""
    return UserLogin(
        email=test_user_data.email,
        password=test_user_data.password
    )



