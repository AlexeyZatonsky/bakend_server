"""
Тесты для сервиса аутентификации.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import uuid
from datetime import datetime, timedelta, UTC
from fastapi import HTTPException

from src.auth.service import AuthService
from src.auth.models import UsersORM, SecretInfoORM
from src.auth.schemas import UserCreateSchema, UserReadSchema

pytestmark = pytest.mark.asyncio


@pytest.fixture
def mock_auth_repository():
    """Мок для репозитория аутентификации."""
    repo = AsyncMock()
    return repo


@pytest.fixture
def auth_service(mock_auth_repository):
    """Фикстура для сервиса аутентификации с моком репозитория."""
    service = AuthService(AsyncMock())
    service.repository = mock_auth_repository
    service.secret_key = "test_secret_key"
    service.algorithm = "HS256"
    service.access_token_expire_minutes = 30
    return service


@pytest.fixture
def test_user():
    """Фикстура для тестового пользователя."""
    return UsersORM(
        id=uuid.uuid4(),
        username="test_user",
        avatar=None,
        is_verified=False,
        is_active=True,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC)
    )


@pytest.fixture
def test_secret_info(test_user):
    """Фикстура для тестовой секретной информации."""
    return SecretInfoORM(
        user_id=test_user.id,
        email="test@example.com",
        hashed_password="hashed_password"
    )


async def test_verify_password(auth_service):
    """Тест верификации пароля."""
    # Патчим функцию verify из контекста паролей
    with patch("src.auth.service.pwd_context.verify") as mock_verify:
        mock_verify.return_value = True
        result = auth_service.verify_password("plain_password", "hashed_password")
        assert result is True
        mock_verify.assert_called_once_with("plain_password", "hashed_password")


async def test_get_password_hash(auth_service):
    """Тест хеширования пароля."""
    # Патчим функцию hash из контекста паролей
    with patch("src.auth.service.pwd_context.hash") as mock_hash:
        mock_hash.return_value = "hashed_password"
        result = auth_service.get_password_hash("plain_password")
        assert result == "hashed_password"
        mock_hash.assert_called_once_with("plain_password")


async def test_create_access_token(auth_service):
    """Тест создания токена доступа."""
    with patch("src.auth.service.jwt.encode") as mock_encode:
        mock_encode.return_value = "encoded_token"
        
        # Тест с указанным временем истечения
        expires_delta = timedelta(minutes=15)
        token = auth_service.create_access_token({"sub": "test@example.com"}, expires_delta)
        assert token == "encoded_token"
        
        # Проверяем, что encode был вызван с правильными параметрами
        assert mock_encode.call_count == 1
        args, kwargs = mock_encode.call_args
        assert "sub" in args[0]
        assert "exp" in args[0]
        assert args[1] == "test_secret_key"
        assert kwargs["algorithm"] == "HS256"
        
        # Сбрасываем мок
        mock_encode.reset_mock()
        
        # Тест без указания времени истечения
        token = auth_service.create_access_token({"sub": "test@example.com"})
        assert token == "encoded_token"
        
        # Проверяем, что encode был вызван с правильными параметрами
        assert mock_encode.call_count == 1
        args, kwargs = mock_encode.call_args
        assert "sub" in args[0]
        assert "exp" in args[0]
        assert args[1] == "test_secret_key"
        assert kwargs["algorithm"] == "HS256"


async def test_authenticate_user_success(auth_service, test_user, test_secret_info):
    """Тест успешной аутентификации пользователя."""
    # Настраиваем моки
    auth_service.repository.get_user_by_email.return_value = (test_user, test_secret_info)
    auth_service.verify_password = MagicMock(return_value=True)
    
    # Выполняем аутентификацию
    result = await auth_service.authenticate_user("test@example.com", "plain_password")
    
    # Проверяем результаты
    assert result is not None
    assert isinstance(result, UserReadSchema)
    assert result.id == test_user.id
    assert result.username == test_user.username
    assert result.email == test_secret_info.email
    
    # Проверяем вызовы методов
    auth_service.repository.get_user_by_email.assert_called_once_with("test@example.com")
    auth_service.verify_password.assert_called_once_with("plain_password", "hashed_password")


async def test_authenticate_user_wrong_password(auth_service, test_user, test_secret_info):
    """Тест аутентификации с неверным паролем."""
    # Настраиваем моки
    auth_service.repository.get_user_by_email.return_value = (test_user, test_secret_info)
    auth_service.verify_password = MagicMock(return_value=False)
    
    # Выполняем аутентификацию
    result = await auth_service.authenticate_user("test@example.com", "wrong_password")
    
    # Проверяем результаты
    assert result is None
    
    # Проверяем вызовы методов
    auth_service.repository.get_user_by_email.assert_called_once_with("test@example.com")
    auth_service.verify_password.assert_called_once_with("wrong_password", "hashed_password")


async def test_authenticate_user_nonexistent_email(auth_service):
    """Тест аутентификации с несуществующим email."""
    # Настраиваем моки
    auth_service.repository.get_user_by_email.return_value = None
    
    # Выполняем аутентификацию
    result = await auth_service.authenticate_user("nonexistent@example.com", "password")
    
    # Проверяем результаты
    assert result is None
    
    # Проверяем вызовы методов
    auth_service.repository.get_user_by_email.assert_called_once_with("nonexistent@example.com")


async def test_create_user_success(auth_service, test_user, test_secret_info):
    """Тест успешного создания пользователя."""
    # Настраиваем моки
    auth_service.repository.get_user_by_email.return_value = None
    auth_service.get_password_hash = MagicMock(return_value="hashed_password")
    auth_service._generate_username_from_email = MagicMock(return_value="generated_username")
    auth_service.repository.create_user.return_value = test_user
    auth_service.repository.get_user_by_email.side_effect = [None, (test_user, test_secret_info)]
    
    # Создаем пользователя
    user_data = UserCreateSchema(
        email="new_user@example.com",
        password="password123"
    )
    result = await auth_service.create_user(user_data)
    
    # Проверяем результаты
    assert result is not None
    assert isinstance(result, UserReadSchema)
    assert result.id == test_user.id
    assert result.username == test_user.username
    assert result.email == test_secret_info.email
    
    # Проверяем вызовы методов
    assert auth_service.repository.get_user_by_email.call_count == 2
    auth_service.get_password_hash.assert_called_once_with("password123")
    auth_service._generate_username_from_email.assert_called_once_with("new_user@example.com")
    auth_service.repository.create_user.assert_called_once_with(
        user_data, "hashed_password", "generated_username"
    )


async def test_create_user_existing_email(auth_service, test_user, test_secret_info):
    """Тест создания пользователя с уже существующим email."""
    # Настраиваем моки
    auth_service.repository.get_user_by_email.return_value = (test_user, test_secret_info)
    
    # Создаем пользователя с существующим email
    user_data = UserCreateSchema(
        email="existing@example.com",
        password="password123"
    )
    
    # Проверяем, что создание пользователя вызывает исключение
    with pytest.raises(HTTPException) as exc_info:
        await auth_service.create_user(user_data)
    
    # Проверяем детали исключения
    assert exc_info.value.status_code == 409
    assert "already exists" in exc_info.value.detail
    
    # Проверяем вызовы методов
    auth_service.repository.get_user_by_email.assert_called_once_with("existing@example.com")
    auth_service.repository.create_user.assert_not_called()


async def test_get_current_user_success(auth_service, test_user, test_secret_info):
    """Тест успешного получения текущего пользователя по токену."""
    # Патчим jwt.decode
    with patch("src.auth.service.jwt.decode") as mock_decode:
        mock_decode.return_value = {"sub": "test@example.com"}
        
        # Настраиваем моки
        auth_service.repository.get_user_by_email.return_value = (test_user, test_secret_info)
        
        # Получаем пользователя
        result = await auth_service.get_current_user("valid_token")
        
        # Проверяем результаты
        assert result is not None
        assert isinstance(result, UserReadSchema)
        assert result.id == test_user.id
        assert result.username == test_user.username
        assert result.email == test_secret_info.email
        
        # Проверяем вызовы методов
        mock_decode.assert_called_once_with("valid_token", "test_secret_key", algorithms=["HS256"])
        auth_service.repository.get_user_by_email.assert_called_once_with("test@example.com")


async def test_get_current_user_invalid_token(auth_service):
    """Тест получения пользователя по невалидному токену."""
    # Патчим jwt.decode для выброса исключения
    with patch("src.auth.service.jwt.decode") as mock_decode:
        from jose import JWTError
        mock_decode.side_effect = JWTError("Invalid token")
        
        # Проверяем, что получение пользователя вызывает исключение
        with pytest.raises(HTTPException) as exc_info:
            await auth_service.get_current_user("invalid_token")
        
        # Проверяем детали исключения
        assert exc_info.value.status_code == 401
        assert "credentials" in exc_info.value.detail
        
        # Проверяем вызовы методов
        mock_decode.assert_called_once_with("invalid_token", "test_secret_key", algorithms=["HS256"])
        auth_service.repository.get_user_by_email.assert_not_called()


async def test_delete_user_success(auth_service):
    """Тест успешного удаления пользователя."""
    # Настраиваем моки
    auth_service.repository.delete_user.return_value = True
    
    # Удаляем пользователя
    result = await auth_service.delete_user("user_id")
    
    # Проверяем результат
    assert result is True
    
    # Проверяем вызовы методов
    auth_service.repository.delete_user.assert_called_once() 