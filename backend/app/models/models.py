"""
Cosmic Watch - Database Models

Copyright © 2026 Rohit. Made with love by Rohit.
All rights reserved.

Repository: https://github.com/rohitb6/Cosmic_Watch
"""
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, ForeignKey, 
    Text, JSON, Index, UniqueConstraint, func
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime, timezone

from app.core.database import Base


class User(Base):
    """User account model"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # JSON preferences storage
    preferences = Column(JSON, default={
        "theme": "dark",
        "notification_frequency": "daily",
        "risk_threshold": 30
    })
    
    # Relationships
    watchlist_items = relationship("Watchlist", back_populates="user", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="user", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_user_email', 'email'),
        Index('idx_user_active', 'is_active'),
    )


class Asteroid(Base):
    """Asteroid information from NASA NeoWs API"""
    __tablename__ = "asteroids"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    neo_id = Column(String(20), unique=True, nullable=False, index=True)  # NASA ID
    name = Column(String(255), nullable=False, index=True)
    url = Column(String(500), nullable=True)
    
    # Physical properties
    diameter_km = Column(Float, nullable=True)
    diameter_min_km = Column(Float, nullable=True)
    diameter_max_km = Column(Float, nullable=True)
    absolute_magnitude = Column(Float, nullable=True)
    
    # Hazard classification
    is_hazardous = Column(Boolean, default=False, index=True)
    is_sentry_object = Column(Boolean, default=False)
    
    # Tracking
    nasa_synced_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    close_approaches = relationship("CloseApproach", back_populates="asteroid", cascade="all, delete-orphan")
    watchlist_items = relationship("Watchlist", back_populates="asteroid", cascade="all, delete-orphan")
    risk_logs = relationship("RiskScoringLog", back_populates="asteroid", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_asteroid_hazardous', 'is_hazardous'),
        Index('idx_asteroid_name', 'name'),
    )


class CloseApproach(Base):
    """Close approach records for asteroids"""
    __tablename__ = "close_approaches"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asteroid_id = Column(UUID(as_uuid=True), ForeignKey("asteroids.id"), nullable=False, index=True)
    
    # Approach data
    closest_approach_date = Column(DateTime(timezone=True), nullable=False, index=True)
    close_approach_date_full = Column(String(50), nullable=True)
    
    # Distance metrics (in km)
    miss_distance_km = Column(Float, nullable=True)
    miss_distance_au = Column(Float, nullable=True)  # Astronomical Units
    miss_distance_lunar = Column(Float, nullable=True)
    
    # Velocity data
    approach_velocity_kmh = Column(Float, nullable=True)
    approach_velocity_kms = Column(Float, nullable=True)
    
    # Relative position
    orbiting_body = Column(String(50), default="Earth")
    is_conjunct = Column(Boolean, default=False)  # Conjunction with other celestial bodies
    
    # Calculated risk score (denormalized for performance)
    calculated_cri = Column(Float, nullable=True)
    
    # Tracking
    nasa_synced_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationship
    asteroid = relationship("Asteroid", back_populates="close_approaches")
    
    __table_args__ = (
        Index('idx_approach_date', 'closest_approach_date'),
        Index('idx_approach_asteroid_date', 'asteroid_id', 'closest_approach_date'),
    )


class Watchlist(Base):
    """User watchlist items"""
    __tablename__ = "watchlists"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    asteroid_id = Column(UUID(as_uuid=True), ForeignKey("asteroids.id"), nullable=False, index=True)
    
    # Alert thresholds (user customizable)
    alert_threshold_distance_km = Column(Float, nullable=True)  # None = no distance alert
    alert_threshold_cri = Column(Float, nullable=True)  # None = no risk alert
    
    # User notes
    custom_notes = Column(Text, nullable=True)
    
    # Tracking
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="watchlist_items")
    asteroid = relationship("Asteroid", back_populates="watchlist_items")
    
    __table_args__ = (
        UniqueConstraint('user_id', 'asteroid_id', name='uq_user_asteroid'),
        Index('idx_watchlist_user', 'user_id'),
    )


class Alert(Base):
    """User alerts for asteroid approaches"""
    __tablename__ = "alerts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    asteroid_id = Column(UUID(as_uuid=True), ForeignKey("asteroids.id"), nullable=False, index=True)
    close_approach_id = Column(UUID(as_uuid=True), ForeignKey("close_approaches.id"), nullable=True)
    
    # Alert metadata
    alert_type = Column(String(50), nullable=False)  # DISTANCE, RISK_SCORE, APPROACH_24H, APPROACH_72H
    triggered_reason = Column(String(255), nullable=True)
    cri_score_at_trigger = Column(Float, nullable=True)
    distance_at_trigger_km = Column(Float, nullable=True)
    
    # Status
    is_read = Column(Boolean, default=False, index=True)
    is_notified = Column(Boolean, default=False)
    notification_method = Column(String(50), nullable=True)  # email, dashboard, push
    
    # Tracking
    triggered_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    read_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    user = relationship("User", back_populates="alerts")
    
    __table_args__ = (
        Index('idx_alert_user_read', 'user_id', 'is_read'),
        Index('idx_alert_triggered', 'triggered_at'),
    )


class RiskScoringLog(Base):
    """Analytics log for CRI calculations"""
    __tablename__ = "risk_scoring_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asteroid_id = Column(UUID(as_uuid=True), ForeignKey("asteroids.id"), nullable=False, index=True)
    close_approach_id = Column(UUID(as_uuid=True), ForeignKey("close_approaches.id"), nullable=True)
    
    # CRI scores
    cri_score = Column(Float, nullable=False)
    
    # Component breakdown
    component_scores = Column(JSON, default={})  # {diameter_score, velocity_score, distance_score, hazard_bonus}
    
    # Inputs used in calculation
    calculation_inputs = Column(JSON, default={})
    
    # Tracking
    calculation_timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    asteroid = relationship("Asteroid", back_populates="risk_logs")
    
    __table_args__ = (
        Index('idx_risk_log_asteroid', 'asteroid_id'),
        Index('idx_risk_log_timestamp', 'calculation_timestamp'),
    )


class NASAAPICache(Base):
    """Cache for NASA API responses to avoid rate limiting"""
    __tablename__ = "nasa_api_cache"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    endpoint = Column(String(255), nullable=False, index=True)
    query_params = Column(JSON, nullable=True)
    response_data = Column(JSON, nullable=False)
    
    # Cache management
    cached_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    hit_count = Column(Integer, default=0)
    
    __table_args__ = (
        Index('idx_cache_endpoint_expires', 'endpoint', 'expires_at'),
    )
