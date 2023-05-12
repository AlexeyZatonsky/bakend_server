from fastapi import APIRouter, Depends

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