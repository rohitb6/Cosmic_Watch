"""
Authentication routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user, create_access_token
from app.services.auth_service import AuthService
from app.schemas.schemas import (
    UserRegisterRequest, UserLoginRequest, TokenResponse, UserProfileResponse,
    RefreshTokenRequest
)

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=TokenResponse)
def register(user_data: UserRegisterRequest, db: Session = Depends(get_db)):
    """Register a new user"""
    try:
        result = AuthService.register_user(db, user_data)
        return TokenResponse(
            access_token=result["access_token"],
            refresh_token=result["refresh_token"]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=TokenResponse)
def login(login_data: UserLoginRequest, db: Session = Depends(get_db)):
    """Login user and get tokens"""
    try:
        result = AuthService.login_user(db, login_data)
        return TokenResponse(
            access_token=result["access_token"],
            refresh_token=result["refresh_token"]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    """
    Refresh access token using refresh token
    Note: In production, validate refresh token and extract user_id from it
    """
    try:
        from jose import jwt
        from app.core.config import settings
        
        payload = jwt.decode(
            request.refresh_token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        user_id = payload.get("sub")
        new_access_token = create_access_token(user_id)
        
        return TokenResponse(
            access_token=new_access_token,
            refresh_token=request.refresh_token
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )


@router.get("/me", response_model=UserProfileResponse)
def get_current_user_profile(
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user profile"""
    try:
        user = AuthService.get_user_by_id(db, user_id)
        return UserProfileResponse(
            id=str(user.id),
            email=user.email,
            username=user.username,
            preferences=user.preferences,
            created_at=user.created_at,
            is_active=user.is_active
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/logout")
def logout(user_id: str = Depends(get_current_user)):
    """Logout user (client-side token invalidation)"""
    return {"message": "Logged out successfully. Please discard token client-side."}
