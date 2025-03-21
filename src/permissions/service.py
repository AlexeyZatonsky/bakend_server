from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


from fastapi import HTTPException

from ..auth.models import Users

from .models import UsersPermission, AccessLevelEnum
from .schemas import UsersPermissionsCreate, UsersPermissionsRead


class PermissionsService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_permissions(self, user: Users) -> UsersPermissionsRead:
        pass