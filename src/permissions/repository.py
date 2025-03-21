from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .models import AccessLevelEnum, UsersPermissionsORM



class PermissionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session


    async def get_by_user_id_and_course_id(self, user_id: int, course_id: int) -> UsersPermissionsORM | None:
        query = select(UsersPermissionsORM).where(UsersPermissionsORM.user_id == user_id, UsersPermissionsORM.course_id == course_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    

    async def create_permission(self, permission: UsersPermissionsORM) -> UsersPermissionsORM:
        self.session.add(permission)
        await self.session.commit()
        await self.session.refresh(permission)
        return permission
    

    async def get_all(self, limit: int = 20) -> list[UsersPermissionsORM]:
        query = select(UsersPermissionsORM).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()
    

    async def delete(self, permission: UsersPermissionsORM) -> None:
        await self.session.delete(permission)
        await self.session.commit() 