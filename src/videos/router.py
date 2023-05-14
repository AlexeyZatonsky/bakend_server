from fastapi import APIRouter, Depends, UploadFile

from.services import OperationsVideo

from .schemas import CategoryRead, CategoryCreate, \
TagRead, TagCreate, VidoeUpload, AboutVideo, BaseVideoTag




router = APIRouter(
    prefix='/Videos',
    tags=['videos']
)



@router.post('/category/create', response_model=CategoryCreate, status_code=201)
async def category_create(category_data: CategoryCreate, service: OperationsVideo=Depends()):
    pass

@router.post('/upload/', response_model=VidoeUpload, status_code=210)
async def video_upload(
    video_data: VidoeUpload, 
    video_file: UploadFile, 
    service: OperationsVideo = Depends()
):
    return service.video_upload(video_data, video_file)

