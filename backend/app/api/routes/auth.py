from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, status

from app.models.user import AuthResponse, AuthToken, UserCreate, UserLogin
from app.services.auth_service import auth_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(user_create: UserCreate):
    """
    Register a new user with email/mobile and password.
    
    - **email**: User's email address (optional if mobile provided)
    - **mobile**: User's mobile number (optional if email provided)
    - **name**: User's full name
    - **password**: User's password (min 6 characters)
    """
    try:
        user, token = auth_service.register(user_create)
        
        return AuthResponse(
            success=True,
            message="Registration successful",
            data=AuthToken(
                access_token=token,
                user=user,
            ),
        )
    except ValueError as e:
        logger.warning(f"Registration failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Registration error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed",
        )


@router.post("/login", response_model=AuthResponse)
async def login(user_login: UserLogin):
    """
    Login with email/mobile and password.
    
    - **email**: User's email address (optional if mobile provided)
    - **mobile**: User's mobile number (optional if email provided)
    - **password**: User's password
    """
    try:
        user, token = auth_service.login(user_login)
        
        return AuthResponse(
            success=True,
            message="Login successful",
            data=AuthToken(
                access_token=token,
                user=user,
            ),
        )
    except ValueError as e:
        logger.warning(f"Login failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Login error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed",
        )
