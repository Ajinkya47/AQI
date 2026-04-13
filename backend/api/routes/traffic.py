"""
Traffic data API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional

from backend.api.dependencies import get_traffic_service
from backend.services.traffic_service import TrafficService
from backend.models.schemas import (
    TrafficResponse,
    TrafficPoint,
    CongestionLevel
)

router = APIRouter()


@router.get("/{city}", response_model=TrafficResponse)
async def get_traffic_data(
    city: str,
    traffic_service: TrafficService = Depends(get_traffic_service)
):
    """
    Get current traffic conditions for a city.
    
    Returns congestion levels and traffic hotspots.
    """
    try:
        traffic_data = await traffic_service.get_city_traffic(city)
        return traffic_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/route/conditions")
async def get_route_traffic(
    origin_lat: float = Query(..., ge=-90, le=90),
    origin_lon: float = Query(..., ge=-180, le=180),
    dest_lat: float = Query(..., ge=-90, le=90),
    dest_lon: float = Query(..., ge=-180, le=180),
    traffic_service: TrafficService = Depends(get_traffic_service)
):
    """Get traffic conditions along a specific route."""
    try:
        conditions = await traffic_service.get_route_traffic(
            origin=(origin_lat, origin_lon),
            destination=(dest_lat, dest_lon)
        )
        return conditions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{city}/hotspots", response_model=List[TrafficPoint])
async def get_traffic_hotspots(
    city: str,
    limit: int = Query(default=10, ge=1, le=50),
    traffic_service: TrafficService = Depends(get_traffic_service)
):
    """Get top traffic congestion hotspots in a city."""
    try:
        hotspots = await traffic_service.get_hotspots(city, limit)
        return hotspots
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{city}/heatmap")
async def get_traffic_heatmap_data(
    city: str,
    traffic_service: TrafficService = Depends(get_traffic_service)
):
    """Get traffic data formatted for heatmap visualization."""
    try:
        heatmap_data = await traffic_service.get_heatmap_data(city)
        return heatmap_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
