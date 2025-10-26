from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid

router = APIRouter(prefix="/api/calls", tags=["Calls"])

# In-memory storage for active calls and waiting queues
active_calls: dict = {}  # call_id -> {agent_ws, customer_ws, agent_name, customer_name, started_at}
waiting_customers: list = []  # [{customer_name, call_id, timestamp}]
available_agents: list = []  # [{agent_name, call_id, timestamp}]

class StartCallRequest(BaseModel):
    user_type: str  # "agent" or "customer"
    user_name: str

class CallResponse(BaseModel):
    call_id: str
    status: str
    message: str
    matched: bool = False
    partner_name: Optional[str] = None

@router.post("/start", response_model=CallResponse)
async def start_call(request: StartCallRequest):
    """
    Start a new call session
    Agent or customer requests to start a call
    If match found, return call_id and partner info
    Otherwise, add to waiting queue
    """
    call_id = f"call_{uuid.uuid4().hex[:12]}"
    
    if request.user_type == "customer":
        # Customer wants to connect - check if any agents available
        if available_agents:
            # Match with first available agent
            agent_info = available_agents.pop(0)
            
            # Create active call session
            active_calls[call_id] = {
                "agent_call_id": agent_info["call_id"],
                "customer_call_id": call_id,
                "agent_name": agent_info["agent_name"],
                "customer_name": request.user_name,
                "started_at": datetime.utcnow().isoformat(),
                "status": "active"
            }
            
            return CallResponse(
                call_id=call_id,
                status="matched",
                message=f"Connected to agent {agent_info['agent_name']}",
                matched=True,
                partner_name=agent_info["agent_name"]
            )
        else:
            # No agents available - add to queue
            waiting_customers.append({
                "customer_name": request.user_name,
                "call_id": call_id,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            return CallResponse(
                call_id=call_id,
                status="waiting",
                message="Waiting for available agent...",
                matched=False
            )
    
    elif request.user_type == "agent":
        # Agent wants to take calls - check if any customers waiting
        if waiting_customers:
            # Match with first waiting customer
            customer_info = waiting_customers.pop(0)
            
            # Create active call session
            active_calls[call_id] = {
                "agent_call_id": call_id,
                "customer_call_id": customer_info["call_id"],
                "agent_name": request.user_name,
                "customer_name": customer_info["customer_name"],
                "started_at": datetime.utcnow().isoformat(),
                "status": "active"
            }
            
            return CallResponse(
                call_id=call_id,
                status="matched",
                message=f"Connected to customer {customer_info['customer_name']}",
                matched=True,
                partner_name=customer_info["customer_name"]
            )
        else:
            # No customers waiting - mark agent as available
            available_agents.append({
                "agent_name": request.user_name,
                "call_id": call_id,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            return CallResponse(
                call_id=call_id,
                status="waiting",
                message="Waiting for customer...",
                matched=False
            )
    
    raise HTTPException(status_code=400, detail="Invalid user_type")

@router.get("/status/{call_id}")
async def get_call_status(call_id: str):
    """Get current status of a call"""
    
    # Check if in active calls
    for active_call_id, call_info in active_calls.items():
        if call_id in [call_info.get("agent_call_id"), call_info.get("customer_call_id")]:
            return {
                "status": "active",
                "call_info": call_info
            }
    
    # Check if in waiting queue
    for customer in waiting_customers:
        if customer["call_id"] == call_id:
            return {
                "status": "waiting",
                "queue_position": waiting_customers.index(customer) + 1,
                "total_waiting": len(waiting_customers)
            }
    
    for agent in available_agents:
        if agent["call_id"] == call_id:
            return {
                "status": "available",
                "waiting_customers": len(waiting_customers)
            }
    
    return {"status": "not_found"}

@router.post("/end/{call_id}")
async def end_call(call_id: str):
    """End a call session"""
    
    # Remove from active calls
    call_to_remove = None
    for active_call_id, call_info in active_calls.items():
        if call_id in [call_info.get("agent_call_id"), call_info.get("customer_call_id")]:
            call_to_remove = active_call_id
            break
    
    if call_to_remove:
        del active_calls[call_to_remove]
        return {"status": "ended", "message": "Call ended successfully"}
    
    # Remove from waiting queues
    waiting_customers[:] = [c for c in waiting_customers if c["call_id"] != call_id]
    available_agents[:] = [a for a in available_agents if a["call_id"] != call_id]
    
    return {"status": "ended", "message": "Removed from queue"}

@router.get("/stats")
async def get_call_stats():
    """Get current call center statistics"""
    return {
        "active_calls": len(active_calls),
        "waiting_customers": len(waiting_customers),
        "available_agents": len(available_agents),
        "active_call_details": list(active_calls.values())
    }

@router.get("/match/{call_id}")
async def get_partner_call_id(call_id: str):
    """Get the partner's call_id for routing messages"""
    for active_call_id, call_info in active_calls.items():
        if call_id == call_info.get("agent_call_id"):
            return {
                "partner_call_id": call_info.get("customer_call_id"),
                "partner_name": call_info.get("customer_name"),
                "partner_type": "customer"
            }
        elif call_id == call_info.get("customer_call_id"):
            return {
                "partner_call_id": call_info.get("agent_call_id"),
                "partner_name": call_info.get("agent_name"),
                "partner_type": "agent"
            }
    
    raise HTTPException(status_code=404, detail="Call not found or not matched")

