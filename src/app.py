from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from uuid import UUID

from .auth.models import Users
from .auth.schemas import UserRead, UserCreate
from .auth.router import router as auth_router
from .auth.dependencies import get_current_user

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

# Регистрируем роутеры
app.include_router(auth_router)
app.include_router(channel_router)
app.include_router(video_router)

@app.get('/protected-route')
async def protected_route(current_user: Users = Depends(get_current_user)):
    return f"Hello {current_user.id}, {current_user.username}"