"""
Traffic data service.
"""

import httpx
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import random
import math

from backend.models.schemas import CongestionLevel, TrafficPoint, TrafficResponse


class TrafficService:
    """Service for fetching and processing traffic data."""
    
    GOOGLE_DIRECTIONS_URL = "[maps.googleapis.com](https://maps.googleapis.com/maps/api/directions/json)"
    
    def __init__(self, google_maps_key: str = ""):
        self.google_maps_key = google_maps_key
        
        # Major city centers
        self.city_centers = {
            "pune": (18.5204, 73.8567),
            "mumbai": (19.0760, 72.8777),
            "delhi": (28.6139, 77.2090),
            "bangalore": (12.9716, 77.5946),
        }
    
    def _get_congestion_level(self, score: float) -> CongestionLevel:
        """Convert congestion score to level."""
        if score < 0.25:
            return CongestionLevel.LOW
        elif score < 0.5:
            return CongestionLevel.MODERATE
        elif score < 0.75:
            return CongestionLevel.HIGH
        else:
            return CongestionLevel.SEVERE
    
    async def get_city_traffic(self, city: str) -> TrafficResponse:
        """Get overall traffic conditions for a city."""
        city_lower = city.lower()
        center = self.city_centers.get(city_lower, (18.5204, 73.8567))
        
        # Simulate traffic based on time
        hour = datetime.now().hour
        day = datetime.now().weekday()
        
        # Rush hour factor
        if day < 5:  # Weekday
            if 8 <= hour <= 10 or 17 <= hour <= 20:
                base_congestion = 0.7
            elif 11 <= hour <= 16:
                base_congestion = 0.4
            else:
                base_congestion = 0.2
        else:  # Weekend
            if 10 <= hour <= 14 or 17 <= hour <= 21:
                base_congestion = 0.5
            else:
                base_congestion = 0.25
        
        # Generate hotspots
        hotspots = self._generate_hotspots(center, base_congestion)
        
        overall = base_congestion + random.uniform(-0.1, 0.1)
        overall = max(0, min(1, overall))
        
        return TrafficResponse(
            city=city,
            overall_congestion=self._get_congestion_level(overall),
            hotspots=hotspots,
            average_speed_kmh=max(10, 60 - (overall * 50)),
            timestamp=datetime.utcnow()
        )
    
    async def get_route_traffic(
        self,
        origin: Tuple[float, float],
        destination: Tuple[float, float]
    ) -> Dict:
        """Get traffic conditions along a route."""
        # If we have a Google Maps key, try real API
        if self.google_maps_key:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        self.GOOGLE_DIRECTIONS_URL,
                        params={
                            "origin": f"{origin[0]},{origin[1]}",
                            "destination": f"{destination[0]},{destination[1]}",
                            "departure_time": "now",
                            "traffic_model": "best_guess",
                            "key": self.google_maps_key
                        },
                        timeout=10.0
                    )
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("status") == "OK":
                            return self._parse_google_traffic(data)
            except Exception:
                pass
        
        # Simulation fallback
        return self._simulate_route_traffic(origin, destination)
    
    async def get_hotspots(self, city: str, limit: int) -> List[TrafficPoint]:
        """Get traffic hotspots for a city."""
        traffic_data = await self.get_city_traffic(city)
        hotspots = sorted(
            traffic_data.hotspots,
            key=lambda x: x.delay_minutes or 0,
            reverse=True
        )
        return hotspots[:limit]
    
    async def get_heatmap_data(self, city: str) -> Dict:
        """Get traffic data formatted for heatmap visualization."""
        city_lower = city.lower()
        center = self.city_centers.get(city_lower, (18.5204, 73.8567))
        
        # Generate grid of points
        grid_size = 20
        radius = 0.1  # degrees
        
        points = []
        for i in range(grid_size):
            for j in range(grid_size):
                lat = center[0] - radius + (2 * radius * i / grid_size)
                lon = center[1] - radius + (2 * radius * j / grid_size)
                
                # Congestion based on distance from center and random factor
                dist = math.sqrt((lat - center[0])**2 + (lon - center[1])**2)
                congestion = max(0.1, 0.8 - dist * 5 + random.uniform(-0.2, 0.2))
                
                points.append({
                    "lat": lat,
                    "lng": lon,
                    "intensity": min(1, max(0, congestion))
                })
        
        return {
            "city": city,
            "center": {"lat": center[0], "lng": center[1]},
            "points": points
        }
    
    def _generate_hotspots(
        self,
        center: Tuple[float, float],
        base_congestion: float
    ) -> List[TrafficPoint]:
        """Generate traffic hotspot data."""
        hotspots = []
        num_hotspots = random.randint(5, 10)
        
        for _ in range(num_hotspots):
            # Random location around center
            lat = center[0] + random.uniform(-0.05, 0.05)
            lon = center[1] + random.uniform(-0.05, 0.05)
            
            congestion = base_congestion + random.uniform(-0.2, 0.3)
            congestion = max(0, min(1, congestion))
            
            delay = int(congestion * 20)
            
            hotspots.append(TrafficPoint(
                latitude=lat,
                longitude=lon,
                congestion_level=self._get_congestion_level(congestion),
                delay_minutes=delay,
                description=self._get_traffic_description(congestion)
            ))
        
        return hotspots
    
    def _get_traffic_description(self, congestion: float) -> str:
        """Get human-readable traffic description."""
        if congestion < 0.25:
            return "Traffic flowing smoothly"
        elif congestion < 0.5:
            return "Moderate traffic, slight delays possible"
        elif congestion < 0.75:
            return "Heavy traffic, expect delays"
        else:
            return "Severe congestion, major delays"
    
    def _simulate_route_traffic(
        self,
        origin: Tuple[float, float],
        destination: Tuple[float, float]
    ) -> Dict:
        """Simulate traffic data for a route."""
        # Calculate approximate distance
        distance = math.sqrt(
            (destination[0] - origin[0])**2 +
            (destination[1] - origin[1])**2
        ) * 111  # km per degree
        
        hour = datetime.now().hour
        if 8 <= hour <= 10 or 17 <= hour <= 20:
            speed = 25
        elif 11 <= hour <= 16:
            speed = 35
        else:
            speed = 45
        
        duration = (distance / speed) * 60  # minutes
        duration_in_traffic = duration * random.uniform(1.0, 1.5)
        
        return {
            "distance_km": round(distance, 2),
            "duration_minutes": round(duration, 1),
            "duration_in_traffic_minutes": round(duration_in_traffic, 1),
            "delay_minutes": round(duration_in_traffic - duration, 1),
            "average_speed_kmh": speed
        }
    
    def _parse_google_traffic(self, data: Dict) -> Dict:
        """Parse Google Directions API response."""
        route = data["routes"][0]["legs"][0]
        return {
            "distance_km": route["distance"]["value"] / 1000,
            "duration_minutes": route["duration"]["value"] / 60,
            "duration_in_traffic_minutes": route.get(
                "duration_in_traffic", route["duration"]
            )["value"] / 60,
        }
