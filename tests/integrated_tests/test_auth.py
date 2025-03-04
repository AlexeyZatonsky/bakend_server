import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession



from src.auth.schemas import UserCreate, UserRead, UserLogin
from src.auth.models import Users, SecretInfo


TEST_EMAIL = "test@example.com"
TEST_USERNAME = "testuser"
TEST_PASSWORD = "testpassword123"
WRONG_PASSWORD = "wrongpassword"
NONEXISTENT_EMAIL = "nonexistent@example.com"





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
def user_data_model() -> UserCreate:
    """Создает тестовые данные для регистрации пользователя."""
    return UserCreate(
        email=TEST_EMAIL,
        username=TEST_USERNAME,
        password=TEST_PASSWORD
    )

@pytest.fixture(scope="session")
def user_login_data(user_data_model: UserCreate) -> UserLogin:
    """Создает тестовые данные для входа пользователя на основе данных регистрации."""
    return UserLogin(
        email=user_data_model.email,
        password=user_data_model.password
    )
        


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
        "username": user_data_model.email,
        "password": WRONG_PASSWORD
    }
    response = await ac.post("/auth/login", data=login_form_data)
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"


@pytest.mark.asyncio(loop_scope="session")
async def test_login_nonexistent_email(
    user_login_data: UserLogin,
    ac: AsyncClient
):
    """
    Тестирует попытку входа с несуществующим email.
    Проверяет корректную обработку ошибки.
    """
    login_form_data = {
        "username": NONEXISTENT_EMAIL,
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


