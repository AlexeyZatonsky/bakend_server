"""
Тесты для роутера аутентификации.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import uuid
from fastapi import FastAPI, status, Depends
from fastapi.testclient import TestClient
from httpx import AsyncClient
import jwt
from datetime import datetime, timedelta

from src.auth.router import router as auth_router
from src.auth.dependencies import get_auth_service, get_current_user
from src.auth.schemas import UserReadSchema, UserCreateSchema, UserLoginSchema
from src.auth.service import AuthService

pytestmark = pytest.mark.asyncio


@pytest.fixture
def mock_auth_service():
    """Фикстура для мока сервиса аутентификации."""
    return AsyncMock()


@pytest.fixture
def app(mock_auth_service):
    """Фикстура для создания тестового приложения FastAPI."""
    app = FastAPI()
    
    # Патчим зависимость get_auth_service
    async def override_get_auth_service():
        return mock_auth_service
    
    # Патчим зависимость get_current_user
    test_user = UserReadSchema(
        id=uuid.uuid4(),
        username="test_user",
        email="test@example.com",
        is_verified=False,
        is_active=True,
        avatar=None,
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat()
    )
    
    async def override_get_current_user(token: str = Depends(get_auth_service)):
        return test_user
    
    app.dependency_overrides[get_auth_service] = override_get_auth_service
    app.dependency_overrides[get_current_user] = override_get_current_user
    
    app.include_router(auth_router, prefix="/auth")
    return app


@pytest.fixture
def test_client(app):
    """Фикстура для создания тестового клиента."""
    return TestClient(app)


async def test_register_success(test_client, mock_auth_service):
    """Тест успешной регистрации пользователя."""
    # Настраиваем мок
    test_user = UserReadSchema(
        id=uuid.uuid4(),
        username="new_user",
        email="new_user@example.com",
        is_verified=False,
        is_active=True,
        avatar=None,
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat()
    )
    mock_auth_service.create_user.return_value = test_user
    
    # Отправляем запрос на регистрацию
    response = test_client.post(
        "/auth/register",
        json={
            "email": "new_user@example.com",
            "password": "Password123!"
        }
    )
    
    # Проверяем результат
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["id"] == str(test_user.id)
    assert data["username"] == test_user.username
    assert data["email"] == test_user.email
    
    # Проверяем вызов метода сервиса
    mock_auth_service.create_user.assert_called_once()
    call_args = mock_auth_service.create_user.call_args[0][0]
    assert call_args.email == "new_user@example.com"
    assert call_args.password == "Password123!"


async def test_register_existing_email(test_client, mock_auth_service):
    """Тест регистрации с уже существующим email."""
    # Настраиваем мок для выброса исключения
    from fastapi import HTTPException
    mock_auth_service.create_user.side_effect = HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="User with this email already exists"
    )
    
    # Отправляем запрос на регистрацию
    response = test_client.post(
        "/auth/register",
        json={
            "email": "existing@example.com",
            "password": "Password123!"
        }
    )
    
    # Проверяем результат
    assert response.status_code == status.HTTP_409_CONFLICT
    data = response.json()
    assert "already exists" in data["detail"]
    
    # Проверяем вызов метода сервиса
    mock_auth_service.create_user.assert_called_once()


async def test_login_success(test_client, mock_auth_service):
    """Тест успешного входа в систему."""
    # Настраиваем моки
    test_user = UserReadSchema(
        id=uuid.uuid4(),
        username="test_user",
        email="test@example.com",
        is_verified=False,
        is_active=True,
        avatar=None,
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat()
    )
    mock_auth_service.authenticate_user.return_value = test_user
    mock_auth_service.create_access_token.return_value = "test_access_token"
    mock_auth_service.access_token_expire_minutes = 30
    
    # Отправляем запрос на вход
    response = test_client.post(
        "/auth/login",
        data={
            "username": "test@example.com",
            "password": "Password123!"
        }
    )
    
    # Проверяем результат
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["access_token"] == "test_access_token"
    assert data["token_type"] == "bearer"
    
    # Проверяем вызовы методов сервиса
    mock_auth_service.authenticate_user.assert_called_once_with(
        "test@example.com", "Password123!"
    )
    mock_auth_service.create_access_token.assert_called_once()
    call_args = mock_auth_service.create_access_token.call_args
    assert call_args[0][0]["sub"] == "test@example.com"
    assert isinstance(call_args[0][1], timedelta)


async def test_login_invalid_credentials(test_client, mock_auth_service):
    """Тест входа с неверными учетными данными."""
    # Настраиваем мок для возврата None при неверных учетных данных
    mock_auth_service.authenticate_user.return_value = None
    
    # Отправляем запрос на вход
    response = test_client.post(
        "/auth/login",
        data={
            "username": "test@example.com",
            "password": "WrongPassword"
        }
    )
    
    # Проверяем результат
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    data = response.json()
    assert "Incorrect" in data["detail"]
    
    # Проверяем вызов метода сервиса
    mock_auth_service.authenticate_user.assert_called_once_with(
        "test@example.com", "WrongPassword"
    )
    mock_auth_service.create_access_token.assert_not_called()


async def test_get_current_user(test_client, mock_auth_service):
    """Тест получения текущего пользователя."""
    # Не нужно настраивать моки, так как мы уже переопределили
    # зависимость get_current_user в фикстуре app
    
    # Отправляем запрос на получение текущего пользователя
    response = test_client.get(
        "/auth/me",
        headers={"Authorization": "Bearer test_token"}
    )
    
    # Проверяем результат
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == "test_user"
    assert data["email"] == "test@example.com"


async def test_get_current_user_no_token(test_client, mock_auth_service, app):
    """Тест получения текущего пользователя без токена."""
    # Переопределяем зависимость get_current_user для возврата исключения
    from fastapi import HTTPException
    
    async def override_get_current_user_failure(token: str = Depends(get_auth_service)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    app.dependency_overrides[get_current_user] = override_get_current_user_failure
    
    # Отправляем запрос на получение текущего пользователя без токена
    response = test_client.get("/auth/me")
    
    # Проверяем результат
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    data = response.json()
    assert "credentials" in data["detail"] 