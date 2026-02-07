"""
Cosmic Watch - Asteroid & NEO Feed Service

Copyright © 2026 Rohit. Made with love by Rohit.
All rights reserved.

NASA NeoWs API integration for real-time asteroid data.
Repository: https://github.com/rohitb6/Cosmic_Watch
"""
import httpx
import asyncio
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import Optional, List, Tuple
from uuid import UUID

from app.models.models import Asteroid, CloseApproach, NASAAPICache, RiskScoringLog
from app.core.config import settings
from app.utils.risk_calculator import calculate_cri, get_risk_level, is_next_72h_threat, calculate_days_until_approach
from app.schemas.schemas import (
    AsteroidDetailResponse, CloseApproachResponse, CRIComponentsResponse,
    RiskLevelInfo, Next72hThreatsResponse
)


class AsteroidService:
    """Handle asteroid data and NASA API integration"""
    
    @staticmethod
    async def fetch_nasa_asteroids(db: Session, limit: int = 20, page: int = 1, start_date: Optional[str] = None, end_date: Optional[str] = None) -> dict:
        """
        Fetch asteroids from NASA NeoWs API feed
        Implements caching to respect rate limits
        start_date and end_date format: YYYY-MM-DD
        """
        # Default to today's date if not provided
        if not start_date:
            start_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        if not end_date:
            end_date = (datetime.now(timezone.utc) + timedelta(days=7)).strftime("%Y-%m-%d")
        
        async with httpx.AsyncClient() as client:
            params = {
                "api_key": settings.nasa_api_key,
                "start_date": start_date,
                "end_date": end_date,
            }
            
            try:
                # Call NASA feed endpoint (this returns asteroids for a date range)
                response = await client.get(
                    f"{settings.nasa_base_url}/feed",
                    params=params,
                    timeout=15.0
                )
                response.raise_for_status()
                data = response.json()
                
                # Cache the response
                cache_entry = NASAAPICache(
                    endpoint="/neo/feed",
                    query_params=params,
                    response_data=data,
                    expires_at=datetime.now(timezone.utc) + timedelta(hours=settings.nasa_cache_ttl_hours)
                )
                db.add(cache_entry)
                db.commit()
                
                return data
                
            except httpx.HTTPError as e:
                # Try to return cached data
                cached = db.query(NASAAPICache).filter(
                    and_(
                        NASAAPICache.endpoint == "/neo/feed",
                        NASAAPICache.expires_at > datetime.now(timezone.utc)
                    )
                ).order_by(NASAAPICache.cached_at.desc()).first()
                
                if cached:
                    return cached.response_data
                
                raise ValueError(f"Failed to fetch NASA data: {str(e)}")
    
    @staticmethod
    async def sync_nasa_feed_to_db(db: Session, start_date: Optional[str] = None, end_date: Optional[str] = None) -> dict:
        """
        Fetch real NASA asteroid feed and sync to database
        Returns stats about the sync
        """
        try:
            nasa_data = await AsteroidService.fetch_nasa_asteroids(db, start_date=start_date, end_date=end_date)
            
            if not nasa_data or "near_earth_objects" not in nasa_data:
                return {"status": "error", "message": "Invalid NASA API response"}
            
            synced_count = 0
            approach_synced = 0
            
            # Iterate through each date's asteroids
            for date_str, asteroids_list in nasa_data["near_earth_objects"].items():
                for nasa_asteroid in asteroids_list:
                    neo_id = nasa_asteroid.get("neo_reference_id")
                    if not neo_id:
                        continue
                    
                    # Check if asteroid exists
                    asteroid = db.query(Asteroid).filter(Asteroid.neo_id == neo_id).first()
                    
                    if not asteroid:
                        asteroid = Asteroid(neo_id=neo_id)
                        synced_count += 1
                    
                    # Update asteroid data from NASA
                    asteroid.name = nasa_asteroid.get("name", "")
                    asteroid.url = nasa_asteroid.get("nasa_jpl_url", "")
                    asteroid.is_hazardous = nasa_asteroid.get("is_potentially_hazardous_asteroid", False)
                    asteroid.is_sentry_object = nasa_asteroid.get("is_sentry_object", False)
                    
                    # Convert magnitude to float
                    try:
                        asteroid.absolute_magnitude = float(nasa_asteroid.get("absolute_magnitude_h") or 0) or None
                    except (ValueError, TypeError):
                        asteroid.absolute_magnitude = None
                    
                    # Extract diameter
                    diameter_data = nasa_asteroid.get("estimated_diameter", {}).get("kilometers", {})
                    diameter_min = diameter_data.get("estimated_diameter_min")
                    diameter_max = diameter_data.get("estimated_diameter_max")
                    
                    # Convert to float if available
                    try:
                        diameter_min = float(diameter_min) if diameter_min else None
                        diameter_max = float(diameter_max) if diameter_max else None
                    except (ValueError, TypeError):
                        diameter_min = None
                        diameter_max = None
                    
                    asteroid.diameter_min_km = diameter_min
                    asteroid.diameter_max_km = diameter_max
                    if diameter_min and diameter_max:
                        asteroid.diameter_km = (diameter_min + diameter_max) / 2
                    
                    asteroid.nasa_synced_at = datetime.now(timezone.utc)
                    db.add(asteroid)
                    db.flush()
                    
                    # Sync close approaches
                    for approach_data in nasa_asteroid.get("close_approach_data", []):
                        AsteroidService._sync_close_approach(db, asteroid.id, approach_data)
                        approach_synced += 1
            
            db.commit()
            
            return {
                "status": "success",
                "synced_asteroids": synced_count,
                "synced_approaches": approach_synced,
                "total_asteroids": sum(len(v) for v in nasa_data["near_earth_objects"].values()),
                "message": f"Synced {synced_count} asteroids and {approach_synced} approaches from NASA"
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def sync_asteroid_from_nasa(db: Session, neo_id: str) -> Asteroid:
        """
        Fetch and sync specific asteroid from NASA API
        """
        async def _fetch():
            async with httpx.AsyncClient() as client:
                params = {"api_key": settings.nasa_api_key}
                response = await client.get(
                    f"{settings.nasa_base_url}/neo/{neo_id}",
                    params=params,
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json()
        
        # Run async function
        data = asyncio.run(_fetch())
        
        # Check if asteroid already exists
        asteroid = db.query(Asteroid).filter(Asteroid.neo_id == neo_id).first()
        
        if not asteroid:
            asteroid = Asteroid(neo_id=neo_id)
        
        # Update asteroid data
        asteroid.name = data.get("name", "")
        asteroid.url = data.get("nasa_jpl_url", "")
        asteroid.is_hazardous = data.get("is_potentially_hazardous_asteroid", False)
        asteroid.is_sentry_object = data.get("is_sentry_object", False)
        asteroid.absolute_magnitude = data.get("absolute_magnitude_h")
        
        # Extract diameter
        diameter_data = data.get("estimated_diameter", {}).get("kilometers", {})
        asteroid.diameter_min_km = diameter_data.get("estimated_diameter_min")
        asteroid.diameter_max_km = diameter_data.get("estimated_diameter_max")
        asteroid.diameter_km = (
            (asteroid.diameter_min_km + asteroid.diameter_max_km) / 2
            if asteroid.diameter_min_km and asteroid.diameter_max_km
            else None
        )
        
        asteroid.nasa_synced_at = datetime.now(timezone.utc)
        
        db.add(asteroid)
        
        # Sync close approaches
        for approach_data in data.get("close_approach_data", []):
            AsteroidService._sync_close_approach(db, asteroid.id, approach_data)
        
        db.commit()
        db.refresh(asteroid)
        
        return asteroid
    
    @staticmethod
    def _sync_close_approach(db: Session, asteroid_id: UUID, approach_data: dict) -> CloseApproach:
        """Sync a single close approach record"""
        approach_date = approach_data.get("close_approach_date_full", "")
        
        # Check if already exists
        existing = db.query(CloseApproach).filter(
            and_(
                CloseApproach.asteroid_id == asteroid_id,
                CloseApproach.close_approach_date_full == approach_date
            )
        ).first()
        
        if existing:
            approach = existing
        else:
            approach = CloseApproach(asteroid_id=asteroid_id)
        
        # Parse date
        try:
            approach.closest_approach_date = datetime.fromisoformat(
                approach_date.replace('Z', '+00:00')
            )
        except:
            approach.closest_approach_date = datetime.now(timezone.utc)
        
        approach.close_approach_date_full = approach_date
        
        # Distance and velocity data - convert strings to floats
        relative_velocity = approach_data.get("relative_velocity", {})
        try:
            approach.approach_velocity_kmh = float(relative_velocity.get("kilometers_per_hour", 0) or 0) or None
            approach.approach_velocity_kms = float(relative_velocity.get("kilometers_per_second", 0) or 0) or None
        except (ValueError, TypeError):
            approach.approach_velocity_kmh = None
            approach.approach_velocity_kms = None
        
        miss_distance = approach_data.get("miss_distance", {})
        try:
            approach.miss_distance_km = float(miss_distance.get("kilometers", 0) or 0) or None
            approach.miss_distance_au = float(miss_distance.get("astronomical", 0) or 0) or None
            approach.miss_distance_lunar = float(miss_distance.get("lunar", 0) or 0) or None
        except (ValueError, TypeError):
            approach.miss_distance_km = None
            approach.miss_distance_au = None
            approach.miss_distance_lunar = None
        
        approach.orbiting_body = approach_data.get("orbiting_body", "Earth")
        approach.nasa_synced_at = datetime.now(timezone.utc)
        
        # Calculate CRI immediately
        diameter_km = db.query(Asteroid.diameter_km).filter(Asteroid.id == asteroid_id).scalar()
        is_hazardous = db.query(Asteroid.is_hazardous).filter(Asteroid.id == asteroid_id).scalar()
        
        cri_score, components = calculate_cri(
            diameter_km=diameter_km,
            velocity_kmh=approach.approach_velocity_kmh,
            miss_distance_km=approach.miss_distance_km,
            is_hazardous=is_hazardous or False
        )
        
        approach.calculated_cri = cri_score
        
        db.add(approach)
        
        # Log the risk calculation
        risk_log = RiskScoringLog(
            asteroid_id=asteroid_id,
            close_approach_id=approach.id,
            cri_score=cri_score,
            component_scores=components.__dict__,
            calculation_inputs={
                "diameter_km": diameter_km,
                "velocity_kmh": approach.approach_velocity_kmh,
                "miss_distance_km": approach.miss_distance_km,
                "is_hazardous": is_hazardous
            }
        )
        db.add(risk_log)
        
        return approach
    
    @staticmethod
    def get_asteroid_detail(db: Session, asteroid_id: str) -> AsteroidDetailResponse:
        """Get detailed asteroid information with CRI"""
        try:
            uuid = UUID(asteroid_id)
        except ValueError:
            raise ValueError("Invalid asteroid ID format")
        
        asteroid = db.query(Asteroid).filter(Asteroid.id == uuid).first()
        if not asteroid:
            raise ValueError("Asteroid not found")
        
        # Get next close approach
        next_approach = db.query(CloseApproach).filter(
            and_(
                CloseApproach.asteroid_id == uuid,
                CloseApproach.closest_approach_date > datetime.now(timezone.utc)
            )
        ).order_by(CloseApproach.closest_approach_date).first()
        
        cri_score = next_approach.calculated_cri if next_approach else None
        risk_level = get_risk_level(cri_score) if cri_score else None
        
        # Get CRI components from log
        cri_components = None
        if next_approach:
            risk_log = db.query(RiskScoringLog).filter(
                RiskScoringLog.close_approach_id == next_approach.id
            ).order_by(RiskScoringLog.calculation_timestamp.desc()).first()
            
            if risk_log and risk_log.component_scores:
                cri_components = CRIComponentsResponse(**risk_log.component_scores)
        
        # Get all approaches
        all_approaches_data = db.query(CloseApproach).filter(
            CloseApproach.asteroid_id == uuid
        ).order_by(CloseApproach.closest_approach_date).all()
        
        all_approaches = [
            CloseApproachResponse(
                id=str(app.id),
                closest_approach_date=app.closest_approach_date,
                miss_distance_km=app.miss_distance_km,
                approach_velocity_kmh=app.approach_velocity_kmh,
                calculated_cri=app.calculated_cri,
                is_next_72h_threat=is_next_72h_threat(
                    app.closest_approach_date.isoformat(),
                    app.calculated_cri or 0
                ),
                days_until_approach=calculate_days_until_approach(
                    app.closest_approach_date.isoformat()
                )
            )
            for app in all_approaches_data
        ]
        
        return AsteroidDetailResponse(
            id=str(asteroid.id),
            neo_id=asteroid.neo_id,
            name=asteroid.name,
            url=asteroid.url,
            diameter_km=asteroid.diameter_km,
            diameter_min_km=asteroid.diameter_min_km,
            diameter_max_km=asteroid.diameter_max_km,
            absolute_magnitude=asteroid.absolute_magnitude,
            is_hazardous=asteroid.is_hazardous,
            is_sentry_object=asteroid.is_sentry_object,
            next_approach=CloseApproachResponse(
                id=str(next_approach.id),
                closest_approach_date=next_approach.closest_approach_date,
                miss_distance_km=next_approach.miss_distance_km,
                approach_velocity_kmh=next_approach.approach_velocity_kmh,
                calculated_cri=next_approach.calculated_cri,
                is_next_72h_threat=is_next_72h_threat(
                    next_approach.closest_approach_date.isoformat(),
                    next_approach.calculated_cri or 0
                ),
                days_until_approach=calculate_days_until_approach(
                    next_approach.closest_approach_date.isoformat()
                )
            ) if next_approach else None,
            cri_score=cri_score,
            risk_level=RiskLevelInfo(**risk_level) if risk_level else None,
            cri_components=cri_components,
            all_approaches=all_approaches,
            created_at=asteroid.created_at,
            nasa_synced_at=asteroid.nasa_synced_at
        )
    
    @staticmethod
    def get_next_72h_threats(db: Session) -> Next72hThreatsResponse:
        """Get asteroids approaching in next 72 hours with high risk"""
        cutoff_time = datetime.now(timezone.utc) + timedelta(hours=72)
        
        threats = db.query(CloseApproach).filter(
            and_(
                CloseApproach.closest_approach_date <= cutoff_time,
                CloseApproach.closest_approach_date > datetime.now(timezone.utc),
                CloseApproach.calculated_cri >= 40  # Filter for medium+ risk
            )
        ).order_by(CloseApproach.calculated_cri.desc()).all()
        
        asteroids = []
        max_cri = None
        
        for approach in threats:
            asteroid = db.query(Asteroid).filter(Asteroid.id == approach.asteroid_id).first()
            if asteroid:
                detail = AsteroidService.get_asteroid_detail(db, str(asteroid.id))
                asteroids.append(detail)
                if max_cri is None or detail.cri_score > max_cri:
                    max_cri = detail.cri_score
        
        critical_count = len([a for a in asteroids if a.cri_score and a.cri_score >= 80])
        
        return Next72hThreatsResponse(
            threats=asteroids[:10],  # Top 10
            total_count=len(asteroids),
            highest_cri=max_cri,
            critical_count=critical_count
        )
    
    @staticmethod
    def search_asteroids(db: Session, query: str, limit: int = 10) -> List[AsteroidDetailResponse]:
        """Full-text search asteroids"""
        results = db.query(Asteroid).filter(
            Asteroid.name.ilike(f"%{query}%")
        ).limit(limit).all()
        
        return [
            AsteroidService.get_asteroid_detail(db, str(a.id))
            for a in results
        ]
