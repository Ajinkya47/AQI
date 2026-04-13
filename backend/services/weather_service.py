"""
Weather data service.
"""

import httpx
from typing import Dict, Optional
from datetime import datetime
import random


class WeatherService:
    """Service for fetching weather data."""
    
    OPENWEATHER_URL = "[api.openweathermap.org](https://api.openweathermap.org/data/2.5/weather)"
    
    def __init__(self, api_key: str = ""):
        self.api_key = api_key
        
        # City coordinates
        self.city_coords = {
            "pune": (18.5204, 73.8567),
            "mumbai": (19.0760, 72.8777),
            "delhi": (28.6139, 77.2090),
            "bangalore": (12.9716, 77.5946),
            "chennai": (13.0827, 80.2707),
            "hyderabad": (17.3850, 78.4867),
            "kolkata": (22.5726, 88.3639),
        }
    
    async def get_current_weather(self, city: str) -> Dict:
        """
        Get current weather for a city.
        
        Uses OpenWeather API if key is available, otherwise simulates.
        """
        if self.api_key:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        self.OPENWEATHER_URL,
                        params={
                            "q": city,
                            "appid": self.api_key,
                            "units": "metric"
                        },
                        timeout=10.0
                    )
                    if response.status_code == 200:
                        data = response.json()
                        return {
                            "temperature": data["main"]["temp"],
                            "humidity": data["main"]["humidity"],
                            "wind_speed": data["wind"]["speed"],
                            "description": data["weather"][0]["description"],
                            "pressure": data["main"]["pressure"],
                            "visibility": data.get("visibility", 10000) / 1000
                        }
            except Exception:
                pass
        
        # Simulation fallback
        return self._simulate_weather(city)
    
    async def get_weather_by_coordinates(
        self,
        lat: float,
        lon: float
    ) -> Dict:
        """Get weather by coordinates."""
        if self.api_key:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        self.OPENWEATHER_URL,
                        params={
                            "lat": lat,
                            "lon": lon,
                            "appid": self.api_key,
                            "units": "metric"
                        },
                        timeout=10.0
                    )
                    if response.status_code == 200:
                        data = response.json()
                        return {
                            "temperature": data["main"]["temp"],
                            "humidity": data["main"]["humidity"],
                            "wind_speed": data["wind"]["speed"],
                        }
            except Exception:
                pass
        
        # Simulation
        return self._simulate_weather("default")
    
    async def get_forecast(self, city: str, hours: int = 24) -> list:
        """Get weather forecast (simulated)."""
        forecast = []
        current = self._simulate_weather(city)
        
        for i in range(hours):
            # Add some variation over time
            temp_change = random.uniform(-2, 2) * (i / 24)
            humidity_change = random.uniform(-5, 5)
            
            forecast.append({
                "hour": i,
                "temperature": current["temperature"] + temp_change,
                "humidity": max(20, min(100, current["humidity"] + humidity_change)),
                "wind_speed": max(0, current["wind_speed"] + random.uniform(-1, 1))
            })
        
        return forecast
    
    def _simulate_weather(self, city: str) -> Dict:
        """Generate simulated weather data."""
        month = datetime.now().month
        hour = datetime.now().hour
        
        # Seasonal base temperature (India)
        if month in [12, 1, 2]:  # Winter
            base_temp = 20
        elif month in [3, 4, 5]:  # Summer
            base_temp = 35
        elif month in [6, 7, 8, 9]:  # Monsoon
            base_temp = 28
        else:  # Post-monsoon
            base_temp = 25
        
        # City-specific adjustment
        city_temp_adj = {
            "delhi": 3,
            "mumbai": -2,
            "pune": -3,
            "bangalore": -5,
            "chennai": 2,
        }
        base_temp += city_temp_adj.get(city.lower(), 0)
        
        # Diurnal variation
        if 6 <= hour <= 10:
            temp = base_temp - 3
        elif 11 <= hour <= 15:
            temp = base_temp + 3
        elif 16 <= hour <= 19:
            temp = base_temp + 1
        else:
            temp = base_temp - 5
        
        temp += random.uniform(-2, 2)
        
        # Humidity based on season
        if month in [6, 7, 8, 9]:  # Monsoon
            humidity = random.uniform(70, 95)
        elif month in [12, 1, 2]:  # Winter
            humidity = random.uniform(40, 60)
        else:
            humidity = random.uniform(50, 75)
        
        return {
            "temperature": round(temp, 1),
            "humidity": round(humidity, 1),
            "wind_speed": round(random.uniform(2, 15), 1),
            "description": self._get_weather_description(temp, humidity),
            "pressure": round(random.uniform(1005, 1020), 0),
            "visibility": round(random.uniform(5, 15), 1)
        }
    
    def _get_weather_description(self, temp: float, humidity: float) -> str:
        """Generate weather description."""
        if humidity > 85:
            return "rainy"
        elif humidity > 70:
            return "cloudy"
        elif temp > 35:
            return "hot and sunny"
        elif temp > 25:
            return "warm and clear"
        elif temp > 15:
            return "pleasant"
        else:
            return "cool"
