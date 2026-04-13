"""
Tests for AQI service and endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.services.aqi_service import AQIService


client = TestClient(app)


class TestAQIEndpoints:
    """Test AQI API endpoints."""
    
    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_get_aqi_valid_city(self):
        """Test getting AQI for a valid city."""
        response = client.get("/api/aqi/pune")
        assert response.status_code == 200
        data = response.json()
        assert "aqi" in data
        assert "category" in data
        assert data["city"] == "pune"
        assert 0 <= data["aqi"] <= 500
    
    def test_get_aqi_invalid_city(self):
        """Test getting AQI for an invalid city."""
        response = client.get("/api/aqi/invalidcityname123")
        # Should still return data (simulated)
        assert response.status_code == 200
    
    def test_get_aqi_by_coordinates(self):
        """Test getting AQI by coordinates."""
        response = client.get("/api/aqi/location/coordinates?lat=18.5204&lon=73.8567")
        assert response.status_code == 200
        data = response.json()
        assert "aqi" in data
    
    def test_get_aqi_history(self):
        """Test getting AQI history."""
        response = client.get("/api/aqi/pune/history?hours=24")
        assert response.status_code == 200
        data = response.json()
        assert data["city"] == "pune"
        assert data["hours"] == 24
        assert len(data["data"]) > 0


class TestAQIService:
    """Test AQI service functionality."""
    
    @pytest.fixture
    def aqi_service(self):
        return AQIService()
    
    def test_get_aqi_category_good(self, aqi_service):
        """Test AQI category for good air quality."""
        category = aqi_service._get_aqi_category(30)
        assert category == "Good"
    
    def test_get_aqi_category_moderate(self, aqi_service):
        """Test AQI category for moderate air quality."""
        category = aqi_service._get_aqi_category(75)
        assert category == "Moderate"
    
    def test_get_aqi_category_unhealthy(self, aqi_service):
        """Test AQI category for unhealthy air quality."""
        category = aqi_service._get_aqi_category(175)
        assert category == "Unhealthy"
    
    def test_get_aqi_category_hazardous(self, aqi_service):
        """Test AQI category for hazardous air quality."""
        category = aqi_service._get_aqi_category(350)
        assert category == "Hazardous"
    
    @pytest.mark.asyncio
    async def test_simulate_aqi(self, aqi_service):
        """Test AQI simulation."""
        data = aqi_service._simulate_aqi("pune")
        assert "aqi" in data
        assert "category" in data
        assert "pm25" in data
        assert 0 <= data["aqi"] <= 500
