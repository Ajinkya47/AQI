"""
Alert generation service.
"""

from typing import List
from datetime import datetime

from backend.config import Settings
from backend.models.schemas import AlertResponse, AlertType


class AlertService:
    """Service for generating pollution alerts."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
    
    def generate_alerts(
        self,
        city: str,
        current_aqi: int,
        predicted_2hr: int,
        predicted_4hr: int
    ) -> List[AlertResponse]:
        """Generate alerts based on current and predicted AQI values."""
        alerts = []
        
        # Current AQI alerts
        if current_aqi > self.settings.aqi_very_unhealthy:
            alerts.append(AlertResponse(
                alert_type=AlertType.CRITICAL,
                title="Critical Air Quality Alert",
                message=f"Current AQI in {city} is {current_aqi}. Air quality is hazardous. Avoid all outdoor activities.",
                aqi_value=current_aqi,
                time_frame="Now",
                actions=[
                    "Stay indoors",
                    "Keep windows and doors closed",
                    "Use air purifiers if available",
                    "Wear N95 mask if going outside is unavoidable"
                ],
                timestamp=datetime.utcnow()
            ))
        elif current_aqi > self.settings.aqi_unhealthy:
            alerts.append(AlertResponse(
                alert_type=AlertType.DANGER,
                title="Unhealthy Air Quality",
                message=f"Current AQI in {city} is {current_aqi}. Air quality is unhealthy for everyone.",
                aqi_value=current_aqi,
                time_frame="Now",
                actions=[
                    "Reduce outdoor activities",
                    "Sensitive groups should stay indoors",
                    "Consider wearing a mask outdoors"
                ],
                timestamp=datetime.utcnow()
            ))
        elif current_aqi > self.settings.aqi_unhealthy_sensitive:
            alerts.append(AlertResponse(
                alert_type=AlertType.WARNING,
                title="Moderate Air Quality Warning",
                message=f"Current AQI in {city} is {current_aqi}. Sensitive groups may experience health effects.",
                aqi_value=current_aqi,
                time_frame="Now",
                actions=[
                    "Sensitive groups should limit prolonged outdoor exertion",
                    "Consider rescheduling outdoor activities"
                ],
                timestamp=datetime.utcnow()
            ))
        
        # Predicted AQI alerts (warning about future)
        if predicted_2hr > current_aqi + 30 and predicted_2hr > self.settings.aqi_moderate:
            alerts.append(AlertResponse(
                alert_type=AlertType.WARNING,
                title="Rising Pollution Warning",
                message=f"AQI is expected to rise to {predicted_2hr} in the next 2 hours.",
                aqi_value=predicted_2hr,
                time_frame="In 2 hours",
                actions=[
                    "Plan to finish outdoor activities soon",
                    "Consider traveling before pollution rises"
                ],
                timestamp=datetime.utcnow()
            ))
        
        if predicted_4hr > self.settings.aqi_unhealthy:
            alerts.append(AlertResponse(
                alert_type=AlertType.WARNING,
                title="High Pollution Forecast",
                message=f"AQI is predicted to reach {predicted_4hr} in the next 4 hours.",
                aqi_value=predicted_4hr,
                time_frame="In 4 hours",
                actions=[
                    "Complete outdoor errands early",
                    "Postpone non-essential outdoor activities",
                    "Prepare indoor activities"
                ],
                timestamp=datetime.utcnow()
            ))
        
        # Good news alert
        if predicted_2hr < current_aqi - 20 and current_aqi > self.settings.aqi_moderate:
            alerts.append(AlertResponse(
                alert_type=AlertType.INFO,
                title="Improving Air Quality",
                message=f"Good news! AQI is expected to improve to {predicted_2hr} in the next 2 hours.",
                aqi_value=predicted_2hr,
                time_frame="In 2 hours",
                actions=[
                    "Consider delaying outdoor activities for better air quality",
                    "Monitor updates for optimal timing"
                ],
                timestamp=datetime.utcnow()
            ))
        
        # If no alerts, add info
        if not alerts:
            alerts.append(AlertResponse(
                alert_type=AlertType.INFO,
                title="Air Quality Status",
                message=f"Current AQI in {city} is {current_aqi}. Air quality is acceptable.",
                aqi_value=current_aqi,
                time_frame="Now",
                actions=[
                    "Outdoor activities are generally safe",
                    "Sensitive individuals should monitor conditions"
                ],
                timestamp=datetime.utcnow()
            ))
        
        return alerts
    
    def get_health_recommendations(self, aqi: int) -> List[str]:
        """Get health recommendations based on AQI."""
        if aqi <= 50:
            return [
                "Air quality is satisfactory",
                "Enjoy outdoor activities",
                "Ideal conditions for exercise"
            ]
        elif aqi <= 100:
            return [
                "Air quality is acceptable",
                "Unusually sensitive people should consider reducing prolonged outdoor exertion",
                "Good conditions for most outdoor activities"
            ]
        elif aqi <= 150:
            return [
                "Sensitive groups may experience health effects",
                "The general public is less likely to be affected",
                "Consider reducing prolonged outdoor exertion"
            ]
        elif aqi <= 200:
            return [
                "Everyone may begin to experience health effects",
                "Sensitive groups should avoid prolonged outdoor exertion",
                "Consider wearing a mask outdoors"
            ]
        elif aqi <= 300:
            return [
                "Health alert: significant health effects possible",
                "Everyone should avoid prolonged outdoor exertion",
                "Wear N95 mask if outdoors",
                "Use air purifiers indoors"
            ]
        else:
            return [
                "Health emergency: everyone affected",
                "Avoid all outdoor activities",
                "Stay indoors with windows closed",
                "Use air purifiers",
                "Seek medical attention if experiencing symptoms"
            ]
