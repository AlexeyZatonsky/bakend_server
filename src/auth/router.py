from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from datetime import timedelta

from .schemas import UserCreateSchema, UserReadSchema, TokenSchema, UserUpdateSchema, UserReadPublicSchema
from .service import AuthService
from ..database import get_async_session
from .dependencies import get_current_user, get_auth_service


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post(
    "/register", 
    response_model=UserReadSchema, 
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация нового пользователя",
    description="Создает нового пользователя с указанным email и паролем."
)
async def register_user(
    user_data: UserCreateSchema,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Регистрация нового пользователя
    
    Args:
        user_data: Данные для создания пользователя (email и пароль)
        auth_service: Сервис аутентификации
        
    Returns:
        UserReadSchema: Данные созданного пользователя
        
    Raises:
        HTTPException: 409 Conflict, если пользователь с таким email уже существует
    """
    logger.info(f"Registering new user with email: {user_data.email}")
    return await auth_service.create_user(user_data)

@router.post(
    "/login", 
    response_model=TokenSchema,
    summary="Аутентификация пользователя",
    description="Проверяет учетные данные пользователя и возвращает токен доступа."
)
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Аутентификация пользователя и получение токена
    
    Args:
        response: Объект ответа FastAPI
        form_data: Форма с данными для входа (username = email, password)
        auth_service: Сервис аутентификации
        
    Returns:
        TokenSchema: Токен доступа и его тип
        
    Raises:
        HTTPException: 401 Unauthorized, если учетные данные неверны
    """
    logger.info(f"Login attempt for user: {form_data.username}")
    
    user = await auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        logger.warning(f"Failed login attempt for: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=auth_service.access_token_expire_minutes)
    access_token = auth_service.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    logger.info(f"Generated token for user: {user.username}")
    
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

@router.post(
    "/logout",
    summary="Выход пользователя",
    description="Удаляет cookie с токеном доступа."
)
async def logout(response: Response):
    """
    Выход пользователя
    
    Args:
        response: Объект ответа FastAPI
        
    Returns:
        dict: Сообщение об успешном выходе
    """
    logger.info("User logout")
    response.delete_cookie(key="access_token")
    return {"message": "Successfully logged out"}

@router.get(
    "/me", 
    response_model=UserReadSchema,
    summary="Информация о текущем пользователе",
    description="Возвращает информацию о текущем аутентифицированном пользователе."
)
async def read_users_me(
    current_user: UserReadSchema = Depends(get_current_user)
):
    """
    Получение информации о текущем пользователе
    
    Args:
        current_user: Текущий пользователь (получен из зависимости)
        
    Returns:
        UserReadSchema: Данные текущего пользователя
    """
    logger.info(f"Get user info for: {current_user.username}")
    return current_user

@router.put(
    "/me", 
    response_model=UserReadSchema,
    summary="Обновление данных пользователя",
    description="Обновляет данные текущего пользователя."
)
async def update_user_me(
    user_data: UserUpdateSchema,
    current_user: UserReadSchema = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Обновление данных текущего пользователя
    
    Args:
        user_data: Новые данные пользователя
        current_user: Текущий пользователь (получен из зависимости)
        auth_service: Сервис аутентификации
        
    Returns:
        UserReadSchema: Обновленные данные пользователя
    """
    logger.info(f"Update user data for: {current_user.username}")
    return await auth_service.update_user(current_user.id, user_data.model_dump(exclude_unset=True))


@router.delete(
    "/me", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удаление пользователя",
    description="Удаляет текущего пользователя."
)
async def delete_user_me(
    current_user: UserReadSchema = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Удаление текущего пользователя
    
    Args:
        current_user: Текущий пользователь (получен из зависимости)
        auth_service: Сервис аутентификации
    """
    logger.info(f"Delete user: {current_user.username}")
    await auth_service.delete_user(current_user.id)
    return None 


@router.get("/users", response_model=list[UserReadPublicSchema])
async def get_users( 
    auth_service: AuthService = Depends(get_auth_service), 
    limit:int = 20) :
    """Тетовы метод просто для получения всех пользователей"""
    return await auth_service.get_all_users(limit)