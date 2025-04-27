import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete

from src.auth.exceptions import AuthHTTPExceptions
from src.auth.schemas import UserCreateSchema, UserReadSchema, UserLoginSchema
from src.auth.models import UsersORM, SecretInfoORM

from tests.integrated_tests.conftest import UserTestData  # если у вас есть такой фикстурный датакласс


@pytest.mark.asyncio()
async def test_register_creates_user_and_secret(
    user_data_model: UserCreateSchema,
    session: AsyncSession,
    ac: AsyncClient,
):
    """
    Регистрируем нового пользователя и проверяем:
     - HTTP 201
     - Появление записи в UsersORM
     - Появление связанной записи в SecretInfoORM
    """
    # Act
    resp = await ac.post("/auth/register", json=user_data_model.model_dump())
    assert resp.status_code == 201

    # Преобразуем ответ в DTO
    user_out = UserReadSchema.model_validate(resp.json())

    # Assert: в таблице users появилась запись с ровно таким id
    row = await session.execute(
        select(UsersORM).where(UsersORM.id == user_out.id)
    )
    db_user = row.scalar_one()
    assert db_user.id == user_out.id

    # Assert: в secret_info тоже есть запись и email совпадает
    row = await session.execute(
        select(SecretInfoORM).where(SecretInfoORM.id == user_out.id)
    )
    db_secret = row.scalar_one()
    assert db_secret.email == user_data_model.email


@pytest.mark.asyncio()
async def test_duplicate_email_register(
    user_data_model: UserCreateSchema,
    session: AsyncSession,
    ac: AsyncClient,
):
    """
    Если регистрируем дважды одного и того же email,
    во второй раз — HTTP 409 и в БД по-прежнему ровно по одной записи.
    """
    # первая
    r1 = await ac.post("/auth/register", json=user_data_model.model_dump())
    assert r1.status_code == 201

    # вторая
    r2 = await ac.post("/auth/register", json=user_data_model.model_dump())
    
    assert r2.status_code == 409

    # в БД — одна запись
    users = (await session.execute(select(UsersORM))).scalars().all()
    secrets = (await session.execute(select(SecretInfoORM))).scalars().all()
    assert len(users) == 1
    assert len(secrets) == 1


@pytest.mark.asyncio()
async def test_successful_login(
    user_data_model: UserCreateSchema,
    user_login_data: UserLoginSchema,
    ac: AsyncClient,
):
    """
    Регистрация -> логин -> 200 + в теле и cookies есть access_token
    """
    await ac.post("/auth/register", json=user_data_model.model_dump())

    login_data = {
        "username": user_login_data.email,  # OAuth2PasswordRequestForm ждёт поле 'username'
        "password": user_login_data.password,
    }

    r = await ac.post("/auth/login", data=login_data)
    assert r.status_code == 200
    body = r.json()

    assert "access_token" in body
    assert "access_token" in r.cookies


@pytest.mark.asyncio()
async def test_login_wrong_password(
    user_data_model: UserCreateSchema,
    test_user_data: UserTestData,
    ac: AsyncClient,
):
    """
    Попытка логина с неправильным паролем даёт 401 и detail="Incorrect email or password"
    """
    await ac.post("/auth/register", json=user_data_model.model_dump())

    r = await ac.post("/auth/login", data={
        "username": test_user_data.test_user_email,
        "password": test_user_data.test_wrong_password,
    })
    assert r.status_code == 401
    assert r.json()["detail"] == "Incorrect email or password"


@pytest.mark.asyncio()
async def test_login_nonexistent_email(
    test_user_data: UserTestData,
    user_login_data: UserLoginSchema,
    ac: AsyncClient,
):
    """
    Логин несуществующим email → 401
    """
    r = await ac.post("/auth/login", data={
        "username": test_user_data.test_nonexistent_email,
        "password": user_login_data.password,
    })
    assert r.status_code == 401


@pytest.mark.asyncio()
async def test_logout_after_login(
    user_data_model: UserCreateSchema,
    user_login_data: UserLoginSchema,
    ac: AsyncClient,
):
    """
    Регистрация → логин → logout → токен из cookies выпал
    """
    await ac.post("/auth/register", json=user_data_model.model_dump())
    login = await ac.post("/auth/login", data={
        "username": user_login_data.email,
        "password": user_login_data.password,
    })
    assert login.status_code == 200
    assert "access_token" in login.cookies

    logout = await ac.post("/auth/logout")
    assert logout.status_code == 200
    assert "access_token" not in logout.cookies


@pytest.mark.asyncio()
async def test_logout_without_login(ac: AsyncClient):
    """
    Логаут без логина → 200 + токена нет
    """
    r = await ac.post("/auth/logout")
    assert r.status_code == 200
    assert "access_token" not in r.cookies
