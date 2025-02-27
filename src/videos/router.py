from fastapi import APIRouter, Depends, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from .services import BaseVideoServices
from ..database import get_async_session
from ..auth.dependencies import get_current_user
from ..auth.models import Users

from .schemas import CategoryRead, CategoryCreate, \
TagRead, TagCreate, VidoeUpload, AboutVideo, BaseVideoTag



router = APIRouter(
    prefix='/Videos',
    tags=['videos']
)

@router.post('/category/create', response_model=CategoryRead, status_code=201)
async def category_create(
    category_data: CategoryCreate, 
    session: AsyncSession = Depends(get_async_session)
):
    service = BaseVideoServices(session)
    return await service.category_create(category_data)
    

   

@router.post('/upload/', response_model=AboutVideo, status_code=210)
async def video_upload(
    title: str,
    description: str,
    category_id: str, 
    video_file: UploadFile,
    session: AsyncSession = Depends(get_async_session),
    current_user: Users = Depends(get_current_user)
):
    service = BaseVideoServices(session)
    return await service.video_upload(title, description, category_id, video_file)

@router.delete('/delete', response_model=None, status_code=200)
async def video_delete(
    title: str, 
    session: AsyncSession = Depends(get_async_session)
):
    service = BaseVideoServices(session)
    return await service.video_remove(title)


@router.get('/category/read', response_model=list[CategoryRead], status_code=200)
async def category_read(
    session: AsyncSession = Depends(get_async_session)
):
    service = BaseVideoServices(session)
    return await service.category_read()