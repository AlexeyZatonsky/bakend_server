from typing import List
from fastapi import APIRouter, Depends, status, HTTPException
from uuid import UUID

from ..auth.dependencies import get_current_user
from ..auth.schemas import UserReadSchema

from ..channels.service import ChannelService
from ..channels.dependencies import get_channel_service, get_current_channel
from ..channels.schemas import ChannelReadSchema

from .dependencies import get_course_service, get_current_course_with_owner_validate
from .service import CourseService
from .schemas import (
    CourseCreateSchema, CourseUpdateSchema, CourseReadSchema
)

router = APIRouter(tags=["Courses"])

# 🔹 Все публичные курсы (для поиска и каталога)
@router.get("/courses", response_model=List[CourseReadSchema])
async def get_all_courses(
    course_service: CourseService = Depends(get_course_service),
):
    return await course_service.get_all_public_courses()


# 🔹 Получить курс по ID (TODO: нужно реализовать)
@router.get("/courses/{course_id}", response_model=CourseReadSchema)
async def get_course_by_id(course_id: UUID):
    # TODO: использовать get_by_id, возможно без прав
    pass


# 🔹 Курсы всех каналов пользователя
@router.get("/users/{user_id}/channels/courses", response_model=List[CourseReadSchema])
async def get_user_courses(
    user_id: UUID,
    course_service: CourseService = Depends(get_course_service),
    channel_service: ChannelService = Depends(get_channel_service),
):
    return await course_service.get_courses_by_user(user_id, channel_service)


@router.post("/channels/{channel_id}/courses", response_model=CourseReadSchema, status_code=status.HTTP_201_CREATED)
async def create_course(
    course_data: CourseCreateSchema,
    channel: ChannelReadSchema = Depends(get_current_channel),  # проверка владельца
    course_service: CourseService = Depends(get_course_service),
):
    return await course_service.create(course_data, channel)


@router.delete("/channels/{channel_id}/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(
    course: CourseReadSchema = Depends(get_current_course_with_owner_validate),  # проверка владельца курса
    course_service: CourseService = Depends(get_course_service),
):
    await course_service.delete_course(course)


@router.patch("/channels/{channel_id}/courses/{course_id}", response_model=CourseReadSchema)
async def patch_course(
    update_data: CourseUpdateSchema,
    course: CourseReadSchema = Depends(get_current_course_with_owner_validate),  # проверка владельца курса
    course_service: CourseService = Depends(get_course_service),
):
    return await course_service.update_course(course, update_data)

@router.get("/channels/{channel_id}/courses", response_model=List[CourseReadSchema])
async def get_channel_courses(
    channel: ChannelReadSchema = Depends(get_current_channel),  # проверка владельца
    course_service: CourseService = Depends(get_course_service),
):
    return await course_service.get_courses_by_channel(channel)