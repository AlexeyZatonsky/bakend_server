from collections.abc import Collection
from datetime import UTC, datetime
from uuid import UUID

from fastapi import Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_async_session

from ..auth.schemas import UserReadSchema
from ..auth.dependencies import get_current_user

from ..courses.dependencies import course_is_open

from .permissionsEnum import PermissionsEnum
from .repository import PermissionRepository
from .service import PermissionsService
from .schemas import PermissionReadSchema
from .exceptions import PermissionsHTTPExceptions

import logging
from ..core.log import configure_logging



logger = logging.getLogger(__name__)
configure_logging()




async def get_permissions_service(session:AsyncSession = Depends(get_async_session)) -> PermissionsService:
    logger.debug("get_permissions_service")
    
    repository = PermissionRepository(session)
    http_exceptions = PermissionsHTTPExceptions()
    return PermissionsService(repository, http_exceptions)



def require_permission(
    access_level: PermissionsEnum | Collection[PermissionsEnum] | None = None,
    course_id_param: str = "course_id",
    *,
    skip_if_public: bool = True,
):
    """
    Возвращает **dependency‑функцию**, проверяющую наличие права пользователя
    на курс.

    * `access_level=None`  → достаточно *любого* актуального права;  
      иначе — нужно хотя бы одно из переданных уровней.
    * `skip_if_public=True` — если курс `is_public`, проверка прав пропускается.

    Возвращает `PermissionReadSchema` или `None` (когда проверку пропустили).
    Бросает HTTP‑403, если право не найдено / просрочено / уровень не подходит.
    """
    # ─── 0. Предварительно нормализуем требуемые уровни доступа ───
    if access_level is None:
        required_levels: set[str] | None = None
    elif isinstance(access_level, PermissionsEnum):
        required_levels = {access_level.value}
    else:  # iterable of enums
        required_levels = {lv.value for lv in access_level}

    # ─── helpers ──────────────────────────────────────────────────
    def _expired(expiration: datetime | None) -> bool:
        return bool(expiration and expiration < datetime.now(tz=UTC))

    def _is_allowed(level: str) -> bool:
        # если конкретных уровней не задано — подходит любой
        return required_levels is None or level in required_levels

    # ─── dependency‑функция ──────────────────────────────────────
    async def dependency(
        course_id: UUID = Path(..., alias=course_id_param),
        user: UserReadSchema = Depends(get_current_user),
        permissions_service: PermissionsService = Depends(get_permissions_service),
    ) -> PermissionReadSchema | None:
        logger.debug("require_permission: start check (course_id=%s)", course_id)

        # 1. Публичный курс — права не требуются
        if skip_if_public and await course_is_open(course_id):
            logger.debug("Course is public → permission check skipped")
            return None

        # 2. Ищем право
        perm = await permissions_service.get_course_permission_for_user(
            user.id, course_id
        )
        if not perm:
            raise permissions_service.http_exceptions.forbidden_403()

        # 3. Срок
        if _expired(perm.expiration_date):
            raise permissions_service.http_exceptions.forbidden_403("Permission expired")

        # 4. Уровень
        if not _is_allowed(perm.access_level):
            raise permissions_service.http_exceptions.forbidden_403("You don't have permission for this action")

        logger.debug("require_permission: success for user %s", user.id)
        return perm

    return dependency

