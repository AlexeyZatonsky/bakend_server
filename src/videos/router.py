from fastapi import APIRouter, Depends, UploadFile

from.services import OperationsVideo

from .schemas import CategoryRead, CategoryCreate, \
TagRead, TagCreate, VidoeUpload, AboutVideo, BaseVideoTag




router = APIRouter(
    prefix='/Videos',
    tags=['videos']
)



@router.post('/category/create', response_model=CategoryRead, status_code=201)
async def category_create(
    category_data: CategoryCreate, 
    service: OperationsVideo=Depends()
                          ):
    return service.category_create(category_data)
    

   

@router.post('/upload/', response_model=AboutVideo, status_code=210)
async def video_upload(
    title: str,
    description: str,
    category_id: str, 
    video_file: UploadFile, 
    service: OperationsVideo = Depends()
):
    return await service.video_upload(title, description, category_id, video_file)

