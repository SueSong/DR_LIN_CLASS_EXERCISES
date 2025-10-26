"""
Main FastAPI Application with Multi-Agent Framework

This version uses the Agent/Team/Coordinator framework for orchestration.
Students can use this as a reference or replace main.py with this approach.
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import uuid

# Import our multi-agent framework
from app.agents import Agent, Team, Coordinator
from app.agents.agent import ParserAgent, RiskAnalyzerAgent, RedlineGeneratorAgent
from app.agents.team import TeamPattern

app = FastAPI(
    title="Exercise 8: HITL Contract Redlining Orchestrator (with Framework)",
    description="Multi-agent system for legal document review with HITL gates",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the Coordinator (manages all agents and blackboard)
coordinator = Coordinator()

# In-memory document and playbook storage (for classroom)
documents: Dict[str, Dict[str, Any]] = {}
playbooks: Dict[str, Dict[str, Any]] = {}


# ==================== Pydantic Models ====================

class RunRequest(BaseModel):
    doc_id: str
    agent_path: str = "sequential"  # sequential | manager_worker | planner_executor
    playbook_id: Optional[str] = None


class RiskApprovalItem(BaseModel):
    clause_id: str
    approved: bool = True
    comments: Optional[str] = None


class RiskApprovalRequest(BaseModel):
    run_id: str
    items: List[RiskApprovalItem]


class FinalApproveRequest(BaseModel):
    run_id: str
    approved_proposals: List[str]
    rejected_proposals: List[str] = []
    notes: Optional[str] = None


# ==================== Startup Event ====================

@app.on_event("startup")
async def setup_teams():
    """
    Initialize demo teams for students to use.
    Students can modify these or create their own teams.
    """
    print("🚀 Initializing multi-agent framework...")
    
    # Sequential Team: Parser -> Risk Analyzer -> Redline Generator
    sequential_team = Team(
        name="sequential_team",
        pattern=TeamPattern.SEQUENTIAL,
        description="Sequential execution: parse, assess, redline"
    )
    sequential_team.add_agent(ParserAgent())
    sequential_team.add_agent(RiskAnalyzerAgent())
    sequential_team.add_agent(RedlineGeneratorAgent())
    coordinator.register_team(sequential_team)
    
    # Manager-Worker Team
    manager_worker_team = Team(
        name="manager_worker_team",
        pattern=TeamPattern.MANAGER_WORKER,
        description="Manager decomposes work, workers execute in parallel"
    )
    # For demo, using same agents (students should implement proper manager/workers)
    manager_worker_team.add_agent(ParserAgent())
    manager_worker_team.add_agent(RiskAnalyzerAgent())
    manager_worker_team.add_agent(RedlineGeneratorAgent())
    coordinator.register_team(manager_worker_team)
    
    # Pipeline Team
    pipeline_team = Team(
        name="planner_executor_team",
        pattern=TeamPattern.PIPELINE,
        description="Pipeline execution with data passing between agents"
    )
    pipeline_team.add_agent(ParserAgent())
    pipeline_team.add_agent(RiskAnalyzerAgent())
    pipeline_team.add_agent(RedlineGeneratorAgent())
    coordinator.register_team(pipeline_team)
    
    print("✅ Demo teams initialized successfully")
    print(f"📊 Coordinator stats: {coordinator.get_stats()}")
    
    # Add some sample documents
    documents["doc_001"] = {
        "doc_id": "doc_001",
        "name": "Sample_NDA.md",
        "content": """# Non-Disclosure Agreement

## 1. Confidential Information
The parties agree to protect confidential information disclosed during the term of this agreement.

## 2. Obligations
Recipient shall not disclose confidential information to third parties without prior written consent.

## 3. Liability
Company shall be liable for any and all damages arising from breach of this agreement, including but not limited to direct, indirect, incidental, consequential, and punitive damages.

## 4. Term
This agreement shall remain in effect for a period of five (5) years from the date of execution."""
    }
    
    # Add sample playbook
    playbooks["playbook_001"] = {
        "playbook_id": "playbook_001",
        "name": "Standard NDA Policy",
        "rules": {
            "liability_cap": "12 months fees",
            "data_retention": "90 days post-termination",
            "indemnity_exclusions": ["force majeure", "third-party claims"]
        }
    }
    
    print("📄 Sample documents and playbooks loaded")


# ==================== Health Check ====================

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "exercise-8-with-framework",
        "coordinator_stats": coordinator.get_stats()
    }


# ==================== Document Management ====================

@app.post("/api/documents")
async def upload_document(file: UploadFile = File(...)):
    """Upload a document"""
    try:
        content = (await file.read()).decode("utf-8", errors="ignore")
        doc_id = f"doc_{uuid.uuid4().hex[:8]}"
        
        documents[doc_id] = {
            "doc_id": doc_id,
            "name": file.filename,
            "content": content,
            "uploaded_at": str(uuid.uuid1().time)
        }
        
        return {"doc_id": doc_id, "name": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/documents")
async def list_documents():
    """List all documents"""
    return [
        {
            "doc_id": doc["doc_id"],
            "name": doc["name"],
            "uploaded_at": doc.get("uploaded_at")
        }
        for doc in documents.values()
    ]


# ==================== Playbook Management ====================

@app.post("/api/playbooks")
async def create_playbook(name: str, rules: Dict[str, Any]):
    """Create a playbook"""
    playbook_id = f"playbook_{uuid.uuid4().hex[:8]}"
    
    playbooks[playbook_id] = {
        "playbook_id": playbook_id,
        "name": name,
        "rules": rules
    }
    
    return {"playbook_id": playbook_id, "name": name}


@app.get("/api/playbooks")
async def list_playbooks():
    """List all playbooks"""
    return list(playbooks.values())


@app.delete("/api/playbooks/{playbook_id}")
async def delete_playbook(playbook_id: str):
    """Delete a playbook"""
    if playbook_id in playbooks:
        del playbooks[playbook_id]
        return {"status": "deleted"}
    raise HTTPException(status_code=404, detail="Playbook not found")


# ==================== Run Orchestration ====================

@app.post("/api/run")
async def start_run(request: RunRequest):
    """
    Start a new document review run using the multi-agent framework.
    
    This endpoint:
    1. Validates the document exists
    2. Gets policy rules from playbook (if specified)
    3. Starts a run using the Coordinator
    4. Returns run_id for tracking
    """
    # Validate document
    if request.doc_id not in documents:
        raise HTTPException(status_code=404, detail="Document not found")
    
    doc = documents[request.doc_id]
    
    # Get policy rules from playbook
    policy_rules = {}
    if request.playbook_id and request.playbook_id in playbooks:
        policy_rules = playbooks[request.playbook_id]["rules"]
    
    # Start run using coordinator
    try:
        run_id = coordinator.start_run(
            doc_id=request.doc_id,
            document_text=doc["content"],
            agent_path=request.agent_path,
            playbook_id=request.playbook_id,
            policy_rules=policy_rules
        )
        
        return {
            "run_id": run_id,
            "doc_id": request.doc_id,
            "agent_path": request.agent_path,
            "status": "running"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/run/{run_id}")
async def get_run(run_id: str):
    """
    Get run details including blackboard state.
    """
    run = coordinator.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    
    blackboard = coordinator.get_blackboard(run_id)
    
    return {
        **run,
        "history": blackboard.get("history", []),
        "assessments": blackboard.get("assessments", []),
        "proposals": blackboard.get("proposals", []),
        "score": blackboard.get("score", 0)
    }


@app.get("/api/runs")
async def list_runs():
    """List all runs"""
    return coordinator.list_runs()


# ==================== HITL Gates ====================

@app.post("/api/hitl/risk-approve")
async def risk_approve(request: RiskApprovalRequest):
    """
    Risk Gate: Human approval for high-risk clauses.
    """
    # Separate approved and rejected clauses
    approved = [item.clause_id for item in request.items if item.approved]
    rejected = [item.clause_id for item in request.items if not item.approved]
    comments = {item.clause_id: item.comments for item in request.items if item.comments}
    
    success = coordinator.approve_risk(
        run_id=request.run_id,
        approved_clauses=approved,
        rejected_clauses=rejected,
        comments=comments
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Run not found")
    
    return {"status": "approved", "run_id": request.run_id}


@app.post("/api/hitl/final-approve")
async def final_approve(request: FinalApproveRequest):
    """
    Final Gate: Human approval for all redline proposals.
    """
    success = coordinator.approve_final(
        run_id=request.run_id,
        approved_proposals=request.approved_proposals,
        rejected_proposals=request.rejected_proposals,
        notes=request.notes
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Run not found")
    
    return {"status": "approved", "run_id": request.run_id}


@app.get("/api/blackboard/{run_id}")
async def get_blackboard(run_id: str):
    """
    Get the blackboard (shared memory) for a run.
    """
    blackboard = coordinator.get_blackboard(run_id)
    if not blackboard:
        raise HTTPException(status_code=404, detail="Run not found")
    
    return blackboard


# ==================== Export ====================

@app.post("/api/export/redline")
async def export_redline(run_id: str, format: str = "md"):
    """
    Export redlined document.
    
    TODO for students: Implement actual document generation
    """
    blackboard = coordinator.get_blackboard(run_id)
    if not blackboard:
        raise HTTPException(status_code=404, detail="Run not found")
    
    # TODO: Generate actual DOCX/PDF/MD file
    # For now, return a mock artifact URI
    return {
        "artifact_uri": f"/exports/{run_id}_redlined.{format}",
        "format": format,
        "run_id": run_id
    }


# ==================== Reports & Metrics ====================

@app.get("/api/reports/slos")
async def get_slos():
    """
    Get SLO metrics.
    
    TODO for students: Implement actual metrics calculation
    """
    return {
        "latency_p95_ms": 4820,
        "quality_score": 94.2,
        "cost_per_doc_usd": 3.85,
        "success_rate": 0.942
    }


# ==================== Replay & Debug ====================

@app.get("/api/replay/{run_id}")
async def get_replay_data(run_id: str):
    """
    Get replay data for debugging.
    """
    blackboard = coordinator.get_blackboard(run_id)
    if not blackboard:
        raise HTTPException(status_code=404, detail="Run not found")
    
    return {
        "run_id": run_id,
        "history": blackboard.get("history", []),
        "blackboard_snapshots": []  # TODO: Implement checkpoint snapshots
    }


# ==================== Team Management (for debugging) ====================

@app.get("/api/teams")
async def list_teams():
    """List all registered teams"""
    return [
        team.get_info()
        for team in coordinator.teams.values()
    ]


@app.get("/api/teams/{team_name}")
async def get_team(team_name: str):
    """Get team details"""
    team = coordinator.get_team(team_name)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    return team.get_info()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
