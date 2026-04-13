"""
Route optimization API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List

from backend.api.dependencies import (
    get_route_optimizer,
    get_aqi_service,
    get_traffic_service
)
from backend.ml.route_optimizer import RouteOptimizer
from backend.services.aqi_service import AQIService
from backend.services.traffic_service import TrafficService
from backend.models.schemas import (
    RouteRequest,
    RouteResponse,
    OptimizedRoute,
    RouteComparison
)

router = APIRouter()


@router.post("/optimize", response_model=RouteResponse)
async def optimize_route(
    request: RouteRequest,
    route_optimizer: RouteOptimizer = Depends(get_route_optimizer),
    aqi_service: AQIService = Depends(get_aqi_service),
    traffic_service: TrafficService = Depends(get_traffic_service)
):
    """
    Get optimized route with lowest pollution exposure.
    
    Considers both AQI and traffic conditions to suggest the best route.
    """
    try:
        # Get AQI data for waypoints
        aqi_data = await aqi_service.get_route_aqi(
            origin=request.origin,
            destination=request.destination
        )
        
        # Get traffic data
        traffic_data = await traffic_service.get_route_traffic(
            origin=request.origin,
            destination=request.destination
        )
        
        # Optimize route
        optimized = route_optimizer.optimize(
            origin=request.origin,
            destination=request.destination,
            aqi_data=aqi_data,
            traffic_data=traffic_data,
            preference=request.preference  # 'fastest', 'cleanest', 'balanced'
        )
        
        return RouteResponse(
            origin=request.origin,
            destination=request.destination,
            recommended_route=optimized["recommended"],
            alternatives=optimized["alternatives"],
            savings=optimized["savings"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compare", response_model=RouteComparison)
async def compare_routes(
    request: RouteRequest,
    route_optimizer: RouteOptimizer = Depends(get_route_optimizer),
    aqi_service: AQIService = Depends(get_aqi_service),
    traffic_service: TrafficService = Depends(get_traffic_service)
):
    """
    Compare multiple routes based on pollution and time.
    
    Returns a comparison of all available routes.
    """
    try:
        aqi_data = await aqi_service.get_route_aqi(
            origin=request.origin,
            destination=request.destination
        )
        
        traffic_data = await traffic_service.get_route_traffic(
            origin=request.origin,
            destination=request.destination
        )
        
        comparison = route_optimizer.compare_routes(
            origin=request.origin,
            destination=request.destination,
            aqi_data=aqi_data,
            traffic_data=traffic_data
        )
        
        return comparison
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/suggestions/{city}")
async def get_route_suggestions(
    city: str,
    route_optimizer: RouteOptimizer = Depends(get_route_optimizer),
    aqi_service: AQIService = Depends(get_aqi_service)
):
    """
    Get general route suggestions for avoiding pollution in a city.
    
    Returns areas to avoid and recommended zones.
    """
    try:
        current_aqi = await aqi_service.get_city_zones_aqi(city)
        suggestions = route_optimizer.get_city_suggestions(city, current_aqi)
        return suggestions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
