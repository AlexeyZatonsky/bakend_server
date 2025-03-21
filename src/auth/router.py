from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from datetime import timedelta

from .schemas import UserCreateSchema, UserReadSchema, TokenSchema, UserUpdateSchema
from .service import AuthService
from ..database import get_async_session
from .dependencies import get_current_user, get_auth_service


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Auth"])

async def get_auth_service(session: AsyncSession = Depends(get_async_session)):
    return AuthService(session)

@router.post("/register", response_model=UserReadSchema, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreateSchema,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Регистрация нового пользователя"""
    return await auth_service.create_user(user_data)

@router.post("/login", response_model=TokenSchema)
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Аутентификация пользователя и получение токена"""
    user = await auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=auth_service.access_token_expire_minutes)
    access_token = auth_service.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    logger.info(f"Generated token for user {user.username}")
    
    # Устанавливаем cookie
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=auth_service.access_token_expire_minutes * 60,
        expires=auth_service.access_token_expire_minutes * 60,
        samesite="lax",
        secure=False  # В продакшн установить True
    )
    logger.info("Cookie set successfully")
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout")
async def logout(response: Response):
    """Выход пользователя"""
    response.delete_cookie(key="access_token")
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=UserReadSchema)
async def read_users_me(
    request: Request,
    current_user: UserReadSchema = Depends(get_current_user)
):
    """Получение информации о текущем пользователе"""
    # Логируем все заголовки для отладки
    logger.info("Request headers:")
    for header, value in request.headers.items():
        logger.info(f"{header}: {value}")
    
    logger.info(f"Cookies: {request.cookies}")
    logger.info(f"Current user: {current_user.username}")
    return current_user

@router.put("/me", response_model=UserReadSchema)
async def update_user_me(
    user_data: UserUpdateSchema,
    current_user: UserReadSchema = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Обновление информации о текущем пользователе"""
    auth_service = AuthService(session)
    return await auth_service.update_user(str(current_user.id), user_data.model_dump(exclude_unset=True))

@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_me(
    current_user: UserReadSchema = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Удаление текущего пользователя"""
    auth_service = AuthService(session)
    await auth_service.delete_user(str(current_user.id))
    return None 