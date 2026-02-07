"""
Watchlist management service
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timezone
from typing import List
from uuid import UUID

from app.models.models import Watchlist, User, Asteroid
from app.schemas.schemas import (
    WatchlistAddRequest, WatchlistUpdateRequest, WatchlistItemResponse, WatchlistResponse
)
from app.services.asteroid_service import AsteroidService


class WatchlistService:
    """Handle user watchlists"""
    
    @staticmethod
    def add_to_watchlist(
        db: Session,
        user_id: str,
        request: WatchlistAddRequest
    ) -> WatchlistItemResponse:
        """Add asteroid to user watchlist"""
        try:
            user_uuid = UUID(user_id)
            asteroid_uuid = UUID(request.asteroid_id)
        except ValueError:
            raise ValueError("Invalid user or asteroid ID")
        
        # Check if user exists
        user = db.query(User).filter(User.id == user_uuid).first()
        if not user:
            raise ValueError("User not found")
        
        # Check if asteroid exists
        asteroid = db.query(Asteroid).filter(Asteroid.id == asteroid_uuid).first()
        if not asteroid:
            raise ValueError("Asteroid not found")
        
        # Check if already in watchlist
        existing = db.query(Watchlist).filter(
            and_(
                Watchlist.user_id == user_uuid,
                Watchlist.asteroid_id == asteroid_uuid
            )
        ).first()
        
        if existing:
            raise ValueError("Asteroid already in watchlist")
        
        # Create watchlist item
        watchlist_item = Watchlist(
            user_id=user_uuid,
            asteroid_id=asteroid_uuid,
            alert_threshold_distance_km=request.alert_threshold_distance_km,
            alert_threshold_cri=request.alert_threshold_cri
        )
        
        db.add(watchlist_item)
        db.commit()
        db.refresh(watchlist_item)
        
        asteroid_detail = AsteroidService.get_asteroid_detail(db, request.asteroid_id)
        
        return WatchlistItemResponse(
            id=str(watchlist_item.id),
            asteroid=asteroid_detail,
            alert_threshold_distance_km=watchlist_item.alert_threshold_distance_km,
            alert_threshold_cri=watchlist_item.alert_threshold_cri,
            custom_notes=watchlist_item.custom_notes,
            created_at=watchlist_item.created_at
        )
    
    @staticmethod
    def remove_from_watchlist(db: Session, user_id: str, asteroid_id: str) -> bool:
        """Remove asteroid from watchlist"""
        try:
            user_uuid = UUID(user_id)
            asteroid_uuid = UUID(asteroid_id)
        except ValueError:
            raise ValueError("Invalid user or asteroid ID")
        
        watchlist_item = db.query(Watchlist).filter(
            and_(
                Watchlist.user_id == user_uuid,
                Watchlist.asteroid_id == asteroid_uuid
            )
        ).first()
        
        if not watchlist_item:
            raise ValueError("Not in watchlist")
        
        db.delete(watchlist_item)
        db.commit()
        
        return True
    
    @staticmethod
    def get_user_watchlist(db: Session, user_id: str) -> WatchlistResponse:
        """Get all asteroids in user watchlist"""
        try:
            user_uuid = UUID(user_id)
        except ValueError:
            raise ValueError("Invalid user ID")
        
        items = db.query(Watchlist).filter(Watchlist.user_id == user_uuid).all()
        
        response_items = []
        for item in items:
            try:
                asteroid_detail = AsteroidService.get_asteroid_detail(db, str(item.asteroid_id))
                response_items.append(
                    WatchlistItemResponse(
                        id=str(item.id),
                        asteroid=asteroid_detail,
                        alert_threshold_distance_km=item.alert_threshold_distance_km,
                        alert_threshold_cri=item.alert_threshold_cri,
                        custom_notes=item.custom_notes,
                        created_at=item.created_at
                    )
                )
            except:
                # Skip asteroids with issues
                pass
        
        return WatchlistResponse(
            items=response_items,
            total_count=len(response_items)
        )
    
    @staticmethod
    def update_watchlist_item(
        db: Session,
        user_id: str,
        asteroid_id: str,
        request: WatchlistUpdateRequest
    ) -> WatchlistItemResponse:
        """Update watchlist item thresholds"""
        try:
            user_uuid = UUID(user_id)
            asteroid_uuid = UUID(asteroid_id)
        except ValueError:
            raise ValueError("Invalid user or asteroid ID")
        
        watchlist_item = db.query(Watchlist).filter(
            and_(
                Watchlist.user_id == user_uuid,
                Watchlist.asteroid_id == asteroid_uuid
            )
        ).first()
        
        if not watchlist_item:
            raise ValueError("Not in watchlist")
        
        if request.alert_threshold_distance_km is not None:
            watchlist_item.alert_threshold_distance_km = request.alert_threshold_distance_km
        
        if request.alert_threshold_cri is not None:
            watchlist_item.alert_threshold_cri = request.alert_threshold_cri
        
        if request.custom_notes is not None:
            watchlist_item.custom_notes = request.custom_notes
        
        watchlist_item.updated_at = datetime.now(timezone.utc)
        
        db.commit()
        db.refresh(watchlist_item)
        
        asteroid_detail = AsteroidService.get_asteroid_detail(db, asteroid_id)
        
        return WatchlistItemResponse(
            id=str(watchlist_item.id),
            asteroid=asteroid_detail,
            alert_threshold_distance_km=watchlist_item.alert_threshold_distance_km,
            alert_threshold_cri=watchlist_item.alert_threshold_cri,
            custom_notes=watchlist_item.custom_notes,
            created_at=watchlist_item.created_at
        )
    
    @staticmethod
    def is_in_watchlist(db: Session, user_id: str, asteroid_id: str) -> bool:
        """Check if asteroid is in user watchlist"""
        try:
            user_uuid = UUID(user_id)
            asteroid_uuid = UUID(asteroid_id)
        except ValueError:
            return False
        
        item = db.query(Watchlist).filter(
            and_(
                Watchlist.user_id == user_uuid,
                Watchlist.asteroid_id == asteroid_uuid
            )
        ).first()
        
        return item is not None
