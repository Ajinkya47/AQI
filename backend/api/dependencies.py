"""
Shared dependencies for API routes.
"""

from functools import lru_cache
from backend.config import Settings, get_settings
from backend.services.aqi_service import AQIService
from backend.services.traffic_service import TrafficService
from backend.services.weather_service import WeatherService
from backend.services.alert_service import AlertService
from backend.ml.predictor import AQIPredictor
from backend.ml.route_optimizer import RouteOptimizer


@lru_cache()
def get_aqi_service() -> AQIService:
    """Get AQI service instance."""
    settings = get_settings()
    return AQIService(
        openweather_key=settings.openweather_api_key,
        aqicn_key=settings.aqicn_api_key
    )


@lru_cache()
def get_traffic_service() -> TrafficService:
    """Get traffic service instance."""
    settings = get_settings()
    return TrafficService(google_maps_key=settings.google_maps_api_key)


@lru_cache()
def get_weather_service() -> WeatherService:
    """Get weather service instance."""
    settings = get_settings()
    return WeatherService(api_key=settings.openweather_api_key)


@lru_cache()
def get_alert_service() -> AlertService:
    """Get alert service instance."""
    settings = get_settings()
    return AlertService(settings=settings)


@lru_cache()
def get_predictor() -> AQIPredictor:
    """Get AQI predictor instance."""
    settings = get_settings()
    return AQIPredictor(model_path=settings.model_path)


@lru_cache()
def get_route_optimizer() -> RouteOptimizer:
    """Get route optimizer instance."""
    return RouteOptimizer()
