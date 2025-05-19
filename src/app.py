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

from .webhooks.router import router as minio_webhook_router
from .videos.router import router as video_router

from .settings.config import API_ENV, MODE_ENV

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

# Настройка корневого пути для документации и серверов в Swagger UI
root_path = "/api"
server_url = API_ENV.public_url if hasattr(API_ENV, 'public_url') else None

app = FastAPI(
    openapi_version="3.0.3",
    title="Video Hosting API",
    description="Video hosting service built with FastAPI",
    version="2.0.0",
    lifespan=lifespan,
    # Настраиваем пути для документации
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    # Добавляем root_path для корректной работы с префиксом /api
    root_path=root_path
)

# Устанавливаем серверы для Swagger UI
if server_url:
    app.servers = [
        {"url": server_url, "description": "Production Server"},
        {"url": "http://localhost/api", "description": "Local Server"}
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=".*",             # ← разрешаем все Origin-ы
    allow_credentials=True,              # куки / HTTP-auth разрешены
    allow_methods=["*"],
    allow_headers=["*"],
)

# Регистрируем роутеры
app.include_router(auth_router)
app.include_router(channel_router)
app.include_router(courses_router)
app.include_router(permissions_router)
app.include_router(courses_structure_router)
app.include_router(storage_router)

app.include_router(minio_webhook_router)
app.include_router(video_router)

@app.get('/')
async def root():
    """
    Корневой маршрут API
    """
    return {
        "message": "API работает",
        "version": app.version,
        "mode": MODE_ENV.MODE,
        "documentation": "/docs"
    }

@app.get('/protected-route')
async def protected_route(current_user: UserReadSchema = Depends(get_current_user)):
    return f"Hello {current_user.id}, {current_user.username}"