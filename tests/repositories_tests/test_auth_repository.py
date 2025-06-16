"""
Тесты для репозитория аутентификации.
"""
import pytest
import uuid
from sqlalchemy import select
from src.auth.repository import AuthRepository, UserRepository, SecretInfoRepository
from src.auth.models import UsersORM, SecretInfoORM

pytestmark = pytest.mark.asyncio


async def test_user_repository_get_by_id(session):
    """Тест получения пользователя по ID из UserRepository."""
    # Создаем тестового пользователя
    test_user = UsersORM(
        username="test_user", 
        is_verified=False,
        is_active=True
    )
    session.add(test_user)
    await session.commit()
    await session.refresh(test_user)
    
    # Создаем репозиторий и получаем пользователя
    repo = UserRepository(session)
    user = await repo.get_by_id(test_user.id)
    
    # Проверяем результат
    assert user is not None
    assert user.id == test_user.id
    assert user.username == "test_user"


async def test_user_repository_get_by_username(session):
    """Тест получения пользователя по имени из UserRepository."""
    # Создаем тестового пользователя
    test_user = UsersORM(
        username="test_user", 
        is_verified=False,
        is_active=True
    )
    session.add(test_user)
    await session.commit()
    await session.refresh(test_user)
    
    # Создаем репозиторий и получаем пользователя
    repo = UserRepository(session)
    user = await repo.get_user_by_username("test_user")
    
    # Проверяем результат
    assert user is not None
    assert user.id == test_user.id
    assert user.username == "test_user"


async def test_secret_info_repository_get_by_email(session):
    """Тест получения секретной информации по email из SecretInfoRepository."""
    # Создаем тестового пользователя
    test_user = UsersORM(
        username="test_user", 
        is_verified=False,
        is_active=True
    )
    session.add(test_user)
    await session.flush()
    
    # Создаем секретную информацию
    test_secret = SecretInfoORM(
        user_id=test_user.id,
        email="test@example.com",
        hashed_password="hashed_password"
    )
    session.add(test_secret)
    await session.commit()
    
    # Создаем репозиторий и получаем секретную информацию
    repo = SecretInfoRepository(session)
    secret = await repo.get_by_email("test@example.com")
    
    # Проверяем результат
    assert secret is not None
    assert secret.user_id == test_user.id
    assert secret.email == "test@example.com"


async def test_auth_repository_create_user(session):
    """Тест создания пользователя через AuthRepository."""
    repo = AuthRepository(session)
    
    # Создаем пользователя
    from src.auth.schemas import UserCreateSchema
    user_data = UserCreateSchema(
        email="new_user@example.com",
        password="password123"
    )
    username = "new_user"
    hashed_password = "hashed_password"
    
    user = await repo.create_user(user_data, hashed_password, username)
    
    # Проверяем, что пользователь создан
    assert user is not None
    assert user.username == username
    
    # Проверяем наличие записи в БД
    db_user = await session.execute(
        select(UsersORM)
        .where(UsersORM.id == user.id)
    )
    db_user = db_user.scalar_one()
    assert db_user.username == username
    
    # Проверяем создание секретной информации
    db_secret = await session.execute(
        select(SecretInfoORM)
        .where(SecretInfoORM.user_id == user.id)
    )
    db_secret = db_secret.scalar_one()
    assert db_secret.email == user_data.email
    assert db_secret.hashed_password == hashed_password


async def test_auth_repository_get_user_by_email(session):
    """Тест получения пользователя и секретной информации по email через AuthRepository."""
    # Создаем тестового пользователя и секретную информацию
    test_user = UsersORM(
        username="test_user", 
        is_verified=False,
        is_active=True
    )
    session.add(test_user)
    await session.flush()
    
    test_secret = SecretInfoORM(
        user_id=test_user.id,
        email="test@example.com",
        hashed_password="hashed_password"
    )
    session.add(test_secret)
    await session.commit()
    
    # Получаем пользователя по email
    repo = AuthRepository(session)
    result = await repo.get_user_by_email("test@example.com")
    
    # Проверяем результат
    assert result is not None
    user, secret = result
    assert user.id == test_user.id
    assert user.username == "test_user"
    assert secret.email == "test@example.com"
    assert secret.hashed_password == "hashed_password"


async def test_auth_repository_update_user(session):
    """Тест обновления данных пользователя через AuthRepository."""
    # Создаем тестового пользователя
    test_user = UsersORM(
        username="test_user", 
        is_verified=False,
        is_active=True
    )
    session.add(test_user)
    await session.commit()
    await session.refresh(test_user)
    
    # Обновляем данные
    repo = AuthRepository(session)
    update_data = {"username": "updated_username", "is_verified": True}
    updated_user = await repo.update_user(test_user.id, update_data)
    
    # Проверяем результат
    assert updated_user is not None
    assert updated_user.username == "updated_username"
    assert updated_user.is_verified is True
    
    # Проверяем обновление в БД
    db_user = await session.execute(
        select(UsersORM)
        .where(UsersORM.id == test_user.id)
    )
    db_user = db_user.scalar_one()
    assert db_user.username == "updated_username"
    assert db_user.is_verified is True


async def test_auth_repository_delete_user(session):
    """Тест удаления пользователя через AuthRepository."""
    # Создаем тестового пользователя и секретную информацию
    test_user = UsersORM(
        username="test_user", 
        is_verified=False,
        is_active=True
    )
    session.add(test_user)
    await session.flush()
    
    test_secret = SecretInfoORM(
        user_id=test_user.id,
        email="test@example.com",
        hashed_password="hashed_password"
    )
    session.add(test_secret)
    await session.commit()
    
    # Удаляем пользователя
    repo = AuthRepository(session)
    success = await repo.delete_user(test_user.id)
    
    # Проверяем результат
    assert success is True
    
    # Проверяем, что пользователь удален из БД
    db_user = await session.execute(
        select(UsersORM)
        .where(UsersORM.id == test_user.id)
    )
    db_user = db_user.scalar_one_or_none()
    assert db_user is None
    
    # Проверяем, что секретная информация также удалена (каскадно)
    db_secret = await session.execute(
        select(SecretInfoORM)
        .where(SecretInfoORM.user_id == test_user.id)
    )
    db_secret = db_secret.scalar_one_or_none()
    assert db_secret is None 