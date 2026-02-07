"""
Sample asteroid data for development/testing
"""
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from sqlalchemy.orm import Session
from app.models.models import Asteroid, CloseApproach, User
from app.core.security import hash_password
from app.utils.risk_calculator import calculate_cri


SAMPLE_ASTEROIDS = [
    {
        "name": "Apophis (99942)",
        "neo_id": "2099942",
        "diameter_km": 0.375,
        "is_hazardous": True,
        "approaches": [
            {
                "date": datetime.now(timezone.utc) + timedelta(hours=24),
                "miss_distance_km": 38000,
                "velocity_kmh": 15000,
            }
        ]
    },
    {
        "name": "Bennu",
        "neo_id": "101955",
        "diameter_km": 0.493,
        "is_hazardous": True,
        "approaches": [
            {
                "date": datetime.now(timezone.utc) + timedelta(hours=48),
                "miss_distance_km": 225000,
                "velocity_kmh": 12500,
            }
        ]
    },
    {
        "name": "NASA Test Asteroid 1",
        "neo_id": "test-001",
        "diameter_km": 0.15,
        "is_hazardous": False,
        "approaches": [
            {
                "date": datetime.now(timezone.utc) + timedelta(hours=36),
                "miss_distance_km": 500000,
                "velocity_kmh": 18000,
            }
        ]
    },
    {
        "name": "NASA Test Asteroid 2",
        "neo_id": "test-002",
        "diameter_km": 0.75,
        "is_hazardous": True,
        "approaches": [
            {
                "date": datetime.now(timezone.utc) + timedelta(hours=60),
                "miss_distance_km": 150000,
                "velocity_kmh": 16500,
            }
        ]
    },
    {
        "name": "NASA Test Asteroid 3",
        "neo_id": "test-003",
        "diameter_km": 0.25,
        "is_hazardous": False,
        "approaches": [
            {
                "date": datetime.now(timezone.utc) + timedelta(hours=18),
                "miss_distance_km": 750000,
                "velocity_kmh": 14000,
            }
        ]
    },
]


def seed_sample_asteroids(db: Session):
    """Add sample asteroids to database if empty"""
    # Create default user if doesn't exist
    default_user = db.query(User).filter(User.email == "demo@cosmicwatch.io").first()
    if not default_user:
        try:
            # Password: "Demo@12345" - 11 chars, well under 72 byte limit
            pwd = "Demo@12345"
            hashed = hash_password(pwd)
            default_user = User(
                email="demo@cosmicwatch.io",
                username="demo",
                password_hash=hashed,
                is_active=True
            )
            db.add(default_user)
            db.commit()
        except Exception as e:
            print(f"Error creating default user: {e}")
            db.rollback()
    
    # Check if asteroids exist
    existing_count = db.query(Asteroid).count()
    if existing_count > 0:
        return
    
    for asteroid_data in SAMPLE_ASTEROIDS:
        asteroid = Asteroid(
            neo_id=asteroid_data["neo_id"],
            name=asteroid_data["name"],
            diameter_km=asteroid_data["diameter_km"],
            diameter_min_km=asteroid_data["diameter_km"] * 0.9,
            diameter_max_km=asteroid_data["diameter_km"] * 1.1,
            is_hazardous=asteroid_data["is_hazardous"],
            is_sentry_object=False,
            absolute_magnitude=22.0,
            url=f"https://ssd.jpl.nasa.gov/tools/sbdb_lookup.html#/?sstr={asteroid_data['neo_id']}"
        )
        
        db.add(asteroid)
        db.flush()
        
        # Add close approaches
        for approach_data in asteroid_data["approaches"]:
            cri_score, cri_components = calculate_cri(
                diameter_km=asteroid_data["diameter_km"],
                velocity_kmh=approach_data["velocity_kmh"],
                miss_distance_km=approach_data["miss_distance_km"],
                is_hazardous=asteroid_data["is_hazardous"]
            )
            
            approach = CloseApproach(
                asteroid_id=asteroid.id,
                closest_approach_date=approach_data["date"],
                miss_distance_km=approach_data["miss_distance_km"],
                approach_velocity_kmh=approach_data["velocity_kmh"],
                approach_velocity_kms=approach_data["velocity_kmh"] / 3600,
                calculated_cri=cri_score,
                orbiting_body="Earth"
            )
            
            db.add(approach)
        
    db.commit()
