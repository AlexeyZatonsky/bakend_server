from contextlib import asynccontextmanager
from .auth.dependencies import get_current_user
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware


from .auth.schemas import UserReadSchema

from .auth.router import router as auth_router
from .channels.router import router as channel_router
from .courses.router import router as courses_router
from .permissions.router import router as permissions_router
from .courses_structure.router import router as courses_structure_router
from .aws.router import router as storage_router
# from .videos.router import router as video_router


# TODO: Auth
# Добавить CSRF-защиту
# Реализовать механизм блокировки после нескольких неудачных попыток
# Добавить систему refresh-токенов
# Настроить более безопасное логирование
# Включить HTTPS в продакшне и установить secure=True для cookies



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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
)

# Регистрируем роутеры
app.include_router(auth_router)
app.include_router(channel_router)
app.include_router(courses_router)
app.include_router(permissions_router)
app.include_router(courses_structure_router)
app.include_router(storage_router)
# app.include_router(video_router)

@app.get('/protected-route')
async def protected_route(current_user: UserReadSchema = Depends(get_current_user)):
    return f"Hello {current_user.id}, {current_user.username}"