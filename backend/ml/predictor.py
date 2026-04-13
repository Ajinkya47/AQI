"""
AQI prediction model.
"""

import numpy as np
import joblib
from pathlib import Path
from datetime import datetime
from typing import Dict, List

from backend.models.schemas import PredictionInput, TrendDirection, TimeRecommendation


class AQIPredictor:
    """Machine learning model for AQI prediction."""
    
    def __init__(self, model_path: str = "backend/ml/models/aqi_model.joblib"):
        self.model_path = Path(model_path)
        self.model = None
        self.feature_names = [
            "temperature", "humidity", "wind_speed",
            "hour", "day_of_week", "current_aqi"
        ]
        self._load_model()
    
    def _load_model(self):
        """Load the trained model if it exists."""
        if self.model_path.exists():
            try:
                self.model = joblib.load(self.model_path)
                print(f"✅ Model loaded from {self.model_path}")
            except Exception as e:
                print(f"⚠️ Could not load model: {e}")
                self.model = None
        else:
            print(f"⚠️ Model not found at {self.model_path}, using simulation")
    
    def _get_category(self, aqi: int) -> str:
        """Get AQI category from value."""
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
    
    def _get_trend(self, current: int, future: int) -> TrendDirection:
        """Determine trend direction."""
        diff = future - current
        if diff > 20:
            return TrendDirection.WORSENING
        elif diff < -20:
            return TrendDirection.IMPROVING
        else:
            return TrendDirection.STABLE
    
    def predict(self, input_data: PredictionInput) -> Dict:
        """
        Predict AQI for the next 2-4 hours.
        
        Uses trained model if available, otherwise uses heuristics.
        """
        if self.model is not None:
            return self._predict_with_model(input_data)
        else:
            return self._predict_heuristic(input_data)
    
    def _predict_with_model(self, input_data: PredictionInput) -> Dict:
        """Make prediction using trained ML model."""
        # Prepare features for 2-hour prediction
        features_2hr = np.array([[
            input_data.temperature,
            input_data.humidity,
            input_data.wind_speed,
            (input_data.hour + 2) % 24,
            input_data.day_of_week,
            input_data.current_aqi
        ]])
        
        # Prepare features for 4-hour prediction
        features_4hr = np.array([[
            input_data.temperature,
            input_data.humidity,
            input_data.wind_speed,
            (input_data.hour + 4) % 24,
            input_data.day_of_week,
            input_data.current_aqi
        ]])
        
        # Make predictions
        pred_2hr = int(self.model.predict(features_2hr)[0])
        pred_4hr = int(self.model.predict(features_4hr)[0])
        
        # Clamp to valid range
        pred_2hr = max(0, min(500, pred_2hr))
        pred_4hr = max(0, min(500, pred_4hr))
        
        # Calculate confidence (higher if model has been trained)
        confidence = 0.75  # Base confidence for trained model
        
        return {
            "aqi_2hr": pred_2hr,
            "aqi_4hr": pred_4hr,
            "category_2hr": self._get_category(pred_2hr),
            "category_4hr": self._get_category(pred_4hr),
            "trend": self._get_trend(input_data.current_aqi, pred_4hr),
            "confidence": confidence
        }
    
    def _predict_heuristic(self, input_data: PredictionInput) -> Dict:
        """Make prediction using heuristics when no model is available."""
        current = input_data.current_aqi
        hour = input_data.hour
        
        # Time-based factors
        # Rush hours typically have higher pollution
        rush_hour_factor = 0
        if 8 <= hour <= 10 or 17 <= hour <= 20:
            rush_hour_factor = 15
        elif 11 <= hour <= 16:
            rush_hour_factor = 5
        else:
            rush_hour_factor = -10
        
        # Weather factors
        # Higher wind = lower AQI (disperses pollutants)
        wind_factor = -input_data.wind_speed * 2
        
        # Higher humidity can trap pollutants
        humidity_factor = (input_data.humidity - 50) * 0.3
        
        # Temperature factor (inversions at certain temps)
        temp_factor = 0
        if input_data.temperature < 15:
            temp_factor = 10  # Cold inversions trap pollution
        
        # Calculate predictions
        hour_2 = (hour + 2) % 24
        hour_4 = (hour + 4) % 24
        
        # Rush hour factor for future hours
        rush_2hr = 15 if (8 <= hour_2 <= 10 or 17 <= hour_2 <= 20) else -5
        rush_4hr = 15 if (8 <= hour_4 <= 10 or 17 <= hour_4 <= 20) else -5
        
        pred_2hr = current + rush_2hr + wind_factor + humidity_factor + temp_factor
        pred_4hr = current + rush_4hr + wind_factor + humidity_factor + temp_factor
        
        # Add some random variation
        pred_2hr += np.random.randint(-10, 10)
        pred_4hr += np.random.randint(-15, 15)
        
        # Clamp to valid range
        pred_2hr = int(max(20, min(400, pred_2hr)))
        pred_4hr = int(max(20, min(400, pred_4hr)))
        
        return {
            "aqi_2hr": pred_2hr,
            "aqi_4hr": pred_4hr,
            "category_2hr": self._get_category(pred_2hr),
            "category_4hr": self._get_category(pred_4hr),
            "trend": self._get_trend(current, pred_4hr),
            "confidence": 0.5  # Lower confidence for heuristic
        }
    
    def find_best_travel_times(
        self,
        current_aqi: int,
        temperature: float,
        humidity: float,
        wind_speed: float
    ) -> List[TimeRecommendation]:
        """Find the best times to travel in the next 12 hours."""
        recommendations = []
        current_hour = datetime.now().hour
        day_of_week = datetime.now().weekday()
        
        hourly_predictions = []
        
        for i in range(12):
            target_hour = (current_hour + i) % 24
            
            input_data = PredictionInput(
                temperature=temperature,
                humidity=humidity,
                wind_speed=wind_speed,
                hour=target_hour,
                day_of_week=day_of_week,
                current_aqi=current_aqi
            )
            
            prediction = self.predict(input_data)
            predicted_aqi = prediction["aqi_2hr"] if i <= 2 else prediction["aqi_4hr"]
            
            hourly_predictions.append({
                "hour": target_hour,
                "hours_from_now": i,
                "aqi": predicted_aqi,
                "category": self._get_category(predicted_aqi)
            })
        
        # Sort by predicted AQI to find best times
        sorted_predictions = sorted(hourly_predictions, key=lambda x: x["aqi"])
        
        # Best time
        best = sorted_predictions[0]
        recommendations.append(TimeRecommendation(
            time_slot=self._format_time_slot(best["hour"]),
            expected_aqi=best["aqi"],
            category=best["category"],
            recommendation=f"Best time to travel - lowest predicted AQI in {best['hours_from_now']} hours"
        ))
        
        # Second best
        if len(sorted_predictions) > 1:
            second = sorted_predictions[1]
            recommendations.append(TimeRecommendation(
                time_slot=self._format_time_slot(second["hour"]),
                expected_aqi=second["aqi"],
                category=second["category"],
                recommendation=f"Second best option in {second['hours_from_now']} hours"
            ))
        
        # Worst time to avoid
        worst = sorted_predictions[-1]
        recommendations.append(TimeRecommendation(
            time_slot=self._format_time_slot(worst["hour"]),
            expected_aqi=worst["aqi"],
            category=worst["category"],
            recommendation=f"Avoid traveling at this time - highest predicted pollution"
        ))
        
        # Current time assessment
        current_pred = hourly_predictions[0]
        if current_pred["aqi"] <= best["aqi"] + 20:
            recommendations.insert(0, TimeRecommendation(
                time_slot="Now",
                expected_aqi=current_aqi,
                category=self._get_category(current_aqi),
                recommendation="Current conditions are good for travel"
            ))
        
        return recommendations
    
    def _format_time_slot(self, hour: int) -> str:
        """Format hour as readable time slot."""
        if hour == 0:
            return "12:00 AM"
        elif hour < 12:
            return f"{hour}:00 AM"
        elif hour == 12:
            return "12:00 PM"
        else:
            return f"{hour-12}:00 PM"
