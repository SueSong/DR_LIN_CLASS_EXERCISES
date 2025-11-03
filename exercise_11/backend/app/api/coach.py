from fastapi import APIRouter
from pydantic import BaseModel
import uuid
from ..sessions import create_session

router = APIRouter(prefix="/api/coach", tags=["Coach"])


class StartSessionRequest(BaseModel):
    parent_name: str


@router.post("/start")
async def start_session(req: StartSessionRequest):
    session_id = f"sess_{uuid.uuid4().hex[:12]}"
    # Store session with parent name
    create_session(session_id, req.parent_name)
    return {
        "session_id": session_id,
        "message": f"Welcome {req.parent_name}! You can start chatting with your parenting coach.",
    }


