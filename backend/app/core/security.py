"""
Cosmic Watch - Security & JWT Authentication

Copyright © 2026 Rohit. Made with love by Rohit.
All rights reserved.

Repository: https://github.com/rohitb6/Cosmic_Watch
"""
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer scheme
security = HTTPBearer()


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    # Bcrypt has a 72-byte limit, truncate if needed
    truncated_password = password[:72]
    return pwd_context.hash(truncated_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    # Bcrypt has a 72-byte limit, truncate if needed
    truncated_password = plain_password[:72]
    return pwd_context.verify(truncated_password, hashed_password)


def create_tokens(user_id: str) -> dict:
    """Create both access and refresh tokens"""
    access_token = create_access_token(user_id)
    refresh_token = create_refresh_token(user_id)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


def create_access_token(user_id: str) -> str:
    """Create JWT access token"""
    expires = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    to_encode = {
        "sub": str(user_id),
        "type": "access",
        "exp": expires
    }
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm
    )
    return encoded_jwt


def create_refresh_token(user_id: str) -> str:
    """Create JWT refresh token"""
    expires = datetime.now(timezone.utc) + timedelta(
        days=settings.refresh_token_expire_days
    )
    to_encode = {
        "sub": str(user_id),
        "type": "refresh",
        "exp": expires
    }
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm
    )
    return encoded_jwt


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Dependency to extract and validate JWT from Bearer token
    Returns user_id
    """
    token = credentials.credentials
    
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if user_id is None or token_type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_id
