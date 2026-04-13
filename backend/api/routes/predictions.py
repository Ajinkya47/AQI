"""
ML Prediction API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from datetime import datetime

from backend.api.dependencies import (
    get_predictor,
    get_aqi_service,
    get_weather_service,
    get_alert_service
)
from backend.ml.predictor import AQIPredictor
from backend.services.aqi_service import AQIService
from backend.services.weather_service import WeatherService
from backend.services.alert_service import AlertService
from backend.models.schemas import (
    PredictionResponse,
    PredictionInput,
    AlertResponse,
    BestTimeResponse
)

router = APIRouter()


@router.get("/{city}", response_model=PredictionResponse)
async def get_aqi_prediction(
    city: str,
    predictor: AQIPredictor = Depends(get_predictor),
    aqi_service: AQIService = Depends(get_aqi_service),
    weather_service: WeatherService = Depends(get_weather_service)
):
    """
    Get AQI predictions for the next 2-4 hours.
    
    Uses current conditions to predict future air quality.
    """
    try:
        # Get current data
        current_aqi = await aqi_service.get_current_aqi(city)
        weather = await weather_service.get_current_weather(city)
        
        # Prepare prediction input
        prediction_input = PredictionInput(
            temperature=weather.get("temperature", 25),
            humidity=weather.get("humidity", 50),
            wind_speed=weather.get("wind_speed", 5),
            hour=datetime.now().hour,
            day_of_week=datetime.now().weekday(),
            current_aqi=current_aqi["aqi"]
        )
        
        # Get predictions
        predictions = predictor.predict(prediction_input)
        
        return PredictionResponse(
            city=city,
            current_aqi=current_aqi["aqi"],
            current_category=current_aqi["category"],
            predicted_2hr=predictions["aqi_2hr"],
            predicted_4hr=predictions["aqi_4hr"],
            category_2hr=predictions["category_2hr"],
            category_4hr=predictions["category_4hr"],
            trend=predictions["trend"],
            confidence=predictions["confidence"],
            timestamp=datetime.utcnow()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{city}/alerts", response_model=List[AlertResponse])
async def get_pollution_alerts(
    city: str,
    predictor: AQIPredictor = Depends(get_predictor),
    aqi_service: AQIService = Depends(get_aqi_service),
    weather_service: WeatherService = Depends(get_weather_service),
    alert_service: AlertService = Depends(get_alert_service)
):
    """
    Get pollution alerts and warnings for a city.
    
    Includes current alerts and predicted future warnings.
    """
    try:
        # Get current and predicted AQI
        current_aqi = await aqi_service.get_current_aqi(city)
        weather = await weather_service.get_current_weather(city)
        
        prediction_input = PredictionInput(
            temperature=weather.get("temperature", 25),
            humidity=weather.get("humidity", 50),
            wind_speed=weather.get("wind_speed", 5),
            hour=datetime.now().hour,
            day_of_week=datetime.now().weekday(),
            current_aqi=current_aqi["aqi"]
        )
        
        predictions = predictor.predict(prediction_input)
        
        # Generate alerts
        alerts = alert_service.generate_alerts(
            city=city,
            current_aqi=current_aqi["aqi"],
            predicted_2hr=predictions["aqi_2hr"],
            predicted_4hr=predictions["aqi_4hr"]
        )
        
        return alerts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{city}/best-time", response_model=BestTimeResponse)
async def get_best_travel_time(
    city: str,
    predictor: AQIPredictor = Depends(get_predictor),
    aqi_service: AQIService = Depends(get_aqi_service),
    weather_service: WeatherService = Depends(get_weather_service)
):
    """
    Get the best time to travel based on predicted AQI.
    
    Analyzes the next 12 hours and recommends optimal windows.
    """
    try:
        current_aqi = await aqi_service.get_current_aqi(city)
        weather = await weather_service.get_current_weather(city)
        
        # Get predictions for next 12 hours
        best_times = predictor.find_best_travel_times(
            current_aqi=current_aqi["aqi"],
            temperature=weather.get("temperature", 25),
            humidity=weather.get("humidity", 50),
            wind_speed=weather.get("wind_speed", 5)
        )
        
        return BestTimeResponse(
            city=city,
            current_aqi=current_aqi["aqi"],
            recommendations=best_times
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
