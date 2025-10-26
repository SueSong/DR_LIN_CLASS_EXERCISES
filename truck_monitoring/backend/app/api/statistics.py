"""
Statistics API routes
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta

from ..database import get_db
from ..auth import get_current_active_user
from ..models import Truck, DailyStatistics, User

router = APIRouter(prefix="/api/statistics", tags=["Statistics"])


class DailyStatsResponse(BaseModel):
    date: str
    total_trucks: int
    avg_length: float
    avg_speed: float
    peak_hour: Optional[int]
    peak_hour_count: int
    container_count: int
    flatbed_count: int
    tanker_count: int
    other_count: int

    class Config:
        from_attributes = True


class HourlyStats(BaseModel):
    hour: int
    count: int


class TruckTypeStats(BaseModel):
    truck_type: str
    count: int
    percentage: float


@router.get("/daily", response_model=List[DailyStatsResponse])
async def get_daily_statistics(
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get daily statistics for the last N days"""
    stats = db.query(DailyStatistics)\
             .order_by(DailyStatistics.date.desc())\
             .limit(days)\
             .all()
    return list(reversed(stats))


@router.get("/dashboard")
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Get dashboard statistics"""
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    # Today's stats
    today_count = db.query(func.count(Truck.id))\
                    .filter(Truck.date == today)\
                    .scalar() or 0
    
    # Yesterday's stats
    yesterday_count = db.query(func.count(Truck.id))\
                        .filter(Truck.date == yesterday)\
                        .scalar() or 0
    
    # Total trucks
    total_trucks = db.query(func.count(Truck.id)).scalar() or 0
    
    # Average length
    avg_length = db.query(func.avg(Truck.length_meters))\
                   .filter(Truck.length_meters.isnot(None))\
                   .scalar() or 0.0
    
    # Average speed
    avg_speed = db.query(func.avg(Truck.speed_kmh))\
                  .filter(Truck.speed_kmh.isnot(None))\
                  .scalar() or 0.0
    
    # Percentage change
    if yesterday_count > 0:
        percentage_change = ((today_count - yesterday_count) / yesterday_count) * 100
    else:
        percentage_change = 100 if today_count > 0 else 0
    
    # Truck types distribution
    type_stats = db.query(
        Truck.truck_type,
        func.count(Truck.id).label('count')
    ).filter(Truck.truck_type.isnot(None))\
     .group_by(Truck.truck_type)\
     .all()
    
    truck_types = []
    total_typed = sum(stat.count for stat in type_stats)
    for stat in type_stats:
        percentage = (stat.count / total_typed * 100) if total_typed > 0 else 0
        truck_types.append({
            "truck_type": stat.truck_type,
            "count": stat.count,
            "percentage": round(percentage, 1)
        })
    
    return {
        "today_count": today_count,
        "yesterday_count": yesterday_count,
        "total_trucks": total_trucks,
        "percentage_change": round(percentage_change, 1),
        "avg_length_meters": round(avg_length, 2),
        "avg_speed_kmh": round(avg_speed, 2),
        "truck_types": truck_types
    }


@router.get("/hourly/{date}")
async def get_hourly_distribution(
    date: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[HourlyStats]:
    """Get hourly distribution of trucks for a specific date"""
    results = db.query(
        func.hour(Truck.pass_time).label('hour'),
        func.count(Truck.id).label('count')
    ).filter(Truck.date == date)\
     .group_by(func.hour(Truck.pass_time))\
     .order_by('hour')\
     .all()
    
    return [
        {"hour": result.hour, "count": result.count}
        for result in results
    ]


@router.get("/weekly")
async def get_weekly_trend(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[Dict[str, Any]]:
    """Get weekly trend (last 7 days)"""
    results = db.query(
        Truck.date,
        func.count(Truck.id).label('count')
    ).filter(
        Truck.date >= (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    ).group_by(Truck.date)\
     .order_by(Truck.date)\
     .all()
    
    return [
        {"date": result.date, "count": result.count}
        for result in results
    ]


@router.get("/types")
async def get_truck_types_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[TruckTypeStats]:
    """Get statistics by truck type"""
    results = db.query(
        Truck.truck_type,
        func.count(Truck.id).label('count')
    ).filter(Truck.truck_type.isnot(None))\
     .group_by(Truck.truck_type)\
     .all()
    
    total = sum(result.count for result in results)
    
    return [
        TruckTypeStats(
            truck_type=result.truck_type,
            count=result.count,
            percentage=round((result.count / total * 100), 1) if total > 0 else 0
        )
        for result in results
    ]

