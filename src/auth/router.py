from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from .schemas import UserLogin, UserCreate, UserRead
from .service import AuthService
from ..database import get_async_session

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_auth_service(session: AsyncSession = Depends(get_async_session)):
    return AuthService(session)

@router.post("/register", response_model=UserRead)
async def register(
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service)
):
    logger.info(f"Received registration request for email: {user_data.email}")
    return await auth_service.register_new_user(user_data)

@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
    response: Response = None
):
    logger.info(f"Received login request for username: {form_data.username}")
    user = await auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    access_token = auth_service.create_access_token(data={"sub": str(user.id)})
    
    # Устанавливаем cookie с токеном
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=1800,
        samesite="lax",
        secure=False
    )
    
    return {"access_token": access_token}

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(
        key="access_token",
        httponly=True,
        samesite="lax",
        secure=False  # В продакшене с HTTPS установите True
    )
    return {"detail": "Successfully logged out"} 