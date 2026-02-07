"""
Authentication service
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from uuid import UUID

from app.models.models import User
from app.core.security import hash_password, verify_password, create_tokens
from app.schemas.schemas import UserRegisterRequest, UserLoginRequest


class AuthService:
    """Handle user authentication"""
    
    @staticmethod
    def register_user(db: Session, user_data: UserRegisterRequest) -> dict:
        """Register a new user"""
        # Check if email already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Check if username already exists
        existing_username = db.query(User).filter(User.username == user_data.username).first()
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        # Create new user
        new_user = User(
            email=user_data.email,
            username=user_data.username,
            password_hash=hash_password(user_data.password),
            is_active=True
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Generate tokens
        tokens = create_tokens(str(new_user.id))
        
        return {
            "user_id": str(new_user.id),
            "email": new_user.email,
            "username": new_user.username,
            **tokens
        }
    
    @staticmethod
    def login_user(db: Session, login_data: UserLoginRequest) -> dict:
        """Authenticate user and return tokens"""
        user = db.query(User).filter(User.email == login_data.email).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        if not verify_password(login_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive"
            )
        
        # Generate tokens
        tokens = create_tokens(str(user.id))
        
        return {
            "user_id": str(user.id),
            "email": user.email,
            "username": user.username,
            **tokens
        }
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: str) -> User:
        """Get user by ID"""
        try:
            uuid = UUID(user_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user ID"
            )
        
        user = db.query(User).filter(User.id == uuid).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return user
    
    @staticmethod
    def update_user_preferences(db: Session, user_id: str, preferences: dict) -> User:
        """Update user preferences"""
        user = AuthService.get_user_by_id(db, user_id)
        
        # Merge with existing preferences
        user.preferences = {**user.preferences, **preferences}
        
        db.commit()
        db.refresh(user)
        return user
