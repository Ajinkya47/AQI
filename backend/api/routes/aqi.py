"""
AQI (Air Quality Index) API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime

from backend.api.dependencies import get_aqi_service, get_weather_service
from backend.services.aqi_service import AQIService
from backend.services.weather_service import WeatherService
from backend.models.schemas import (
    AQIResponse,
    AQIHistoryResponse,
    LocationQuery,
    MultiLocationAQI
)

router = APIRouter()


@router.get("/{city}", response_model=AQIResponse)
async def get_current_aqi(
    city: str,
    aqi_service: AQIService = Depends(get_aqi_service),
    weather_service: WeatherService = Depends(get_weather_service)
):
    """
    Get current AQI for a city.
    
    Returns current air quality index along with weather data.
    """
    try:
        aqi_data = await aqi_service.get_current_aqi(city)
        weather_data = await weather_service.get_current_weather(city)
        
        return AQIResponse(
            city=city,
            aqi=aqi_data["aqi"],
            category=aqi_data["category"],
            pm25=aqi_data.get("pm25"),
            pm10=aqi_data.get("pm10"),
            o3=aqi_data.get("o3"),
            no2=aqi_data.get("no2"),
            temperature=weather_data.get("temperature"),
            humidity=weather_data.get("humidity"),
            wind_speed=weather_data.get("wind_speed"),
            timestamp=datetime.utcnow()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/location/coordinates")
async def get_aqi_by_coordinates(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    aqi_service: AQIService = Depends(get_aqi_service)
):
    """Get AQI by geographic coordinates."""
    try:
        aqi_data = await aqi_service.get_aqi_by_coordinates(lat, lon)
        return aqi_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/multiple", response_model=List[MultiLocationAQI])
async def get_multiple_locations_aqi(
    locations: List[LocationQuery],
    aqi_service: AQIService = Depends(get_aqi_service)
):
    """Get AQI for multiple locations at once."""
    results = []
    for location in locations:
        try:
            if location.city:
                aqi_data = await aqi_service.get_current_aqi(location.city)
            else:
                aqi_data = await aqi_service.get_aqi_by_coordinates(
                    location.latitude, location.longitude
                )
            results.append(MultiLocationAQI(
                location=location.city or f"{location.latitude},{location.longitude}",
                aqi=aqi_data["aqi"],
                category=aqi_data["category"]
            ))
        except Exception:
            results.append(MultiLocationAQI(
                location=location.city or f"{location.latitude},{location.longitude}",
                aqi=None,
                category="Unknown",
                error="Failed to fetch data"
            ))
    return results


@router.get("/{city}/history", response_model=AQIHistoryResponse)
async def get_aqi_history(
    city: str,
    hours: int = Query(default=24, ge=1, le=168),
    aqi_service: AQIService = Depends(get_aqi_service)
):
    """
    Get historical AQI data for a city.
    
    Returns hourly AQI data for the specified number of hours.
    """
    try:
        history = await aqi_service.get_historical_data(city, hours)
        return AQIHistoryResponse(
            city=city,
            hours=hours,
            data=history
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
