"""
Cosmic Risk Index (CRI) - Custom proprietary risk scoring engine
Formula combines asteroid diameter, velocity, distance, and hazard status
"""
import math
from typing import Optional, Dict
from dataclasses import dataclass


@dataclass
class CRIComponents:
    """Breakdown of CRI calculation"""
    diameter_score: float
    velocity_score: float
    distance_score: float
    hazard_bonus: float
    final_cri: float


def sigmoid(x: float) -> float:
    """
    Sigmoid function to normalize scores to 0-1
    Maps any input to probability-like output
    """
    try:
        return 1 / (1 + math.exp(-x))
    except OverflowError:
        return 1.0 if x > 0 else 0.0


def calculate_cri(
    diameter_km: Optional[float],
    velocity_kmh: Optional[float],
    miss_distance_km: Optional[float],
    is_hazardous: bool
) -> tuple[float, CRIComponents]:
    """
    Calculate Cosmic Risk Index (0-100)
    
    Args:
        diameter_km: Estimated diameter in kilometers
        velocity_kmh: Velocity relative to Earth in km/h
        miss_distance_km: Miss distance from Earth in km
        is_hazardous: NASA hazard classification
    
    Returns:
        Tuple of (cri_score, components_breakdown)
    """
    
    # Safe defaults and bounds checking
    diameter_km = diameter_km or 0.05  # Minimum detectable asteroid
    velocity_kmh = velocity_kmh or 15000  # Typical asteroid velocity
    miss_distance_km = miss_distance_km or 1000000  # ~2.6x Earth-Moon distance safe
    
    # ============ DIAMETER SCORE ============
    # Larger asteroids = higher risk
    # Formula: sigmoid((diameter / 1km) * weight)
    diameter_normalized = (diameter_km / 1) * 100
    diameter_score_raw = sigmoid(diameter_normalized / 10)
    diameter_score = diameter_score_raw * 100
    
    # ============ VELOCITY SCORE ============
    # Faster = higher energy impact
    # Formula: sigmoid((velocity / 30000 kmh) * weight)
    velocity_normalized = (velocity_kmh / 30000) * 100
    velocity_score_raw = sigmoid(velocity_normalized / 10)
    velocity_score = velocity_score_raw * 100
    
    # ============ DISTANCE SCORE ============
    # Closer = higher risk
    # Formula: sigmoid(1 / (distance + safety_margin))
    # Log scale because distance matters more at close ranges
    distance_factor = 1 / (math.log(miss_distance_km + 1) + 1)
    distance_score_raw = sigmoid(distance_factor * 100)
    distance_score = distance_score_raw * 100
    
    # ============ HAZARD BONUS ============
    # NASA's hazard classification adds 15-20 points
    hazard_bonus = 15.0 if is_hazardous else 0.0
    
    # ============ FINAL CRI CALCULATION ============
    # Weighted combination of all factors
    final_cri = (
        (diameter_score * 0.35) +      # Asteroid size: 35% weight
        (velocity_score * 0.25) +      # Speed: 25% weight
        (distance_score * 0.25) +      # Proximity: 25% weight
        (hazard_bonus * 0.15)          # NASA flag: 15% weight
    )
    
    # Clamp to 0-100 range
    final_cri = max(0, min(100, final_cri))
    
    components = CRIComponents(
        diameter_score=round(diameter_score, 2),
        velocity_score=round(velocity_score, 2),
        distance_score=round(distance_score, 2),
        hazard_bonus=round(hazard_bonus, 2),
        final_cri=round(final_cri, 2)
    )
    
    return final_cri, components


def get_risk_level(cri: float) -> Dict[str, str]:
    """
    Convert CRI score to human-readable risk level
    
    Returns:
        Dict with 'level', 'emoji', 'color', 'description'
    """
    if cri >= 81:
        return {
            "level": "CRITICAL",
            "emoji": "⛔",
            "color": "#FF1744",
            "description": "Rare celestial event - Extremely close approach",
            "recommendation": "High scientific interest - Monitor in real-time"
        }
    elif cri >= 61:
        return {
            "level": "RED",
            "emoji": "⚠️",
            "color": "#FF6B35",
            "description": "Very close approach - Significant risk",
            "recommendation": "Add to watchlist for continuous monitoring"
        }
    elif cri >= 41:
        return {
            "level": "ORANGE",
            "emoji": "🟠",
            "color": "#FFA500",
            "description": "High interest - Moderately close approach",
            "recommendation": "Worth tracking for research"
        }
    elif cri >= 21:
        return {
            "level": "YELLOW",
            "emoji": "🟡",
            "color": "#FFD700",
            "description": "Monitor closely - Notable asteroid",
            "recommendation": "Interesting for astronomy enthusiasts"
        }
    else:
        return {
            "level": "GREEN",
            "emoji": "🟢",
            "color": "#00D084",
            "description": "Safe to observe - Low risk approach",
            "recommendation": "Routine asteroid - Safe observation"
        }


def calculate_days_until_approach(approach_date: str) -> int:
    """Calculate days until close approach"""
    from datetime import datetime
    approach = datetime.fromisoformat(approach_date.replace('Z', '+00:00'))
    days = (approach - datetime.now()).days
    return max(0, days)


def is_next_72h_threat(approach_date: str, cri: float) -> bool:
    """Check if approach is within 72 hours and high risk"""
    days = calculate_days_until_approach(approach_date)
    return days <= 3 and cri >= 40
