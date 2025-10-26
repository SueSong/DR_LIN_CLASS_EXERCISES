"""
Exercise 7: Agents API Routes (Scaffold)
Plan/Execute controller entrypoints, trace replay, prompt switching, cost report

Students: fill controller logic and telemetry in app/agents/* modules.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any
from datetime import datetime
import uuid

router = APIRouter(prefix="/api/agents", tags=["Agents"])


@router.post("/run")
async def run_agent(payload: Dict[str, Any], background: BackgroundTasks) -> Dict[str, Any]:
    """Kick off a plan-execute run. Returns a new trace_id.

    Expected payload: { "query": str, "session_id"?: str }
    """
    query = payload.get("query")
    if not query:
        raise HTTPException(status_code=400, detail="query is required")

    trace_id = str(uuid.uuid4())
    # execute controller in background and store trace
    try:
        from app.agents.tracing import trace_store
        from app.agents.controller import run_plan
        trace_store.new_trace(trace_id)
        overrides = payload.get("overrides") or {}
        background.add_task(run_plan, trace_id, query, overrides)
    except Exception:
        pass
    return {"trace_id": trace_id, "status": "queued"}


@router.get("/trace/{trace_id}")
async def get_trace(trace_id: str) -> Dict[str, Any]:
    """Return a mock trace with spans for UI development.
    Students will replace with real persisted trace data.
    """
    try:
        from app.agents.tracing import trace_store
        return trace_store.get_trace(trace_id)
    except Exception:
        return {"trace": {"trace_id": trace_id}, "spans": []}


@router.post("/replay/{trace_id}")
async def replay_trace(trace_id: str) -> Dict[str, Any]:
    """Stub replay endpoint. Students wire to controller with stored inputs."""
    new_trace_id = str(uuid.uuid4())
    return {"trace_id": new_trace_id, "replayed_from": trace_id}


@router.post("/prompt/switch")
async def switch_prompt(name: str, v: int) -> Dict[str, Any]:
    """Switch active prompt version for a prompt name (scaffold)."""
    if name != "planner":
        raise HTTPException(status_code=400, detail="unknown prompt name")
    return {"status": "ok", "name": name, "active_version": v}


@router.get("/report/cost")
async def report_cost(from_ts: str | None = None, to_ts: str | None = None) -> Dict[str, Any]:
    """Return mock aggregates for cost dashboard (students to implement)."""
    return {
        "summary": {"total_cost_usd": 0.0123, "total_traces": 3},
        "by_prompt_version": [
            {"version": "v1", "cost_usd": 0.008, "traces": 2},
            {"version": "v2", "cost_usd": 0.0043, "traces": 1},
        ],
        "by_tool": [
            {"tool": "SearchTool", "cost_usd": 0.004},
            {"tool": "PriceTool", "cost_usd": 0.007},
            {"tool": "CacheTool", "cost_usd": 0.0013},
        ],
    }


