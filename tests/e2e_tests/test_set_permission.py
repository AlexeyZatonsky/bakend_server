# tests/e2e/test_permissions.py
from httpx import AsyncClient, HTTPStatusError
import pytest
from uuid import UUID

from src.permissions.permissionsEnum import PermissionsEnum

@pytest.mark.asyncio
async def test_owner_grants_moderator_ok(
    registered_users,         # owner, collaborator, stranger
    ac: AsyncClient,
    channel_factory,
    course_factory,
    grant_permission_factory,
):
    owner, collaborator, _ = registered_users

    channel = await channel_factory(owner.id)
    course  = await course_factory(owner.id, channel.id)

    perm = await grant_permission_factory(
        owner.id, collaborator.id, course.id, PermissionsEnum.MODERATOR
    )

    assert perm.user_id   == collaborator.id
    assert perm.course_id == course.id
    assert perm.access_level == PermissionsEnum.MODERATOR.value


@pytest.mark.asyncio
async def test_non_owner_cannot_grant(
    registered_users,
    authed_clients,
    channel_factory,
    course_factory,
    grant_permission_factory,
):
    owner, _, stranger = registered_users

    channel = await channel_factory(owner.id)
    course  = await course_factory(owner.id, channel.id)

    # stranger пытается выдать себе MODERATOR
    with pytest.raises(HTTPStatusError) as err:
        await grant_permission_factory(
            stranger.id, stranger.id, course.id, PermissionsEnum.MODERATOR
        )
    assert err.value.response.status_code == 403  # проверяем запрет
