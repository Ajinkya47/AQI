"""
Utility helper functions.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import math


def get_aqi_color(aqi: int) -> str:
    """Get color code for AQI value."""
    if aqi <= 50:
        return "#00E400"  # Green
    elif aqi <= 100:
        return "#FFFF00"  # Yellow
    elif aqi <= 150:
        return "#FF7E00"  # Orange
    elif aqi <= 200:
        return "#FF0000"  # Red
    elif aqi <= 300:
        return "#8F3F97"  # Purple
    else:
        return "#7E0023"  # Maroon


def get_aqi_emoji(aqi: int) -> str:
    """Get emoji for AQI value."""
    if aqi <= 50:
        return "😊"
    elif aqi <= 100:
        return "🙂"
    elif aqi <= 150:
        return "😐"
    elif aqi <= 200:
        return "😷"
    elif aqi <= 300:
        return "🤢"
    else:
        return "☠️"


def format_duration(minutes: float) -> str:
    """Format duration in minutes to readable string."""
    if minutes < 60:
        return f"{int(minutes)} min"
    else:
        hours = int(minutes // 60)
        mins = int(minutes % 60)
        if mins == 0:
            return f"{hours} hr"
        return f"{hours} hr {mins} min"


def calculate_exposure_index(
    aqi_values: List[int],
    duration_minutes: int
) -> float:
    """
    Calculate pollution exposure index.
    
    Higher values indicate more harmful exposure.
    """
    if not aqi_values:
        return 0.0
    
    avg_aqi = sum(aqi_values) / len(aqi_values)
    max_aqi = max(aqi_values)
    
    # Weighted calculation (max AQI matters more)
    weighted_aqi = (avg_aqi * 0.6) + (max_aqi * 0.4)
    
    # Exposure increases with duration
    exposure = weighted_aqi * (duration_minutes / 60)
    
    return round(exposure, 2)


def interpolate_coordinates(
    start: Tuple[float, float],
    end: Tuple[float, float],
    num_points: int
) -> List[Tuple[float, float]]:
    """Generate interpolated points between start and end."""
    points = []
    for i in range(num_points):
        fraction = i / (num_points - 1) if num_points > 1 else 0
        lat = start[0] + (end[0] - start[0]) * fraction
        lon = start[1] + (end[1] - start[1]) * fraction
        points.append((lat, lon))
    return points


def parse_time_string(time_str: str) -> Optional[datetime]:
    """Parse various time string formats."""
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
        "%H:%M:%S",
        "%H:%M"
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(time_str, fmt)
        except ValueError:
            continue
    
    return None


def get_time_period(hour: int) -> str:
    """Get time period name for an hour."""
    if 5 <= hour < 12:
        return "Morning"
    elif 12 <= hour < 17:
        return "Afternoon"
    elif 17 <= hour < 21:
        return "Evening"
    else:
        return "Night"


def round_coordinates(lat: float, lon: float, precision: int = 4) -> Tuple[float, float]:
    """Round coordinates to specified precision."""
    return (round(lat, precision), round(lon, precision))


def meters_to_km(meters: float) -> float:
    """Convert meters to kilometers."""
    return meters / 1000


def kmh_to_ms(kmh: float) -> float:
    """Convert km/h to m/s."""
    return kmh / 3.6


def validate_coordinates(lat: float, lon: float) -> bool:
    """Validate latitude and longitude values."""
    return -90 <= lat <= 90 and -180 <= lon <= 180


def create_bounding_box(
    center: Tuple[float, float],
    radius_km: float
) -> Dict[str, float]:
    """Create a bounding box around a center point."""
    # Approximate degrees per km
    lat_deg_per_km = 1 / 111
    lon_deg_per_km = 1 / (111 * math.cos(math.radians(center[0])))
    
    lat_delta = radius_km * lat_deg_per_km
    lon_delta = radius_km * lon_deg_per_km
    
    return {
        "min_lat": center[0] - lat_delta,
        "max_lat": center[0] + lat_delta,
        "min_lon": center[1] - lon_delta,
        "max_lon": center[1] + lon_delta
    }
