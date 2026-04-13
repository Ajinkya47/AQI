"""
Tests for prediction service and ML model.
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.ml.predictor import AQIPredictor
from backend.models.schemas import PredictionInput


client = TestClient(app)


class TestPredictionEndpoints:
    """Test prediction API endpoints."""
    
    def test_get_prediction(self):
        """Test getting AQI prediction."""
        response = client.get("/api/predictions/pune")
        assert response.status_code == 200
        data = response.json()
        assert "current_aqi" in data
        assert "predicted_2hr" in data
        assert "predicted_4hr" in data
        assert "trend" in data
    
    def test_get_alerts(self):
        """Test getting pollution alerts."""
        response = client.get("/api/predictions/pune/alerts")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if data:
            assert "alert_type" in data[0]
            assert "message" in data[0]
    
    def test_get_best_time(self):
        """Test getting best travel time."""
        response = client.get("/api/predictions/pune/best-time")
        assert response.status_code == 200
        data = response.json()
        assert "recommendations" in data
        assert len(data["recommendations"]) > 0


class TestAQIPredictor:
    """Test AQI predictor functionality."""
    
    @pytest.fixture
    def predictor(self):
        return AQIPredictor()
    
    def test_predict_returns_valid_structure(self, predictor):
        """Test that predict returns correct structure."""
        input_data = PredictionInput(
            temperature=25.0,
            humidity=60.0,
            wind_speed=5.0,
            hour=10,
            day_of_week=1,
            current_aqi=100
        )
        
        result = predictor.predict(input_data)
        
        assert "aqi_2hr" in result
        assert "aqi_4hr" in result
        assert "category_2hr" in result
        assert "category_4hr" in result
        assert "trend" in result
        assert "confidence" in result
    
    def test_predict_values_in_range(self, predictor):
        """Test that predictions are within valid range."""
        input_data = PredictionInput(
            temperature=30.0,
            humidity=70.0,
            wind_speed=3.0,
            hour=18,
            day_of_week=0,
            current_aqi=150
        )
        
        result = predictor.predict(input_data)
        
        assert 0 <= result["aqi_2hr"] <= 500
        assert 0 <= result["aqi_4hr"] <= 500
        assert 0 <= result["confidence"] <= 1
    
    def test_category_mapping(self, predictor):
        """Test AQI category mapping."""
        assert predictor._get_category(30) == "Good"
        assert predictor._get_category(75) == "Moderate"
        assert predictor._get_category(125) == "Unhealthy for Sensitive Groups"
        assert predictor._get_category(175) == "Unhealthy"
        assert predictor._get_category(250) == "Very Unhealthy"
        assert predictor._get_category(350) == "Hazardous"
    
    def test_find_best_travel_times(self, predictor):
        """Test finding best travel times."""
        recommendations = predictor.find_best_travel_times(
            current_aqi=120,
            temperature=28.0,
            humidity=55.0,
            wind_speed=6.0
        )
        
        assert len(recommendations) >= 2
        for rec in recommendations:
            assert rec.time_slot
            assert rec.expected_aqi >= 0
            assert rec.recommendation
