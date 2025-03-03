import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select, delete
from src.auth.schemas import UserCreate, UserRead
from src.auth.models import Users, SecretInfo
from src.app import app
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase
from typing import Type, List, AsyncGenerator


@pytest.fixture()
def user_data_model() -> UserCreate:
    return UserCreate(
        email="test@example.com",
        username="testuser",
        password="testpassword123"
    )

        


@pytest.mark.asyncio(loop_scope="session")
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
    
    await session.execute(delete(Users))
    await session.commit()
        
@pytest.mark.asyncio(loop_scope="session")
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
    
    await session.execute(delete(Users))
    await session.commit()


