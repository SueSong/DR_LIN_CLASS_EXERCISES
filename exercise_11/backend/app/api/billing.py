"""
Billing API endpoints for cost tracking and reports.
"""

import sys
from pathlib import Path
from datetime import date, timedelta
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any

# Add billing directory to path
billing_dir = Path(__file__).parent.parent.parent.parent / "billing"
sys.path.insert(0, str(billing_dir.parent))

from billing.ledger import get_ledger

router = APIRouter(prefix="/api/billing", tags=["billing"])


class BudgetConfig(BaseModel):
    """Budget configuration request"""
    daily_budget_usd: float


@router.get("/daily")
async def get_daily_stats(target_date: Optional[str] = None):
    """
    Get daily cost statistics.
    
    Query params:
        target_date: Date in YYYY-MM-DD format (default: today)
    """
    ledger = get_ledger()
    
    if target_date:
        try:
            target = date.fromisoformat(target_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    else:
        target = None
    
    stats = ledger.get_daily_stats(target)
    is_over, current_cost, budget = ledger.is_over_budget(target)
    
    return {
        **stats,
        "is_over_budget": is_over,
        "current_cost_usd": round(current_cost, 4),
        "budget_limit_usd": budget
    }


@router.get("/budget/status")
async def get_budget_status(target_date: Optional[str] = None):
    """
    Get current budget status.
    
    Query params:
        target_date: Date in YYYY-MM-DD format (default: today)
    """
    ledger = get_ledger()
    
    if target_date:
        try:
            target = date.fromisoformat(target_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    else:
        target = None
    
    is_over, current_cost, budget = ledger.is_over_budget(target)
    
    return {
        "is_over_budget": is_over,
        "current_cost_usd": round(current_cost, 4),
        "budget_limit_usd": budget,
        "budget_remaining_usd": round(budget - current_cost, 4),
        "budget_used_percent": round((current_cost / budget) * 100, 2) if budget > 0 else 0,
        "date": (target or date.today()).isoformat()
    }


@router.post("/budget")
async def set_budget(config: BudgetConfig):
    """Set daily budget limit."""
    ledger = get_ledger()
    ledger.set_daily_budget(config.daily_budget_usd)
    return {
        "success": True,
        "daily_budget_usd": ledger.daily_budget_usd
    }


@router.get("/report")
async def get_report(days: int = 7):
    """
    Get summary report with sparkline data.
    
    Query params:
        days: Number of days to include (default: 7)
    """
    ledger = get_ledger()
    report = ledger.generate_summary_report(days)
    return report


@router.get("/report/csv/{target_date}")
async def get_csv_report(target_date: str):
    """
    Generate and return CSV report for a specific date.
    
    Path params:
        target_date: Date in YYYY-MM-DD format
    """
    ledger = get_ledger()
    
    try:
        target = date.fromisoformat(target_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    csv_path = ledger.generate_daily_csv(target)
    
    if not csv_path.exists():
        raise HTTPException(status_code=404, detail="Report not found")
    
    from fastapi.responses import FileResponse
    return FileResponse(
        path=str(csv_path),
        filename=csv_path.name,
        media_type="text/csv"
    )


@router.get("/report/preview/{target_date}")
async def get_csv_preview(target_date: str):
    """
    Get CSV report data as JSON for preview.
    
    Path params:
        target_date: Date in YYYY-MM-DD format
        
    Returns:
        JSON object with report data and metadata
    """
    ledger = get_ledger()
    
    try:
        target = date.fromisoformat(target_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    target_date_str = target.isoformat()
    
    # Get day's records
    day_records = [
        record for record in ledger.turns
        if record.timestamp.startswith(target_date_str)
    ]
    
    # Convert to list of dicts for JSON response
    records_data = []
    for record in day_records:
        records_data.append({
            'turn_id': record.turn_id,
            'session_id': record.session_id,
            'timestamp': record.timestamp,
            'input_tokens': record.input_tokens,
            'output_tokens': record.output_tokens,
            'total_tokens': record.input_tokens + record.output_tokens,
            'cost_usd': round(record.cost_usd, 6),
            'model_mode': record.model_mode,
            'was_over_budget': record.was_over_budget
        })
    
    # Get stats for this date
    stats = ledger.get_daily_stats(target)
    
    return {
        'date': target_date_str,
        'total_records': len(records_data),
        'stats': stats,
        'records': records_data
    }


@router.get("/sparkline")
async def get_sparkline(days: int = 7):
    """
    Get sparkline data for visualization.
    
    Query params:
        days: Number of days to include (default: 7)
        
    Returns:
        Array of daily costs for sparkline chart
    """
    ledger = get_ledger()
    report = ledger.generate_summary_report(days)
    
    return {
        "days": days,
        "start_date": report["start_date"],
        "end_date": report["end_date"],
        "data": report["sparkline_data"],
        "labels": [s["date"] for s in report["daily_stats"]]
    }

