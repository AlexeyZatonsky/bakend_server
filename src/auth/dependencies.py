from fastapi import Depends, HTTPException, status, Request, Cookie
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

import logging

from ..core.log import configure_logging

from .exceptions import AuthHTTPExceptions
from .service import AuthService
from .schemas import UserReadSchema
from ..database import get_async_session


logger = logging.getLogger(__name__)
configure_logging()



async def get_auth_service(session: AsyncSession = Depends(get_async_session)) -> AuthService:
    """
    Зависимость для получения сервиса аутентификации
    
    Args:
        session: Асинхронная сессия SQLAlchemy
        
    Returns:
        AuthService: Экземпляр сервиса аутентификации
    """
    http_exceptions = AuthHTTPExceptions()
    

    return AuthService(session, http_exceptions)

async def get_token_from_cookie(
    request: Request,
    access_token: Optional[str] = Cookie(None)
) -> Optional[str]:
    """
    Извлекает токен доступа из cookie или заголовка Authorization
    
    Args:
        request: Запрос FastAPI
        access_token: Токен доступа из cookie
        
    Returns:
        Optional[str]: Токен доступа или None, если токен не найден
    """
    logger.debug("Extracting token from cookies or headers")
    
    # Сначала проверяем cookie
    if access_token:
        logger.debug("Token found in cookie")
        # Удаляем префикс Bearer, если он есть
        return access_token.replace("Bearer ", "")
    
    # Если токена нет в cookie, ищем в заголовке
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        logger.debug("Token found in Authorization header")
        return auth_header[7:]
    
    logger.debug("No token found in cookies or headers")
    return None

async def get_current_user(
    request: Request,
    token: Optional[str] = Depends(get_token_from_cookie),
    auth_service: AuthService = Depends(get_auth_service)
) -> UserReadSchema:
    """
    Зависимость для получения текущего пользователя
    
    Args:
        request: Запрос FastAPI
        token: Токен доступа
        auth_service: Сервис аутентификации
        
    Returns:
        UserReadSchema: Данные текущего пользователя
        
    Raises:
        HTTPException: 401 Unauthorized, если токен недействителен или отсутствует
    """
    logger.debug(f"Getting current user from token: {token is not None}")
    
    if not token:
        logger.warning("No token provided for authentication")
        raise auth_service.http_exceptions.unauthorized_401()
    
    try:
        user = await auth_service.get_current_user(token)
        logger.debug(f"User authenticated: {user.username}")
        return user
    except Exception as e:
        logger.warning(f"Authentication failed: {str(e)}")
        raise auth_service.http_exceptions.unauthorized_401("Invalid authentication credentials")

