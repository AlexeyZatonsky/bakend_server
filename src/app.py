from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from uuid import UUID

from .auth.models import Users
from .auth.schemas import UserRead, UserCreate
from .auth.base_config import auth_backend, fastapi_users

from .channels.router import router as channel_router
from .videos.router import router as video_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown

app = FastAPI(
    title="Video Hosting API",
    description="Video hosting service built with FastAPI",
    version="2.0.0",
    lifespan=lifespan
)

current_user = fastapi_users.current_user()

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

@app.get('/protected-route')
async def protected_route(user: Users = Depends(current_user)):
    return f"Hello {user.id}, {user.username}"

app.include_router(channel_router)
app.include_router(video_router)