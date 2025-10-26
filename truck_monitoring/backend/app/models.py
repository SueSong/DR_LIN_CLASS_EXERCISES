"""
Database models for truck monitoring system
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class User(Base):
    """User model for authentication"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<User {self.username}>"


class Truck(Base):
    """Truck passing record"""
    __tablename__ = "trucks"

    id = Column(Integer, primary_key=True, index=True)
    truck_number = Column(String(50), index=True, nullable=False)
    license_plate = Column(String(20), index=True)
    truck_type = Column(String(50))  # e.g., "Container", "Flatbed", "Tanker"
    length_meters = Column(Float)
    weight_tons = Column(Float, nullable=True)
    speed_kmh = Column(Float, nullable=True)
    
    # Location data
    location = Column(String(100))  # e.g., "Highway 101 North"
    direction = Column(String(20))  # e.g., "Northbound", "Southbound"
    
    # Time data
    pass_time = Column(DateTime, index=True, nullable=False)
    date = Column(String(10), index=True)  # YYYY-MM-DD for easy querying
    
    # Media
    image_url = Column(String(500))
    video_url = Column(String(500))
    thumbnail_url = Column(String(500))
    
    # Additional info
    company_name = Column(String(100))
    driver_name = Column(String(100))
    cargo_description = Column(Text)
    notes = Column(Text)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Truck {self.truck_number} at {self.pass_time}>"


class DailyStatistics(Base):
    """Daily aggregated statistics"""
    __tablename__ = "daily_statistics"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String(10), unique=True, index=True, nullable=False)  # YYYY-MM-DD
    total_trucks = Column(Integer, default=0)
    avg_length = Column(Float, default=0.0)
    avg_speed = Column(Float, default=0.0)
    peak_hour = Column(Integer)  # Hour with most traffic (0-23)
    peak_hour_count = Column(Integer, default=0)
    
    # Breakdown by type
    container_count = Column(Integer, default=0)
    flatbed_count = Column(Integer, default=0)
    tanker_count = Column(Integer, default=0)
    other_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<DailyStats {self.date}: {self.total_trucks} trucks>"

