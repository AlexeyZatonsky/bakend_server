from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware



from .auth.router import router as auth_router
from .channels.router import router as channel_router
from .courses.router import router as courses_router
from .permissions.router import router as permissions_router
from .courses_structure.router import router as courses_structure_router
from .aws.router import router as storage_router

from .webhooks.router import router as minio_webhook_router
from .videos.router import router as video_router

from .settings.config import API_ENV, MODE_ENV



@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown

root_path = "/api"
server_url = API_ENV.public_url

app = FastAPI(
    openapi_version="3.0.3",
    title="Video Hosting API",
    description="Video hosting service built with FastAPI",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
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
    allow_origin_regex=".*",            
    allow_credentials=True,              
    allow_methods=["*"],
    allow_headers=["*"],
)


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