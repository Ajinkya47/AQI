"""
Script to train the AQI prediction model.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
from pathlib import Path
import random
from datetime import datetime, timedelta


def generate_synthetic_data(num_samples: int = 10000) -> pd.DataFrame:
    """
    Generate synthetic training data for AQI prediction.
    
    In production, replace this with real historical data.
    """
    data = []
    
    for _ in range(num_samples):
        # Generate random features
        temperature = random.uniform(10, 45)  # Celsius
        humidity = random.uniform(20, 95)  # Percent
        wind_speed = random.uniform(0, 25)  # m/s
        hour = random.randint(0, 23)
        day_of_week = random.randint(0, 6)
        
        # Base AQI calculation (simplified model)
        base_aqi = 80
        
        # Temperature effect (extreme temps = higher pollution)
        if temperature > 35 or temperature < 15:
            base_aqi += 20
        
        # Humidity effect (high humidity traps pollutants)
        base_aqi += (humidity - 50) * 0.5
        
        # Wind effect (higher wind = lower pollution)
        base_aqi -= wind_speed * 3
        
        # Hour effect (rush hours have higher pollution)
        if 8 <= hour <= 10 or 17 <= hour <= 20:
            base_aqi += 30
        elif 11 <= hour <= 16:
            base_aqi += 10
        elif 0 <= hour <= 5:
            base_aqi -= 15
        
        # Weekend effect (less traffic)
        if day_of_week >= 5:
            base_aqi -= 15
        
        # Add noise
        current_aqi = max(20, min(400, base_aqi + random.uniform(-30, 30)))
        
        # Future AQI (2 hours ahead)
        future_hour = (hour + 2) % 24
        future_base = current_aqi
        
        # Rush hour transition
        if 8 <= future_hour <= 10 or 17 <= future_hour <= 20:
            future_base += 15
        elif 0 <= future_hour <= 5:
            future_base -= 10
        
        future_aqi = max(20, min(400, future_base + random.uniform(-20, 20)))
        
        data.append({
            "temperature": temperature,
            "humidity": humidity,
            "wind_speed": wind_speed,
            "hour": hour,
            "day_of_week": day_of_week,
            "current_aqi": current_aqi,
            "future_aqi_2hr": future_aqi
        })
    
    return pd.DataFrame(data)


def train_model():
    """Train and save the AQI prediction model."""
    print("🚀 Starting model training...")
    
    # Generate or load training data
    print("📊 Generating synthetic training data...")
    df = generate_synthetic_data(10000)
    
    # Prepare features and target
    feature_columns = [
        "temperature", "humidity", "wind_speed",
        "hour", "day_of_week", "current_aqi"
    ]
    
    X = df[feature_columns]
    y = df["future_aqi_2hr"]
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    print(f"📈 Training samples: {len(X_train)}")
    print(f"📉 Testing samples: {len(X_test)}")
    
    # Train Random Forest model
    print("🌲 Training Random Forest model...")
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=15,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    print(f"\n📊 Model Performance:")
    print(f"   Mean Absolute Error: {mae:.2f}")
    print(f"   R² Score: {r2:.4f}")
    
    # Feature importance
    print(f"\n🔍 Feature Importance:")
    importance = dict(zip(feature_columns, model.feature_importances_))
    for feature, imp in sorted(importance.items(), key=lambda x: x[1], reverse=True):
        print(f"   {feature}: {imp:.4f}")
    
    # Save model
    model_dir = Path("backend/ml/models")
    model_dir.mkdir(parents=True, exist_ok=True)
    
    model_path = model_dir / "aqi_model.joblib"
    joblib.dump(model, model_path)
    
    print(f"\n✅ Model saved to {model_path}")
    
    # Save sample data for reference
    sample_data_path = Path("data/sample_aqi.csv")
    sample_data_path.parent.mkdir(parents=True, exist_ok=True)
    df.head(1000).to_csv(sample_data_path, index=False)
    print(f"📁 Sample data saved to {sample_data_path}")
    
    return model


if __name__ == "__main__":
    train_model()
