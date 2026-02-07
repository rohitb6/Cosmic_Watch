"""
Alert routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.services.alert_service import AlertService
from app.schemas.schemas import (
    AlertListResponse, AlertStatsResponse
)

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=AlertListResponse)
def get_alerts(
    unread_only: bool = Query(False),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user alerts"""
    try:
        return AlertService.get_user_alerts(db, user_id, unread_only, limit, offset)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch("/{alert_id}/read")
def mark_alert_read(
    alert_id: str,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark alert as read"""
    try:
        AllertService.mark_alert_read(db, user_id, alert_id)
        return {"success": True, "message": "Alert marked as read"}
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


@router.delete("/{alert_id}")
def delete_alert(
    alert_id: str,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete alert"""
    try:
        AlertService.delete_alert(db, user_id, alert_id)
        return {"success": True, "message": "Alert deleted"}
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


@router.get("/stats", response_model=AlertStatsResponse)
def get_alert_stats(
    days: int = Query(7, ge=1, le=90),
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get alert statistics"""
    try:
        return AlertService.get_alert_stats(db, user_id, days)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/check-thresholds")
def check_watchlist_thresholds(
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check watchlist items and trigger alerts if needed"""
    try:
        count = AlertService.check_watchlist_thresholds(db, user_id)
        return {
            "success": True,
            "alerts_triggered": count,
            "message": f"Triggered {count} new alerts based on watchlist thresholds"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
