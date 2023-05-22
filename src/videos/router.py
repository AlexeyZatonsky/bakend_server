from fastapi import APIRouter, Depends, UploadFile

from.services import BaseVideoServices

from .schemas import CategoryRead, CategoryCreate, \
TagRead, TagCreate, VidoeUpload, AboutVideo, BaseVideoTag



router = APIRouter(
    prefix='/Videos',
    tags=['videos']
)



@router.post('/category/create', response_model=CategoryRead, status_code=201)
async def category_create(
    category_data: CategoryCreate, 
    service: BaseVideoServices=Depends()
                          ):
    return await service.category_create(category_data)
    

   

@router.post('/upload/', response_model=AboutVideo, status_code=210)
async def video_upload(
    title: str,
    description: str,
    category_id: str, 
    video_file: UploadFile, 
    service: BaseVideoServices = Depends()
):
    return await service.video_upload(title, description, category_id, video_file)

@router.delete('/delete', response_model=None, status_code=200)
async def video_delete(title: str, service: BaseVideoServices = Depends()):
    return await service.video_remove(title)


@router.get('/category/read', response_model=list[CategoryRead], status_code=200)
async def category_read(service: BaseVideoServices = Depends()):
    return await service.category_read()