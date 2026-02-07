"""
Cosmic Watch - Configuration Management

Copyright © 2026 Rohit. Made with love by Rohit.
All rights reserved.

Repository: https://github.com/rohitb6/Cosmic_Watch
"""
from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path
import os
from dotenv import load_dotenv

# Load .env file explicitly from parent directory
env_path = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(env_path)


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # App
    app_name: str = "Cosmic Watch"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Database
    database_url: str = "sqlite:///./cosmic_watch.db"
    
    # Redis
    redis_url: str = ""  # Optional, disabled for local dev
    
    # JWT
    secret_key: str = "your-super-secret-key-change-in-prod"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    
    # NASA API - Load from environment, with fallback to DEMO_KEY
    nasa_api_key: str = "DEMO_KEY"
    nasa_base_url: str = "https://api.nasa.gov/neo/rest/v1"
    nasa_cache_ttl_hours: int = 6
    
    # OpenAI API
    openai_api_key: str = ""
    openai_model: str = "gpt-3.5-turbo"
    
    # CORS
    cors_origins: list = ["http://localhost:3000", "http://localhost:5173", "http://localhost:3001"]
    
    # Pagination
    default_page_size: int = 20
    max_page_size: int = 100
    
    class Config:
        case_sensitive = False


settings = Settings()
