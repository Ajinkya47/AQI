"""
Configuration management for the application.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Keys
    openweather_api_key: str = ""
    aqicn_api_key: str = ""
    google_maps_api_key: str = ""
    
    # App Settings
    debug: bool = True
    database_url: str = "sqlite:///./pollution_traffic.db"
    
    # Model Settings
    model_path: str = "backend/ml/models/aqi_model.joblib"
    
    # AQI Thresholds
    aqi_good: int = 50
    aqi_moderate: int = 100
    aqi_unhealthy_sensitive: int = 150
    aqi_unhealthy: int = 200
    aqi_very_unhealthy: int = 300
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
