"""
Database setup and session management.
"""

from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from sqlalchemy import Boolean


from backend.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False}  # SQLite specific
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class AQIRecord(Base):
    """Store historical AQI data."""
    
    __tablename__ = "aqi_records"
    
    id = Column(Integer, primary_key=True, index=True)
    city = Column(String, index=True)
    latitude = Column(Float)
    longitude = Column(Float)
    aqi = Column(Integer)
    pm25 = Column(Float, nullable=True)
    pm10 = Column(Float, nullable=True)
    temperature = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    wind_speed = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)


class PredictionRecord(Base):
    """Store prediction history."""
    
    __tablename__ = "prediction_records"
    
    id = Column(Integer, primary_key=True, index=True)
    city = Column(String, index=True)
    current_aqi = Column(Integer)
    predicted_aqi_2hr = Column(Integer)
    predicted_aqi_4hr = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)


class AlertRecord(Base):
    """Store generated alerts."""
    
    __tablename__ = "alert_records"
    
    id = Column(Integer, primary_key=True, index=True)
    city = Column(String, index=True)
    alert_type = Column(String)  # warning, danger, critical
    message = Column(String)
    aqi_value = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)

class User(Base):
    """Store registered users."""
 
    __tablename__ = "users"
 
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    city = Column(String, nullable=True)
    age_group = Column(String, nullable=True)        # <18 | 18-30 | 30-45 | 45-60 | 60+
    health_condition = Column(String, nullable=True) # normal | asthma | elderly
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)



def create_tables():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
