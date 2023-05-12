from uuid import UUID
from fastapi import FastAPI, Depends
from .auth.manager import get_user_manager

from .auth.models import User


from .auth.schemas import UserRead, UserCreate
from .auth.base_config import auth_backend, fastapi_users
from .channels.router import router as channel_router




app = FastAPI(
    title = "vidoses"
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

@app.get('/protected-rout')
async def protected_rout(user: User = Depends(User)):
    return f'hellod{user.id}, {user.username}'

app.include_router(channel_router)