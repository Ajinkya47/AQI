"""
Pydantic models for request/response validation.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Tuple
from datetime import datetime
from enum import Enum


# Enums
class AQICategory(str, Enum):
    GOOD = "Good"
    MODERATE = "Moderate"
    UNHEALTHY_SENSITIVE = "Unhealthy for Sensitive Groups"
    UNHEALTHY = "Unhealthy"
    VERY_UNHEALTHY = "Very Unhealthy"
    HAZARDOUS = "Hazardous"


class CongestionLevel(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    SEVERE = "severe"


class TrendDirection(str, Enum):
    IMPROVING = "improving"
    STABLE = "stable"
    WORSENING = "worsening"


class RoutePreference(str, Enum):
    FASTEST = "fastest"
    CLEANEST = "cleanest"
    BALANCED = "balanced"


class AlertType(str, Enum):
    INFO = "info"
    WARNING = "warning"
    DANGER = "danger"
    CRITICAL = "critical"


# AQI Models
class AQIResponse(BaseModel):
    city: str
    aqi: int
    category: str
    pm25: Optional[float] = None
    pm10: Optional[float] = None
    o3: Optional[float] = None
    no2: Optional[float] = None
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    wind_speed: Optional[float] = None
    timestamp: datetime


class LocationQuery(BaseModel):
    city: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class MultiLocationAQI(BaseModel):
    location: str
    aqi: Optional[int]
    category: str
    error: Optional[str] = None


class AQIHistoryPoint(BaseModel):
    timestamp: datetime
    aqi: int
    category: str


class AQIHistoryResponse(BaseModel):
    city: str
    hours: int
    data: List[AQIHistoryPoint]


# Traffic Models
class TrafficPoint(BaseModel):
    latitude: float
    longitude: float
    congestion_level: CongestionLevel
    delay_minutes: Optional[int] = None
    description: Optional[str] = None


class TrafficResponse(BaseModel):
    city: str
    overall_congestion: CongestionLevel
    hotspots: List[TrafficPoint]
    average_speed_kmh: Optional[float] = None
    timestamp: datetime


# Prediction Models
class PredictionInput(BaseModel):
    temperature: float = Field(..., ge=-50, le=60)
    humidity: float = Field(..., ge=0, le=100)
    wind_speed: float = Field(..., ge=0, le=200)
    hour: int = Field(..., ge=0, le=23)
    day_of_week: int = Field(..., ge=0, le=6)
    current_aqi: int = Field(..., ge=0, le=500)


class PredictionResponse(BaseModel):
    city: str
    current_aqi: int
    current_category: str
    predicted_2hr: int
    predicted_4hr: int
    category_2hr: str
    category_4hr: str
    trend: TrendDirection
    confidence: float
    timestamp: datetime


class TimeRecommendation(BaseModel):
    time_slot: str
    expected_aqi: int
    category: str
    recommendation: str


class BestTimeResponse(BaseModel):
    city: str
    current_aqi: int
    recommendations: List[TimeRecommendation]


# Alert Models
class AlertResponse(BaseModel):
    alert_type: AlertType
    title: str
    message: str
    aqi_value: Optional[int] = None
    time_frame: Optional[str] = None
    actions: List[str]
    timestamp: datetime


# Route Models
class Coordinates(BaseModel):
    latitude: float
    longitude: float


class RouteRequest(BaseModel):
    origin: Coordinates
    destination: Coordinates
    preference: RoutePreference = RoutePreference.BALANCED


class RouteWaypoint(BaseModel):
    coordinates: Coordinates
    aqi: int
    traffic_level: CongestionLevel


class OptimizedRoute(BaseModel):
    name: str
    waypoints: List[RouteWaypoint]
    total_distance_km: float
    estimated_time_minutes: int
    average_aqi: float
    max_aqi: int
    pollution_exposure_score: float
    recommendation_reason: str


class RouteSavings(BaseModel):
    time_saved_minutes: int
    pollution_reduction_percent: float
    distance_difference_km: float


class RouteResponse(BaseModel):
    origin: Coordinates
    destination: Coordinates
    recommended_route: OptimizedRoute
    alternatives: List[OptimizedRoute]
    savings: RouteSavings


class RouteComparisonItem(BaseModel):
    route: OptimizedRoute
    rank: int
    pros: List[str]
    cons: List[str]


class RouteComparison(BaseModel):
    origin: Coordinates
    destination: Coordinates
    routes: List[RouteComparisonItem]
    recommendation: str
