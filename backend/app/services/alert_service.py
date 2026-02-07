"""
Alert system service
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timezone
from typing import List
from uuid import UUID

from app.models.models import Alert, User, Asteroid, CloseApproach, Watchlist
from app.schemas.schemas import (
    AlertResponse, AlertListResponse, AlertStatsResponse, AlertTypeEnum
)


class AlertService:
    """Handle alert management"""
    
    @staticmethod
    def trigger_alert(
        db: Session,
        user_id: str,
        asteroid_id: str,
        close_approach_id: str,
        alert_type: AlertTypeEnum,
        triggered_reason: str,
        cri_score: float,
        distance_km: float
    ) -> Alert:
        """
        Trigger an alert for user
        """
        try:
            user_uuid = UUID(user_id)
            asteroid_uuid = UUID(asteroid_id)
            approach_uuid = UUID(close_approach_id)
        except ValueError:
            raise ValueError("Invalid IDs")
        
        # Check if alert already exists (prevent duplicates)
        existing = db.query(Alert).filter(
            and_(
                Alert.user_id == user_uuid,
                Alert.close_approach_id == approach_uuid,
                Alert.alert_type == alert_type.value
            )
        ).first()
        
        if existing:
            return existing
        
        alert = Alert(
            user_id=user_uuid,
            asteroid_id=asteroid_uuid,
            close_approach_id=approach_uuid,
            alert_type=alert_type.value,
            triggered_reason=triggered_reason,
            cri_score_at_trigger=cri_score,
            distance_at_trigger_km=distance_km,
            is_read=False,
            is_notified=False
        )
        
        db.add(alert)
        db.commit()
        db.refresh(alert)
        
        return alert
    
    @staticmethod
    def get_user_alerts(
        db: Session,
        user_id: str,
        unread_only: bool = False,
        limit: int = 50,
        offset: int = 0
    ) -> AlertListResponse:
        """Get user alerts"""
        try:
            user_uuid = UUID(user_id)
        except ValueError:
            raise ValueError("Invalid user ID")
        
        query = db.query(Alert).filter(Alert.user_id == user_uuid)
        
        if unread_only:
            query = query.filter(Alert.is_read == False)
        
        total_count = query.count()
        
        alerts = query.order_by(Alert.triggered_at.desc()).limit(limit).offset(offset).all()
        
        # Get unread count
        unread_count = db.query(Alert).filter(
            and_(
                Alert.user_id == user_uuid,
                Alert.is_read == False
            )
        ).count()
        
        response_items = [
            AlertResponse(
                id=str(alert.id),
                asteroid_id=str(alert.asteroid_id),
                asteroid_name=db.query(Asteroid.name).filter(
                    Asteroid.id == alert.asteroid_id
                ).scalar(),
                alert_type=alert.alert_type,
                triggered_reason=alert.triggered_reason,
                cri_score_at_trigger=alert.cri_score_at_trigger,
                distance_at_trigger_km=alert.distance_at_trigger_km,
                is_read=alert.is_read,
                triggered_at=alert.triggered_at
            )
            for alert in alerts
        ]
        
        return AlertListResponse(
            items=response_items,
            total_count=total_count,
            unread_count=unread_count
        )
    
    @staticmethod
    def mark_alert_read(db: Session, user_id: str, alert_id: str) -> Alert:
        """Mark alert as read"""
        try:
            user_uuid = UUID(user_id)
            alert_uuid = UUID(alert_id)
        except ValueError:
            raise ValueError("Invalid IDs")
        
        alert = db.query(Alert).filter(
            and_(
                Alert.id == alert_uuid,
                Alert.user_id == user_uuid
            )
        ).first()
        
        if not alert:
            raise ValueError("Alert not found")
        
        alert.is_read = True
        alert.read_at = datetime.now(timezone.utc)
        
        db.commit()
        db.refresh(alert)
        
        return alert
    
    @staticmethod
    def delete_alert(db: Session, user_id: str, alert_id: str) -> bool:
        """Delete alert"""
        try:
            user_uuid = UUID(user_id)
            alert_uuid = UUID(alert_id)
        except ValueError:
            raise ValueError("Invalid IDs")
        
        alert = db.query(Alert).filter(
            and_(
                Alert.id == alert_uuid,
                Alert.user_id == user_uuid
            )
        ).first()
        
        if not alert:
            raise ValueError("Alert not found")
        
        db.delete(alert)
        db.commit()
        
        return True
    
    @staticmethod
    def get_alert_stats(db: Session, user_id: str, days: int = 7) -> AlertStatsResponse:
        """Get alert statistics"""
        try:
            user_uuid = UUID(user_id)
        except ValueError:
            raise ValueError("Invalid user ID")
        
        cutoff = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        cutoff -= __import__('datetime').timedelta(days=days)
        
        query = db.query(Alert).filter(
            and_(
                Alert.user_id == user_uuid,
                Alert.triggered_at >= cutoff
            )
        )
        
        total = query.count()
        unread = query.filter(Alert.is_read == False).count()
        critical = query.filter(Alert.cri_score_at_trigger >= 80).count()
        high = query.filter(
            and_(
                Alert.cri_score_at_trigger >= 60,
                Alert.cri_score_at_trigger < 80
            )
        ).count()
        medium = query.filter(
            and_(
                Alert.cri_score_at_trigger >= 40,
                Alert.cri_score_at_trigger < 60
            )
        ).count()
        
        # Count by type
        from sqlalchemy import func as sql_func
        type_counts = db.query(
            Alert.alert_type,
            sql_func.count(Alert.id).label('count')
        ).filter(
            and_(
                Alert.user_id == user_uuid,
                Alert.triggered_at >= cutoff
            )
        ).group_by(Alert.alert_type).all()
        
        alerts_by_type = {t[0]: t[1] for t in type_counts}
        
        return AlertStatsResponse(
            total_alerts=total,
            unread_alerts=unread,
            critical_alerts=critical,
            high_alerts=high,
            medium_alerts=medium,
            alerts_by_type=alerts_by_type
        )
    
    @staticmethod
    def check_watchlist_thresholds(db: Session, user_id: str) -> int:
        """
        Check watchlist items for threshold violations
        Returns count of new alerts triggered
        """
        try:
            user_uuid = UUID(user_id)
        except ValueError:
            raise ValueError("Invalid user ID")
        
        alerts_triggered = 0
        
        # Get all watchlist items
        watchlist_items = db.query(Watchlist).filter(Watchlist.user_id == user_uuid).all()
        
        for item in watchlist_items:
            # Get next close approach
            next_approach = db.query(CloseApproach).filter(
                and_(
                    CloseApproach.asteroid_id == item.asteroid_id,
                    CloseApproach.closest_approach_date > datetime.now(timezone.utc)
                )
            ).order_by(CloseApproach.closest_approach_date).first()
            
            if not next_approach:
                continue
            
            # Check distance threshold
            if item.alert_threshold_distance_km:
                if next_approach.miss_distance_km and next_approach.miss_distance_km <= item.alert_threshold_distance_km:
                    AlertService.trigger_alert(
                        db=db,
                        user_id=user_id,
                        asteroid_id=str(item.asteroid_id),
                        close_approach_id=str(next_approach.id),
                        alert_type=AlertTypeEnum.DISTANCE,
                        triggered_reason=f"Asteroid within {item.alert_threshold_distance_km} km threshold",
                        cri_score=next_approach.calculated_cri or 0,
                        distance_km=next_approach.miss_distance_km or 0
                    )
                    alerts_triggered += 1
            
            # Check CRI threshold
            if item.alert_threshold_cri:
                if next_approach.calculated_cri and next_approach.calculated_cri >= item.alert_threshold_cri:
                    AlertService.trigger_alert(
                        db=db,
                        user_id=user_id,
                        asteroid_id=str(item.asteroid_id),
                        close_approach_id=str(next_approach.id),
                        alert_type=AlertTypeEnum.RISK_SCORE,
                        triggered_reason=f"Risk score {next_approach.calculated_cri} exceeds threshold {item.alert_threshold_cri}",
                        cri_score=next_approach.calculated_cri,
                        distance_km=next_approach.miss_distance_km or 0
                    )
                    alerts_triggered += 1
        
        return alerts_triggered
