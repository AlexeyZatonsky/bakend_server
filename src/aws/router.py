from uuid import UUID


from fastapi import APIRouter, Depends,status

from ..auth.schemas import UserReadSchema
from ..auth.dependencies import get_current_user

from .schemas import UserAvatarUploadRequestSchema, UserAvatarUploadResponseSchema
from .service  import StorageService
from .dependencies import get_storage_service
from .strategies import ObjectKind




router = APIRouter(
    prefix="/upload",
    tags=["Storage"]
)



@router.post(
    "/avatar",
    response_model=UserAvatarUploadResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Получение ссылки для загрузки аватара пользователя"
)
async def get_user_profile_preview_url(
    payload: UserAvatarUploadRequestSchema,
    user_data: UserReadSchema = Depends(get_current_user),
    storage_service: StorageService = Depends(get_storage_service) 
):
    presign = await storage_service.generate_upload_urls(
        owner_id=user_data.id,
        object_kind=ObjectKind.PROFILE_AVATAR,
        content_type=payload.content_type,
        source_filename=payload.file_name,
    )

    return UserAvatarUploadResponseSchema(upload_url=presign["upload_url"], key=presign["key"])