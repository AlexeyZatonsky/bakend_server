from fastapi import Depends, HTTPException, status, Request
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Users
from .router import oauth2_scheme
from ..database import get_async_session
from ..settings.config import SECRET_AUTH

async def get_current_user(
    request: Request,
    session: AsyncSession = Depends(get_async_session)
) -> Users:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials"
    )

    # Получаем токен из cookie
    token = request.cookies.get("access_token")
    
    # Для обратной совместимости проверяем и заголовок Authorization
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
    
    if not token:
        raise credentials_exception

    try:
        payload = jwt.decode(token, SECRET_AUTH, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await session.execute(select(Users).where(Users.id == user_id))
    user = user.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    return user 