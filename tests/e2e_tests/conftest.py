# tests/e2e/conftest.py
import asyncio
from typing import List, Dict, Callable, Awaitable
from uuid import UUID

import pytest
import pytest_asyncio
from faker import Faker
from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient, ASGITransport

from src.app import app
from src.channels.schemas import ChannelReadSchema
from src.courses.schemas import CourseCreateSchema, CourseReadSchema
from src.permissions.schemas import PermissionCreateSchema, PermissionReadSchema
from src.permissions.permissionsEnum import PermissionsEnum

fake = Faker("ru_RU")


class TestUser:
    def __init__(self, index: int):
        self.email = f"user_{index}@example.com"
        self.password = f"User_{index}_PSWD"


# Получаем список пользователей
@pytest.fixture(scope="function")
def raw_users() -> List[TestUser]:
    return [TestUser(i) for i in range(1, 4)]


async def _register_user(ac: AsyncClient, user: TestUser) -> None:
    await ac.post("/auth/register", json={"email": user.email, "password": user.password})
    r = await ac.post("/auth/login", data={"username": user.email, "password": user.password})
    user.token = r.json()["access_token"]

    me = await ac.get("/auth/me", headers={"Authorization": f"Bearer {user.token}"})
    user.id = me.json()["id"]


@pytest_asyncio.fixture(scope="function")
async def registered_users(raw_users: List[TestUser], ac: AsyncClient) -> List[TestUser]:
    await asyncio.gather(*(_register(ac, u) for u in raw_users))
    return raw_users


# ────────────────────────────────
# авторизованные клиенты
# ────────────────────────────────
@pytest_asyncio.fixture(scope="function")
async def authed_clients(
    registered_users: List[TestUser],
    ac: AsyncClient,
) -> Dict[str, AsyncClient]:
    """
    user_id → AsyncClient с заголовком Authorization.
    Cookies умышленно не копируем, чтобы не тащить чужие access_token.
    """
    result: Dict[str, AsyncClient] = {}
    for u in registered_users:
        result[u.id] = AsyncClient(
            transport=ac._transport,          # общий ASGITransport
            base_url=ac.base_url,
            headers={"Authorization": f"Bearer {u.token}"},
        )
    yield result
    await asyncio.gather(*(c.aclose() for c in result.values()))


# ────────────────────────────────
# фабрики-утилиты
# ────────────────────────────────
@pytest_asyncio.fixture
async def channel_factory(
    authed_clients: Dict[str, AsyncClient],
) -> Callable[[str], Awaitable[ChannelReadSchema]]:
    async def _create(owner_id: str) -> ChannelReadSchema:
        c = authed_clients[owner_id]
        payload = {"id": fake.slug().replace("-", ""), "avatar": fake.image_url()}
        r = await c.post("/channels", json=payload)
        r.raise_for_status()
        return ChannelReadSchema.model_validate(r.json())

    return _create


@pytest_asyncio.fixture
async def course_factory(
    authed_clients: Dict[str, AsyncClient],
) -> Callable[[str, str], Awaitable[CourseReadSchema]]:
    async def _create(user_id: str, channel_id: str) -> CourseReadSchema:
        client = authed_clients[user_id]
        payload = CourseCreateSchema(name=fake.catch_phrase()).model_dump()
        r = await client.post(f"/channels/{channel_id}/courses", json=payload)
        r.raise_for_status()
        return CourseReadSchema.model_validate(r.json())

    return _create


@pytest_asyncio.fixture
async def grant_permission_factory(
    authed_clients: Dict[str, AsyncClient],
) -> Callable[[str, str, str, PermissionsEnum], Awaitable[PermissionReadSchema]]:
    """
    grant(granter_id, target_user_id, course_id, level) → PermissionReadSchema
    Требование: granter — владелец канала курса.
    """

    async def _grant(
        granter_id: str,
        target_user_id: UUID,
        course_id: UUID,
        level: PermissionsEnum = PermissionsEnum.MODERATOR,
    ) -> PermissionReadSchema:
        client = authed_clients[granter_id]
        payload = jsonable_encoder(
            PermissionCreateSchema(
                user_id=target_user_id,
                course_id=course_id,
                access_level=level,
            )
        )
        r = await client.post(f"/courses/{course_id}/permissions", json=payload)
        r.raise_for_status()
        return PermissionReadSchema.model_validate(r.json())

    return _grant
