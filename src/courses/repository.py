from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .models import CoursesORM, CoursesStructureORM



class CourseRepository:
    def __init__(self, session: AsyncSession):
        self.session = session




    async def get_by_id(self, course_id: UUID) -> CoursesORM | None:
        query = select(CoursesORM).where(CoursesORM.id == course_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_structure_by_id(self, course_id: UUID) -> CoursesStructureORM:
        pass
    

    async def create_course(self, course: CoursesORM) -> CoursesORM:    
        self.session.add(course)
        await self.session.commit()
        await self.session.refresh(course)
        return course


    async def get_all(self, limit: int = 20) -> list[CoursesORM]:
        query = select(CoursesORM).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_by_channel_name(self, channel_unique_name: str) -> list[CoursesORM]:
        query = select(CoursesORM).where(CoursesORM.channel_name == channel_unique_name)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def delete(self, course: CoursesORM) -> None:
        await self.session.delete(course)
        await self.session.commit()

