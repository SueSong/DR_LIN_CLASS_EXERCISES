"""
Truck management API routes
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from ..database import get_db
from ..auth import get_current_active_user
from ..models import Truck, User

router = APIRouter(prefix="/api/trucks", tags=["Trucks"])


class TruckResponse(BaseModel):
    id: int
    truck_number: str
    license_plate: Optional[str]
    truck_type: Optional[str]
    length_meters: Optional[float]
    weight_tons: Optional[float]
    speed_kmh: Optional[float]
    location: Optional[str]
    direction: Optional[str]
    pass_time: datetime
    date: str
    image_url: Optional[str]
    video_url: Optional[str]
    thumbnail_url: Optional[str]
    company_name: Optional[str]
    driver_name: Optional[str]
    cargo_description: Optional[str]
    notes: Optional[str]

    class Config:
        from_attributes = True


class TruckListResponse(BaseModel):
    trucks: List[TruckResponse]
    total: int
    page: int
    page_size: int


@router.get("/", response_model=TruckListResponse)
async def list_trucks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    date: Optional[str] = None,
    truck_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    List all trucks with pagination and filters
    """
    query = db.query(Truck)
    
    # Apply filters
    if date:
        query = query.filter(Truck.date == date)
    if truck_type:
        query = query.filter(Truck.truck_type == truck_type)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    trucks = query.order_by(desc(Truck.pass_time))\
                  .offset((page - 1) * page_size)\
                  .limit(page_size)\
                  .all()
    
    return {
        "trucks": trucks,
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.get("/{truck_id}", response_model=TruckResponse)
async def get_truck(
    truck_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get truck details by ID"""
    truck = db.query(Truck).filter(Truck.id == truck_id).first()
    if not truck:
        raise HTTPException(status_code=404, detail="Truck not found")
    return truck


@router.get("/search/by-plate/{license_plate}", response_model=List[TruckResponse])
async def search_by_plate(
    license_plate: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Search trucks by license plate"""
    trucks = db.query(Truck)\
              .filter(Truck.license_plate.like(f"%{license_plate}%"))\
              .order_by(desc(Truck.pass_time))\
              .all()
    return trucks


@router.get("/search/by-date/{date}", response_model=List[TruckResponse])
async def get_trucks_by_date(
    date: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all trucks for a specific date (YYYY-MM-DD)"""
    trucks = db.query(Truck)\
              .filter(Truck.date == date)\
              .order_by(Truck.pass_time)\
              .all()
    return trucks

