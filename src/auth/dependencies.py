from fastapi import Depends, HTTPException, status, Request, Cookie
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from typing import Optional

from .service import AuthService
from .schemas import UserReadSchema
from ..database import get_async_session

# Настраиваем логирование
logger = logging.getLogger(__name__)

# Создаем схему OAuth2 для работы с токенами
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login",
    scheme_name="JWT",
    auto_error=False  # Установить False, чтобы не вызывать ошибку автоматически
)


async def get_auth_service(session: AsyncSession = Depends(get_async_session)) -> AuthService:
    """Получение сервиса аутентификации"""
    return AuthService(session)


async def get_token_from_cookie(
    request: Request,
    access_token: Optional[str] = Cookie(None)
) -> Optional[str]:
    """Получение токена из cookie"""
    if access_token:
        logger.info("Token found in cookie")
        # Удаляем префикс Bearer, если он есть
        if access_token.startswith("Bearer "):
            return access_token[7:]
        return access_token
    
    # Пытаемся получить токен из заголовка (для обратной совместимости)
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        logger.info("Token found in Authorization header")
        return auth_header[7:]
    
    return None


async def get_current_user(
    request: Request,
    token: Optional[str] = Depends(get_token_from_cookie),
    auth_service: AuthService = Depends(get_auth_service)
) -> UserReadSchema:
    """Получение текущего пользователя"""
    logger.info("=== Executing get_current_user dependency ===")
    
    # Логируем все заголовки для отладки
    logger.info("Request headers:")
    for header, value in request.headers.items():
        logger.info(f"{header}: {value}")
        
    # Выводим данные запроса
    logger.info(f"Request method: {request.method}")
    logger.info(f"Request URL: {request.url}")
    logger.info(f"Request cookies: {request.cookies}")
        
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not token:
        logger.error("No token found in cookie or header")
        raise credentials_exception
    
    try:
        logger.info("Attempting to validate token and get current user")
        logger.info(f"Token from cookie/header: {token[:10]}...")
        user = await auth_service.get_current_user(token)
        logger.info(f"Successfully retrieved user: {user.username}")
        return user
    except Exception as e:
        logger.error(f"Error validating token: {str(e)}")
        raise credentials_exception
