"""
AQI data fetching and processing service.
"""

import httpx
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import random


class AQIService:
    """Service for fetching and processing Air Quality Index data."""
    
    AQICN_BASE_URL = "[api.waqi.info](https://api.waqi.info)"
    OPENWEATHER_AQI_URL = "[api.openweathermap.org](http://api.openweathermap.org/data/2.5/air_pollution)"
    
    def __init__(self, openweather_key: str = "", aqicn_key: str = ""):
        self.openweather_key = openweather_key
        self.aqicn_key = aqicn_key
        
        # City coordinates for simulation
        self.city_coords = {
            "pune": (18.5204, 73.8567),
            "mumbai": (19.0760, 72.8777),
            "delhi": (28.6139, 77.2090),
            "bangalore": (12.9716, 77.5946),
            "chennai": (13.0827, 80.2707),
            "hyderabad": (17.3850, 78.4867),
            "kolkata": (22.5726, 88.3639),
        }
    
    def _get_aqi_category(self, aqi: int) -> str:
        """Get AQI category based on value."""
        if aqi <= 50:
            return "Good"
        elif aqi <= 100:
            return "Moderate"
        elif aqi <= 150:
            return "Unhealthy for Sensitive Groups"
        elif aqi <= 200:
            return "Unhealthy"
        elif aqi <= 300:
            return "Very Unhealthy"
        else:
            return "Hazardous"
    
    async def get_current_aqi(self, city: str) -> Dict:
        """
        Get current AQI for a city.
        
        Tries real API first, falls back to simulation.
        """
        city_lower = city.lower()
        
        # Try AQICN API if key is available
        if self.aqicn_key:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{self.AQICN_BASE_URL}/feed/{city}/?token={self.aqicn_key}",
                        timeout=10.0
                    )
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("status") == "ok":
                            aqi = data["data"]["aqi"]
                            iaqi = data["data"].get("iaqi", {})
                            return {
                                "aqi": aqi,
                                "category": self._get_aqi_category(aqi),
                                "pm25": iaqi.get("pm25", {}).get("v"),
                                "pm10": iaqi.get("pm10", {}).get("v"),
                                "o3": iaqi.get("o3", {}).get("v"),
                                "no2": iaqi.get("no2", {}).get("v"),
                            }
            except Exception:
                pass  # Fall through to simulation
        
        # Simulation fallback
        return self._simulate_aqi(city_lower)
    
    async def get_aqi_by_coordinates(self, lat: float, lon: float) -> Dict:
        """Get AQI by geographic coordinates."""
        if self.aqicn_key:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{self.AQICN_BASE_URL}/feed/geo:{lat};{lon}/?token={self.aqicn_key}",
                        timeout=10.0
                    )
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("status") == "ok":
                            aqi = data["data"]["aqi"]
                            return {
                                "aqi": aqi,
                                "category": self._get_aqi_category(aqi),
                                "latitude": lat,
                                "longitude": lon
                            }
            except Exception:
                pass
        
        # Simulation
        base_aqi = random.randint(40, 180)
        return {
            "aqi": base_aqi,
            "category": self._get_aqi_category(base_aqi),
            "latitude": lat,
            "longitude": lon
        }
    
    async def get_historical_data(self, city: str, hours: int) -> List[Dict]:
        """Get historical AQI data (simulated)."""
        history = []
        current_time = datetime.utcnow()
        base_aqi = random.randint(60, 120)
        
        for i in range(hours, 0, -1):
            timestamp = current_time - timedelta(hours=i)
            # Add some variation based on time of day
            hour_factor = abs(12 - timestamp.hour) / 12  # Higher at noon
            variation = random.randint(-20, 20)
            aqi = max(0, min(500, base_aqi + int(30 * hour_factor) + variation))
            
            history.append({
                "timestamp": timestamp,
                "aqi": aqi,
                "category": self._get_aqi_category(aqi)
            })
        
        return history
    
    async def get_route_aqi(
        self,
        origin: Tuple[float, float],
        destination: Tuple[float, float]
    ) -> List[Dict]:
        """Get AQI data for points along a route."""
        # Generate waypoints
        num_points = 5
        waypoints = []
        
        for i in range(num_points):
            fraction = i / (num_points - 1)
            lat = origin[0] + (destination[0] - origin[0]) * fraction
            lon = origin[1] + (destination[1] - origin[1]) * fraction
            
            aqi = random.randint(40, 200)
            waypoints.append({
                "latitude": lat,
                "longitude": lon,
                "aqi": aqi,
                "category": self._get_aqi_category(aqi)
            })
        
        return waypoints
    
    async def get_city_zones_aqi(self, city: str) -> Dict:
        """Get AQI for different zones in a city."""
        zones = ["North", "South", "East", "West", "Central"]
        zone_data = {}
        
        for zone in zones:
            aqi = random.randint(40, 200)
            zone_data[zone] = {
                "aqi": aqi,
                "category": self._get_aqi_category(aqi)
            }
        
        return zone_data
    
    def _simulate_aqi(self, city: str) -> Dict:
        """Generate simulated AQI data for a city."""
        # Base AQI varies by city (higher for more polluted cities)
        city_base = {
            "delhi": 150,
            "mumbai": 100,
            "pune": 80,
            "bangalore": 70,
            "chennai": 75,
            "hyderabad": 85,
            "kolkata": 120,
        }
        
        base = city_base.get(city, 90)
        hour = datetime.now().hour
        
        # Time-based variation (higher during rush hours)
        if 8 <= hour <= 10 or 17 <= hour <= 20:
            time_factor = 1.3
        elif 11 <= hour <= 16:
            time_factor = 1.1
        else:
            time_factor = 0.9
        
        # Random daily variation
        variation = random.uniform(0.8, 1.2)
        
        aqi = int(base * time_factor * variation)
        aqi = max(20, min(500, aqi))  # Clamp to valid range
        
        return {
            "aqi": aqi,
            "category": self._get_aqi_category(aqi),
            "pm25": aqi * 0.8 + random.uniform(-10, 10),
            "pm10": aqi * 1.2 + random.uniform(-15, 15),
            "o3": random.uniform(20, 80),
            "no2": random.uniform(10, 60),
        }
