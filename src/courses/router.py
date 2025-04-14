from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID


from ..auth.dependencies import get_current_user
from ..auth.schemas import UserReadSchema

from ..channels.service import ChannelService
from ..channels.repository import ChannelRepository
from ..channels.schemas import ChannelReadSchema
from ..channels.dependencies import get_channel_service

from .dependencies import get_course_service, get_course_structure_service
from .service import CourseService


from .schemas import (
    CourseCreateSchema, CourseUpdateSchema, CourseReadSchema


)

router = APIRouter(
    tags=["Courses"]
)



@router.get("/courses", response_model=List[CourseReadSchema])
async def get_all_courses(
    course_service: CourseService = Depends(get_course_service)
):
    return await course_service.get_all_public_courses()


@router.get("/courses/{course_id}", response_model=CourseReadSchema)
async def get_course_by_id(course_id : UUID): pass

@router.get("/users/{user_id}/channels/courses", response_model=List[CourseReadSchema])
async def get_user_courses(
    user_id: UUID,
    course_service: CourseService = Depends(get_course_service),
    channel_service: ChannelService = Depends(get_channel_service)
):
    return await course_service.get_courses_by_user(user_id, channel_service)



@router.post("/channels/{channel_id}/courses", response_model=CourseReadSchema, status_code=status.HTTP_201_CREATED)
async def create_course(
    channel_id: str,
    course_data: CourseCreateSchema,
    user_data: UserReadSchema = Depends(get_current_user),
    course_service: CourseService = Depends(get_course_service),
    channel_service: ChannelService = Depends(get_channel_service),
):
    channel_data = await channel_service.validate_owner(channel_id, user_data)
    return await course_service.create(course_data, channel_data, user_data)

@router.delete("/channels/{channel_id}/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(
    channel_id: str,
    course_id: UUID,
    user_data: UserReadSchema = Depends(get_current_user),
    course_service: CourseService = Depends(get_course_service),
    channel_service: ChannelService = Depends(get_channel_service),
):
    channel_data = await channel_service.validate_owner(channel_id, user_data)
    await course_service.delete_course(user_data, channel_data, course_id)

@router.patch("/channels/{channel_id}/courses/{course_id}", response_model=CourseReadSchema)
async def patch_course(
    channel_id: str,
    course_id: UUID,
    update_data: CourseUpdateSchema,
    user_data: UserReadSchema = Depends(get_current_user),
    course_service: CourseService = Depends(get_course_service),
    channel_service: ChannelService = Depends(get_channel_service),
):

    await channel_service.validate_owner(channel_id, user_data)
    return await course_service.update_course(course_id, update_data)

@router.get("/channels/{channel_id}/courses", response_model=List[CourseReadSchema])
async def get_channel_courses(
    channel_id: str,
    course_service: CourseService = Depends(get_course_service),
):
    return await course_service.get_courses_by_channel(channel_id)
