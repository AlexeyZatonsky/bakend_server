from uuid import UUID
from fastapi import FastAPI, Depends

from .auth.models import User


from .auth.schemas import UserRead, UserCreate
from .auth.base_config import auth_backend, fastapi_users

from .channels.router import router as channel_router
from .videos.router import router as video_roter


app = FastAPI(
    title = "vidoses"
)


app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth",
    tags=["Auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["Auth"],
)


app.include_router(channel_router)
app.include_router(video_roter)