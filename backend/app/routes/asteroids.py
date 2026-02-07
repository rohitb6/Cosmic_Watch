"""
Asteroid and NEO feed routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta, timezone

from app.core.database import get_db
from app.core.security import get_current_user
from app.services.asteroid_service import AsteroidService
from app.schemas.schemas import (
    AsteroidDetailResponse, AsteroidListResponse, SearchAsteroidsRequest,
    Next72hThreatsResponse
)
from app.models.models import Asteroid, CloseApproach

router = APIRouter(prefix="/neo", tags=["asteroids"])


@router.post("/sync-nasa")
async def sync_nasa_data(
    days_ahead: int = Query(7, ge=1, le=30),
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Sync real-time NASA asteroid feed to database
    days_ahead: How many days ahead to fetch (1-30)
    """
    try:
        start_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        end_date = (datetime.now(timezone.utc) + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
        
        result = await AsteroidService.sync_nasa_feed_to_db(db, start_date=start_date, end_date=end_date)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync NASA data: {str(e)}"
        )


@router.get("/feed", response_model=AsteroidListResponse)
def get_asteroid_feed(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    sort: str = Query("risk_desc", description="risk_desc, risk_asc, date_asc, date_desc"),
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get paginated asteroid feed with real NASA data
    Sorting by risk (CRI) or closest approach date
    """
    try:
        # Query asteroids from database (synced from NASA)
        query = db.query(Asteroid)
        
        # Apply sorting
        if sort == "risk_desc":
            # Join with CloseApproach and sort by CRI descending
            query = query.outerjoin(CloseApproach).order_by(CloseApproach.calculated_cri.desc())
        elif sort == "risk_asc":
            query = query.outerjoin(CloseApproach).order_by(CloseApproach.calculated_cri.asc())
        elif sort == "date_asc":
            query = query.outerjoin(CloseApproach).order_by(CloseApproach.closest_approach_date.asc())
        elif sort == "date_desc":
            query = query.outerjoin(CloseApproach).order_by(CloseApproach.closest_approach_date.desc())
        
        # Pagination
        total_count = db.query(Asteroid).count()
        
        asteroids = query.offset((page - 1) * limit).limit(limit).all()
        
        # Convert to response
        items = []
        for asteroid in asteroids:
            try:
                item = AsteroidService.get_asteroid_detail(db, str(asteroid.id))
                items.append(item)
            except:
                continue
        
        return AsteroidListResponse(
            items=items,
            total_count=total_count,
            page=page,
            page_size=limit,
            total_pages=(total_count + limit - 1) // limit
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch asteroid feed: {str(e)}"
        )


@router.get("/next-72h", response_model=Next72hThreatsResponse)
def get_next_72h_threats(
    threat_level: Optional[str] = Query(None, description="critical, high, medium, low"),
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get asteroids approaching in next 72 hours with high risk"""
    try:
        return AsteroidService.get_next_72h_threats(db)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{asteroid_id}", response_model=AsteroidDetailResponse)
def get_asteroid_detail(
    asteroid_id: str,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed info for single asteroid with CRI"""
    try:
        return AsteroidService.get_asteroid_detail(db, asteroid_id)
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


@router.get("/search", response_model=list[AsteroidDetailResponse])
def search_asteroids(
    q: str = Query(..., min_length=1, max_length=255, description="Search query"),
    limit: int = Query(10, ge=1, le=100),
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Search for asteroids by name"""
    try:
        return AsteroidService.search_asteroids(db, q, limit)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/sync/{neo_id}")
def sync_asteroid(
    neo_id: str,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Force sync specific asteroid from NASA API"""
    try:
        asteroid = AsteroidService.sync_asteroid_from_nasa(db, neo_id)
        return {
            "success": True,
            "asteroid_id": str(asteroid.id),
            "name": asteroid.name,
            "synced_at": asteroid.nasa_synced_at
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/today")
def get_todays_asteroids(
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get asteroids approaching today"""
    try:
        from datetime import datetime, timezone, timedelta
        from sqlalchemy import and_
        from app.models.models import CloseApproach
        
        today = datetime.now(timezone.utc).date()
        tomorrow = today + timedelta(days=1)
        
        approaches = db.query(CloseApproach).filter(
            and_(
                CloseApproach.closest_approach_date >= datetime.combine(today, __import__('datetime').time.min),
                CloseApproach.closest_approach_date < datetime.combine(tomorrow, __import__('datetime').time.min)
            )
        ).order_by(CloseApproach.calculated_cri.desc()).all()
        
        asteroids = []
        for approach in approaches:
            try:
                detail = AsteroidService.get_asteroid_detail(db, str(approach.asteroid_id))
                asteroids.append(detail)
            except:
                pass
        
        return {
            "count": len(asteroids),
            "asteroids": asteroids
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
