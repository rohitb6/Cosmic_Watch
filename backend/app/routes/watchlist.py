"""
Watchlist routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.services.watchlist_service import WatchlistService
from app.schemas.schemas import (
    WatchlistAddRequest, WatchlistUpdateRequest, WatchlistItemResponse, WatchlistResponse
)

router = APIRouter(prefix="/watchlist", tags=["watchlist"])


@router.get("", response_model=WatchlistResponse)
def get_watchlist(
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's watchlist"""
    try:
        return WatchlistService.get_user_watchlist(db, user_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("", response_model=WatchlistItemResponse)
def add_to_watchlist(
    request: WatchlistAddRequest,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add asteroid to watchlist"""
    try:
        return WatchlistService.add_to_watchlist(db, user_id, request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{asteroid_id}")
def remove_from_watchlist(
    asteroid_id: str,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove asteroid from watchlist"""
    try:
        WatchlistService.remove_from_watchlist(db, user_id, asteroid_id)
        return {"success": True, "message": "Removed from watchlist"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{asteroid_id}", response_model=WatchlistItemResponse)
def update_watchlist_item(
    asteroid_id: str,
    request: WatchlistUpdateRequest,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update watchlist item alert thresholds"""
    try:
        return WatchlistService.update_watchlist_item(db, user_id, asteroid_id, request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{asteroid_id}/status")
def check_in_watchlist(
    asteroid_id: str,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check if asteroid is in user's watchlist"""
    try:
        is_in = WatchlistService.is_in_watchlist(db, user_id, asteroid_id)
        return {"in_watchlist": is_in}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
