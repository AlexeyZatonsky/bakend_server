import pytest 
import pytest_asyncio
import asyncio
from httpx import AsyncClient
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr


import sys, pathlib
root_dir = pathlib.Path(__file__).resolve().parents[1]   #  …/bakend_server
sys.path.insert(0, str(root_dir)) 
from src.auth.schemas import UserCreateSchema, UserLoginSchema





TEST_EMAIL = "test@example.com"
TEST_USERNAME = "testuser"
TEST_PASSWORD = "TesTpassword123"
WRONG_PASSWORD = "wrongpassword"
NONEXISTENT_EMAIL = "nonexistent@example.com"
TEST_channel_id = "test_channel"
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
    test_channel_id: str = TEST_channel_id
    test_user_avatar: str = TEST_USER_AVATAR
    test_channel_avatar: str = TEST_CHANNEL_AVATAR



@pytest.fixture(scope="session")
def test_user_data() -> UserTestData:
    """Фикстура для получения тестовых данных пользователя"""
    return UserTestData()

@pytest.fixture(scope="session")
def user_data_model(test_user_data: UserTestData) -> UserCreateSchema:
    """Создает тестовые данные для регистрации пользователя."""
    return UserCreateSchema(
        email=test_user_data.test_user_email,
        password=test_user_data.test_password
    )


@pytest.fixture(scope="session")
def user_login_data(test_user_data: UserTestData) -> UserLoginSchema:
    """Создает тестовые данные для входа пользователя."""
    return UserLoginSchema(
        email=test_user_data.test_user_email,
        password=test_user_data.test_password
    )


