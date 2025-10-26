from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import uuid

app = FastAPI(title="Exercise 8 Backend", version="0.2.0")

app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_methods=["*"],
	allow_headers=["*"],
)

# In-memory store (classroom scope)
BLACKBOARD: Dict[str, Dict[str, Any]] = {
	"runs": {},        # run_id -> {doc_id, agent_path, playbook_id, history[], score, ...}
	"docs": {},        # doc_id -> {name, content}
	"playbooks": {},   # playbook_id -> {name, rules}
}

class RunRequest(BaseModel):
	doc_id: Optional[str] = None
	agent_path: Optional[str] = None  # e.g. manager_worker | planner_executor | reviewer_referee
	playbook_id: Optional[str] = None
	scope: Optional[str] = None
	options: Optional[Dict[str, Any]] = None

class RiskApprovalItem(BaseModel):
	clause_id: str
	risk_override: Optional[str] = None
	comments: Optional[str] = None

class RiskApprovalRequest(BaseModel):
	run_id: str
	items: List[RiskApprovalItem]

class FinalApproveRequest(BaseModel):
	run_id: str
	note: Optional[str] = None

@app.get("/health")
async def health():
	return {"status": "healthy", "service": "exercise-8"}

# --------------------------- Documents ---------------------------
@app.post("/api/docs/upload")
async def upload_doc(file: UploadFile = File(...)):
	content = (await file.read()).decode("utf-8", errors="ignore")
	doc_id = str(uuid.uuid4())
	BLACKBOARD["docs"][doc_id] = {"name": file.filename, "content": content}
	return {"doc_id": doc_id, "name": file.filename}

@app.get("/api/docs")
async def list_docs():
	return [{"doc_id": k, "name": v.get("name")} for k, v in BLACKBOARD["docs"].items()]

@app.get("/api/docs/{doc_id}")
async def get_doc(doc_id: str):
	doc = BLACKBOARD["docs"].get(doc_id)
	if not doc:
		raise HTTPException(status_code=404, detail="doc not found")
	return doc

# --------------------------- Playbooks ---------------------------
class PlaybookCreate(BaseModel):
	name: str
	rules: Dict[str, Any]

@app.post("/api/playbooks")
async def create_playbook(pb: PlaybookCreate):
	pb_id = str(uuid.uuid4())
	BLACKBOARD["playbooks"][pb_id] = {"name": pb.name, "rules": pb.rules}
	return {"playbook_id": pb_id}

@app.get("/api/playbooks")
async def list_playbooks():
	return [{"playbook_id": k, "name": v.get("name")} for k, v in BLACKBOARD["playbooks"].items()]

@app.get("/api/playbooks/{playbook_id}")
async def get_playbook(playbook_id: str):
	pb = BLACKBOARD["playbooks"].get(playbook_id)
	if not pb:
		raise HTTPException(status_code=404, detail="playbook not found")
	return pb

@app.delete("/api/playbooks/{playbook_id}")
async def delete_playbook(playbook_id: str):
	if playbook_id in BLACKBOARD["playbooks"]:
		del BLACKBOARD["playbooks"][playbook_id]
		return {"status": "deleted"}
	raise HTTPException(status_code=404, detail="playbook not found")

# --------------------------- Run & Orchestration ---------------------------
@app.post("/api/run")
async def start_run(req: RunRequest):
	run_id = str(uuid.uuid4())
	doc_id = req.doc_id or next(iter(BLACKBOARD["docs"].keys()), "nda")
	# minimal clause seed; in real impl, parse doc into clauses
	clauses = [
		{"id": "c1", "heading": "Confidential Information", "text": "The parties agree to keep information secret."},
		{"id": "c2", "heading": "Term", "text": "Two (2) years from Effective Date."},
		{"id": "c3", "heading": "Liability", "text": "Liability capped at 12 months of fees."},
	]
	assessments = [
		{"clause_id": "c1", "risk_level": "Low", "rationale": "Standard confidentiality", "policy_refs": ["security_standards"]},
		{"clause_id": "c2", "risk_level": "Medium", "rationale": "Term may vary", "policy_refs": []},
		{"clause_id": "c3", "risk_level": "Low", "rationale": "Aligns with policy cap", "policy_refs": ["liability_cap"]},
	]
	proposals = [
		{"clause_id": "c2", "variant": "conservative", "edited_text": "Three (3) years term.", "diffs": "+1y"},
		{"clause_id": "c2", "variant": "moderate", "edited_text": "Term: 24 months with renewal.", "diffs": "-"},
	]
	history = [
		{"step": "plan", "agent": "manager", "status": "ok", "notes": {"agent_path": req.agent_path or "manager_worker"}},
		{"step": "parse", "agent": "clause_parser", "status": "ok", "output": {"clauses": len(clauses)}},
		{"step": "retrieve_policy", "agent": "policy_retriever", "status": "ok"},
		{"step": "assess", "agent": "risk_tagger", "status": "ok", "output": {"high": 0, "medium": 1, "low": 2}},
		{"step": "review", "agent": "reviewer", "status": "ok"},
	]
	# toy score: 1 - (medium_count * 0.1)
	medium_count = sum(1 for a in assessments if a.get("risk_level") == "Medium")
	score = max(0.0, 1.0 - 0.1 * medium_count)
	BLACKBOARD["runs"][run_id] = {
		"doc_id": doc_id,
		"agent_path": req.agent_path or "manager_worker",
		"playbook_id": req.playbook_id,
		"clauses": clauses,
		"assessments": assessments,
		"proposals": proposals,
		"decisions": [],
		"artifacts": {},
		"history": history,
		"score": score,
	}
	return {"run_id": run_id, "trace_id": str(uuid.uuid4())}

@app.get("/api/run/{run_id}")
async def get_run(run_id: str):
	run = BLACKBOARD["runs"].get(run_id)
	if not run:
		raise HTTPException(status_code=404, detail="run not found")
	return run

@app.get("/api/blackboard/{run_id}")
async def get_blackboard(run_id: str):
	run = BLACKBOARD["runs"].get(run_id)
	if not run:
		raise HTTPException(status_code=404, detail="run not found")
	return run

@app.post("/api/hitl/risk-approve")
async def risk_approve(body: RiskApprovalRequest):
	run = BLACKBOARD["runs"].get(body.run_id)
	if not run:
		raise HTTPException(status_code=404, detail="run not found")
	for it in body.items:
		run.setdefault("decisions", []).append({
			"clause_id": it.clause_id,
			"status": "approved",
			"reviewer": "teacher",
			"comments": it.comments or "",
		})
		if it.risk_override:
			for a in run.get("assessments", []):
				if a.get("clause_id") == it.clause_id:
					a["risk_level"] = it.risk_override
	return {"status": "ok"}

@app.post("/api/hitl/final-approve")
async def final_approve(body: FinalApproveRequest):
	run = BLACKBOARD["runs"].get(body.run_id)
	if not run:
		raise HTTPException(status_code=404, detail="run not found")
	run.setdefault("artifacts", {})["memo.md"] = f"Approved note: {body.note or ''}"
	return {"status": "approved"}

@app.post("/api/export/redline")
async def export_redline(run_id: str, format: str = "md"):
	run = BLACKBOARD["runs"].get(run_id)
	if not run:
		raise HTTPException(status_code=404, detail="run not found")
	uri = f"/artifacts/{run_id}/redline.{format}"
	run.setdefault("artifacts", {})[f"redline.{format}"] = uri
	return {"artifact_uri": uri}

@app.get("/api/replay/{run_id}")
async def replay(run_id: str):
	# For class: simply return a new run cloned from existing
	run = BLACKBOARD["runs"].get(run_id)
	if not run:
		raise HTTPException(status_code=404, detail="run not found")
	new_id = str(uuid.uuid4())
	BLACKBOARD["runs"][new_id] = {**run, "replayed_from": run_id}
	return {"run_id": new_id}

@app.get("/api/report/slos")
async def report_slos():
	return {"p50_ms": 1200, "p95_ms": 3200, "reviewer_pass_rate": 0.9, "cost_usd": 0.012}
