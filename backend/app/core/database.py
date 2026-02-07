"""
Database connection and session management
"""
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Generator

from app.core.config import settings

# Create engine with connection pooling
# Check if using SQLite
if "sqlite" in settings.database_url:
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False},
    )
else:
    engine = create_engine(
        settings.database_url,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,  # Test connections before using
    )

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


def get_db() -> Generator:
    """Dependency for getting DB session in routes"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables"""
    Base.metadata.create_all(bind=engine)
