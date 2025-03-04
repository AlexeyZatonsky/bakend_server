import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select, delete
from src.auth.schemas import UserCreate, UserRead, UserLogin
from src.auth.models import Users, SecretInfo
from src.app import app
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase
from typing import Type, List, AsyncGenerator
from pytest import mark, fixture
from pytest_asyncio import fixture as async_fixture


@async_fixture(autouse=True)
async def clean_tables(session: AsyncSession):    
    yield

    await session.execute(delete(Users))
    await session.execute(delete(SecretInfo))
    await session.commit()

@pytest.fixture()
def user_data_model() -> UserCreate:
    return UserCreate(
        email="test@example.com",
        username="testuser",
        password="testpassword123"
    )

@pytest.fixture()
def user_login_data(user_data_model: UserCreate) -> UserLogin:
    return UserLogin(
        email=user_data_model.email,
        password=user_data_model.password
    )
        


@mark.asyncio(loop_scope="session")
async def test_register_new_user(
    user_data_model: UserCreate, 
    session: AsyncSession,
    ac: AsyncClient):
    
    response = await ac.post("/auth/register", json=user_data_model.model_dump())
    
    assert response.status_code == 201
    user_response = UserRead.model_validate(response.json())
    
    db_user = await session.execute(
        select(Users)
        .where(Users.id == user_response.id)
    )
    db_user = db_user.scalar_one()
    assert db_user.username == user_data_model.username
    
    db_secret = await session.execute(
        select(SecretInfo).where(SecretInfo.user_id == user_response.id)
    )
    db_secret = db_secret.scalar_one()
    assert db_secret.email == user_data_model.email
    
@mark.asyncio(loop_scope="session")
async def test_duplicate_email_register(
    user_data_model: UserCreate, 
    session: AsyncSession,
    ac: AsyncClient
):
    
    # Первая регистрация
    response = await ac.post("/auth/register", json=user_data_model.model_dump())
    assert response.status_code == 201
    
    # Вторая регистрация с тем же email
    response = await ac.post("/auth/register", json=user_data_model.model_dump())
    assert response.status_code == 400
    error_data = response.json()
    
    # Проверяем детали ошибки
    assert error_data == {
        "detail": "Email already registered"
    }
    
    # Проверяем количество записей в БД
    assert len((await session.execute(select(Users))).scalars().all()) == 1
    assert len((await session.execute(select(SecretInfo))).scalars().all()) == 1

@mark.asyncio(loop_scope="session")
async def test_successful_login(
    user_data_model: UserCreate,
    user_login_data: UserLogin,
    ac: AsyncClient
):
    # Регистрируем пользователя
    await ac.post("/auth/register", json=user_data_model.model_dump())
    
    # Отправляем данные в формате, который ожидает OAuth2PasswordRequestForm
    login_form_data = {
        "username": user_login_data.email,  # OAuth2 использует username, но мы передаем email
        "password": user_login_data.password
    }
    
    response = await ac.post("/auth/login", data=login_form_data)
    
    print(response.json())
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "access_token" in response.cookies
    
@mark.asyncio(loop_scope="session")
async def test_login_wrong_password(
    user_data_model: UserCreate,
    ac: AsyncClient
):
    await ac.post("/auth/register", json=user_data_model.model_dump())
    
    login_form_data = {
        "username": user_data_model.email,
        "password": "wrongpassword"
    }
    response = await ac.post("/auth/login", data=login_form_data)
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"

@mark.asyncio(loop_scope="session")
async def test_login_nonexistent_email(
    user_login_data: UserLogin,
    ac: AsyncClient
):
    login_form_data = {
        "username": "nonexistent@example.com",
        "password": user_login_data.password
    }
    response = await ac.post("/auth/login", data=login_form_data)
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"


