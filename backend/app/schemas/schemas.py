"""
Pydantic schemas for API request/response validation
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ============ Authentication Schemas ============

class UserRegisterRequest(BaseModel):
    """User registration request"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=72)


class UserLoginRequest(BaseModel):
    """User login request"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 900  # seconds


class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str


class UserProfileResponse(BaseModel):
    """User profile response"""
    id: str
    email: str
    username: str
    preferences: Dict[str, Any] = {}
    created_at: datetime
    is_active: bool = True
    
    model_config = ConfigDict(from_attributes=True)


# ============ Asteroid Schemas ============

class AsteroidBasicResponse(BaseModel):
    """Basic asteroid info for listings"""
    id: str
    neo_id: str
    name: str
    diameter_km: Optional[float] = None
    is_hazardous: bool = False
    
    model_config = ConfigDict(from_attributes=True)


class RiskLevelInfo(BaseModel):
    """Risk level interpretation"""
    level: str
    emoji: str
    color: str
    description: str
    recommendation: str


class CRIComponentsResponse(BaseModel):
    """CRI calculation breakdown"""
    diameter_score: float
    velocity_score: float
    distance_score: float
    hazard_bonus: float
    final_cri: float


class CloseApproachResponse(BaseModel):
    """Close approach data"""
    id: str
    closest_approach_date: datetime
    miss_distance_km: Optional[float] = None
    approach_velocity_kmh: Optional[float] = None
    calculated_cri: Optional[float] = None
    is_next_72h_threat: bool = False
    days_until_approach: int = 0
    
    model_config = ConfigDict(from_attributes=True)


class AsteroidDetailResponse(BaseModel):
    """Detailed asteroid info"""
    id: str
    neo_id: str
    name: str
    url: Optional[str] = None
    
    # Physical properties
    diameter_km: Optional[float] = None
    diameter_min_km: Optional[float] = None
    diameter_max_km: Optional[float] = None
    absolute_magnitude: Optional[float] = None
    
    # Hazard info
    is_hazardous: bool = False
    is_sentry_object: bool = False
    
    # Next close approach with CRI
    next_approach: Optional[CloseApproachResponse] = None
    cri_score: Optional[float] = None
    risk_level: Optional[RiskLevelInfo] = None
    cri_components: Optional[CRIComponentsResponse] = None
    
    # All approaches
    all_approaches: List[CloseApproachResponse] = []
    
    # Timestamps
    created_at: datetime
    nasa_synced_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class AsteroidListResponse(BaseModel):
    """Paginated asteroids response"""
    items: List[AsteroidDetailResponse]
    total_count: int
    page: int
    page_size: int
    total_pages: int


# ============ Watchlist Schemas ============

class WatchlistAddRequest(BaseModel):
    """Add to watchlist request"""
    asteroid_id: str
    alert_threshold_distance_km: Optional[float] = None
    alert_threshold_cri: Optional[float] = None


class WatchlistUpdateRequest(BaseModel):
    """Update watchlist item request"""
    alert_threshold_distance_km: Optional[float] = None
    alert_threshold_cri: Optional[float] = None
    custom_notes: Optional[str] = None


class WatchlistItemResponse(BaseModel):
    """Watchlist item response"""
    id: str
    asteroid: AsteroidDetailResponse
    alert_threshold_distance_km: Optional[float] = None
    alert_threshold_cri: Optional[float] = None
    custom_notes: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class WatchlistResponse(BaseModel):
    """User watchlist response"""
    items: List[WatchlistItemResponse]
    total_count: int


# ============ Alert Schemas ============

class AlertTypeEnum(str, Enum):
    """Alert type enumeration"""
    DISTANCE = "DISTANCE"
    RISK_SCORE = "RISK_SCORE"
    APPROACH_24H = "APPROACH_24H"
    APPROACH_72H = "APPROACH_72H"


class AlertResponse(BaseModel):
    """Alert response"""
    id: str
    asteroid_id: str
    asteroid_name: Optional[str] = None
    alert_type: str
    triggered_reason: Optional[str] = None
    cri_score_at_trigger: Optional[float] = None
    distance_at_trigger_km: Optional[float] = None
    is_read: bool = False
    triggered_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class AlertListResponse(BaseModel):
    """Paginated alerts response"""
    items: List[AlertResponse]
    total_count: int
    unread_count: int


class AlertStatsResponse(BaseModel):
    """Alert statistics"""
    total_alerts: int
    unread_alerts: int
    critical_alerts: int  # CRI >= 80
    high_alerts: int      # CRI >= 60
    medium_alerts: int    # CRI >= 40
    alerts_by_type: Dict[str, int]


# ============ Search & Filter Schemas ============

class SearchAsteroidsRequest(BaseModel):
    """Search request"""
    query: str = Field(..., min_length=1, max_length=255)
    limit: int = Field(10, ge=1, le=100)


class ThreatLevel(str, Enum):
    """Threat level filter"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Next72hThreatsResponse(BaseModel):
    """Next 72 hours threats summary"""
    threats: List[AsteroidDetailResponse]
    total_count: int
    highest_cri: Optional[float] = None
    critical_count: int


# ============ Analytics Schemas ============

class RiskDistributionBucket(BaseModel):
    """Risk score distribution bucket"""
    range_min: int
    range_max: int
    count: int
    percentage: float
    examples: List[str] = []  # Asteroid names


class RiskDistributionResponse(BaseModel):
    """Risk distribution analytics"""
    buckets: List[RiskDistributionBucket]
    total_asteroids: int
    average_cri: float
    median_cri: float


class TopThreatResponse(BaseModel):
    """Top threat asteroid"""
    asteroid_id: str
    name: str
    cri_score: float
    next_approach_date: Optional[datetime] = None
    days_until_approach: Optional[int] = None


class TopThreatsResponse(BaseModel):
    """Top threats list"""
    threats: List[TopThreatResponse]
    calculation_timestamp: datetime


class UserActivityResponse(BaseModel):
    """User activity metrics"""
    total_watchlist_items: int
    total_alerts_triggered: int
    unread_alerts: int
    favorite_threat_level: str
    last_api_sync: Optional[datetime] = None


# ============ Error Schemas ============

class ErrorResponse(BaseModel):
    """Error response"""
    detail: str
    error_code: str
    timestamp: datetime


class ValidationErrorResponse(BaseModel):
    """Validation error response"""
    detail: str
    errors: List[Dict[str, Any]]
    timestamp: datetime

# ============ Chatbot Schemas ============

class ChatMessageRequest(BaseModel):
    """Chat message request"""
    message: str = Field(..., min_length=1, max_length=2000)
    conversation_id: Optional[str] = None


class ChatMessageResponse(BaseModel):
    """Chat message response"""
    response: str
    conversation_id: str
    timestamp: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ChatHistoryMessage(BaseModel):
    """Single message in chat history"""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime


class ConversationResponse(BaseModel):
    """Full conversation response"""
    conversation_id: str
    messages: List[ChatHistoryMessage]
    created_at: datetime
    last_message_at: datetime
    
    model_config = ConfigDict(from_attributes=True)