import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from conftest import UserTestData

from src.auth.schemas import UserCreate, UserRead, UserLogin
from src.auth.models import Users, SecretInfo





@pytest.mark.asyncio(loop_scope="session")
async def test_register_new_user(
    user_data_model: UserCreate, 
    session: AsyncSession,
    ac: AsyncClient):
    
    """
    Тестирует успешную регистрацию нового пользователя.
    Проверяет:
    - Статус ответа
    - Создание записи в таблице Users
    - Создание записи в таблице SecretInfo
    """
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
    
    
@pytest.mark.asyncio(loop_scope="session")
async def test_duplicate_email_register(
    user_data_model: UserCreate, 
    session: AsyncSession,
    ac: AsyncClient
):
    """
    Тестирует попытку регистрации с уже существующим email.
    Проверяет:
    - Успешную первую регистрацию
    - Ошибку при повторной регистрации
    - Отсутствие дублирования записей в БД
    """
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


@pytest.mark.asyncio(loop_scope="session")
async def test_successful_login(
    user_data_model: UserCreate,
    user_login_data: UserLogin,
    ac: AsyncClient
):
    """
    Тестирует успешный вход пользователя.
    Проверяет:
    - Успешную регистрацию
    - Успешный вход
    - Наличие токена в ответе и cookies
    """
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
    
    
@pytest.mark.asyncio(loop_scope="session")
async def test_login_wrong_password(
    user_data_model: UserCreate,
    test_user_data: UserTestData,
    ac: AsyncClient
):
    """
    Тестирует попытку входа с неверным паролем.
    Проверяет:
    - Успешную регистрацию
    - Ошибку при входе с неверным паролем
    """
    await ac.post("/auth/register", json=user_data_model.model_dump())
    
    login_form_data = {
        "username": test_user_data.test_user_email,
        "password": test_user_data.test_wrong_password
    }
    response = await ac.post("/auth/login", data=login_form_data)
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"


@pytest.mark.asyncio(loop_scope="session")
async def test_login_nonexistent_email(
    test_user_data: UserTestData,
    user_login_data: UserLogin,
    ac: AsyncClient
):
    """
    Тестирует попытку входа с несуществующим email.
    Проверяет корректную обработку ошибки.
    """
    login_form_data = {
        "username": test_user_data.test_nonexistent_email,
        "password": user_login_data.password
    }
    response = await ac.post("/auth/login", data=login_form_data)
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"


@pytest.mark.asyncio(loop_scope="session")
async def test_logout_after_login(
    user_data_model: UserCreate,
    user_login_data: UserLogin,
    ac: AsyncClient
):
    """
    Тестирует выход после успешного входа.
    Проверяет:
    - Успешную регистрацию и вход
    - Успешный выход
    - Удаление токена из cookies
    """
    """Регистрация + Авторизация + Логаут"""  
    await ac.post("/auth/register", json=user_data_model.model_dump())
    
    login_form_data = {
        "username": user_login_data.email,
        "password": user_login_data.password
    }
    login_response = await ac.post("/auth/login", data=login_form_data)
    assert login_response.status_code == 200
    assert "access_token" in login_response.cookies
    
    
    logout_response = await ac.post("/auth/logout")
    assert logout_response.status_code == 200
    assert logout_response.json() == {"detail": "Successfully logged out"}
    
    
    assert "access_token" not in logout_response.cookies
    
    
@pytest.mark.asyncio(loop_scope="session")
async def test_logout_without_login(ac: AsyncClient):
    """
    Тестирует выход без предварительного входа.
    Проверяет корректную обработку выхода для неавторизованного пользователя.
    """
    response = await ac.post("/auth/logout")
    
    assert response.status_code == 200
    assert response.json() == {"detail": "Successfully logged out"}
    assert "access_token" not in response.cookies


