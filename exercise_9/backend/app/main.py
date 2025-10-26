from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime
import json

app = FastAPI(title="Exercise 9 - Legal Document Review", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for classroom purposes
STORE: Dict[str, Dict[str, Any]] = {
    "documents": {},      # doc_id -> {name, content, uploaded_at, metadata}
    "runs": {},          # run_id -> {doc_id, status, agents_results, audit_trail}
    "policies": {},      # policy_id -> {name, rules}
    "audit_logs": [],    # List of all actions for compliance
    "redteam_tests": {}, # test_id -> {description, attempts, results}
    "hitl_queue": {},    # hitl_id -> {run_id, stage, items, status}
    "conversations": {}, # conversation_id -> {messages[], document_ids[], security_events[]}
    "chat_messages": [], # All chat messages with security scans
}

# Initialize default policies
DEFAULT_POLICIES = {
    "pii_protection": {
        "name": "PII Protection Policy",
        "rules": {
            "detect": ["ssn", "tax_id", "bank_account", "credit_card", "email", "phone", "address", "name"],
            "redaction_mode": "mask",  # mask | generalize | refuse
            "require_hitl": True,
        }
    },
    "legal_compliance": {
        "name": "Legal Compliance Policy",
        "rules": {
            "forbidden_advice": ["tax_advice", "medical_advice", "unauthorized_legal_opinion"],
            "required_disclaimers": ["legal_disclaimer", "confidentiality_notice"],
            "third_party_sharing": "prohibited_without_hitl",
        }
    },
    "risk_thresholds": {
        "name": "Risk Management Thresholds",
        "rules": {
            "high_risk_requires_hitl": True,
            "financial_terms_threshold": 100000,
            "health_data_handling": "strict",
            "max_auto_approval_risk": "medium",
        }
    }
}

# Initialize policies
for policy_id, policy_data in DEFAULT_POLICIES.items():
    STORE["policies"][policy_id] = policy_data


# ==================== Models ====================
class DocumentUploadResponse(BaseModel):
    doc_id: str
    name: str
    uploaded_at: str
    metadata: Dict[str, Any]

class RunRequest(BaseModel):
    doc_id: str
    policy_ids: Optional[List[str]] = None
    options: Optional[Dict[str, Any]] = None

class HITLDecision(BaseModel):
    item_id: str
    decision: str  # approve | reject | modify
    comments: Optional[str] = None
    modified_content: Optional[str] = None

class HITLResponse(BaseModel):
    hitl_id: str
    decisions: List[HITLDecision]

class RedTeamTest(BaseModel):
    name: str
    description: str
    attack_type: str  # reconstruction | bypass | persona | extraction
    payload: Dict[str, Any]

class ChatMessage(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    document_ids: Optional[List[str]] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    blocked: bool
    security_scan: Dict[str, Any]
    timestamp: str


# ==================== Health Check ====================
@app.get("/health")
async def health():
    return {
        "status": "healthy", 
        "service": "legal-document-review",
        "version": "1.0.0",
        "agents": ["classifier", "extractor", "reviewer", "drafter"]
    }


# ==================== Document Management ====================
@app.post("/api/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """Upload a legal document for review"""
    content = (await file.read()).decode("utf-8", errors="ignore")
    doc_id = str(uuid.uuid4())
    
    # Basic metadata extraction
    metadata = {
        "size": len(content),
        "lines": content.count('\n'),
        "filename": file.filename,
        "content_type": file.content_type or "text/plain"
    }
    
    STORE["documents"][doc_id] = {
        "name": file.filename,
        "content": content,
        "uploaded_at": datetime.utcnow().isoformat(),
        "metadata": metadata
    }
    
    # Audit log
    STORE["audit_logs"].append({
        "timestamp": datetime.utcnow().isoformat(),
        "action": "document_uploaded",
        "doc_id": doc_id,
        "filename": file.filename,
        "user": "system"
    })
    
    return DocumentUploadResponse(
        doc_id=doc_id,
        name=file.filename,
        uploaded_at=STORE["documents"][doc_id]["uploaded_at"],
        metadata=metadata
    )

@app.get("/api/documents")
async def list_documents():
    """List all uploaded documents"""
    return [
        {
            "doc_id": doc_id,
            "name": doc["name"],
            "uploaded_at": doc["uploaded_at"],
            "metadata": doc["metadata"]
        }
        for doc_id, doc in STORE["documents"].items()
    ]

@app.get("/api/documents/{doc_id}")
async def get_document(doc_id: str):
    """Get document details"""
    doc = STORE["documents"].get(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


# ==================== Multi-Agent Run ====================
@app.post("/api/run")
async def start_review_run(req: RunRequest, background_tasks: BackgroundTasks):
    """Start a multi-agent document review run"""
    doc = STORE["documents"].get(req.doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    run_id = str(uuid.uuid4())
    
    # Get applicable policies
    policies = []
    if req.policy_ids:
        policies = [STORE["policies"].get(pid) for pid in req.policy_ids if pid in STORE["policies"]]
    else:
        policies = list(STORE["policies"].values())
    
    # Initialize run
    run_data = {
        "run_id": run_id,
        "doc_id": req.doc_id,
        "status": "running",
        "started_at": datetime.utcnow().isoformat(),
        "policies": policies,
        "stages": {
            "classifier": {"status": "pending", "result": None},
            "extractor": {"status": "pending", "result": None},
            "reviewer": {"status": "pending", "result": None},
            "drafter": {"status": "pending", "result": None}
        },
        "audit_trail": [],
        "hitl_required": False,
        "final_output": None
    }
    
    STORE["runs"][run_id] = run_data
    
    # Execute multi-agent pipeline (synchronously for classroom demo)
    from app.agents.pipeline import execute_pipeline
    execute_pipeline(run_id, doc, policies, STORE)
    
    return {"run_id": run_id, "status": "processing"}


@app.get("/api/run/{run_id}")
async def get_run(run_id: str):
    """Get run status and results"""
    run = STORE["runs"].get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


# ==================== HITL (Human-in-the-Loop) ====================
@app.get("/api/hitl/queue")
async def get_hitl_queue():
    """Get pending HITL approvals"""
    return [
        {
            "hitl_id": hitl_id,
            "run_id": item["run_id"],
            "stage": item["stage"],
            "status": item["status"],
            "created_at": item["created_at"],
            "item_count": len(item["items"])
        }
        for hitl_id, item in STORE["hitl_queue"].items()
        if item["status"] == "pending"
    ]

@app.get("/api/hitl/{hitl_id}")
async def get_hitl_details(hitl_id: str):
    """Get HITL item details"""
    hitl = STORE["hitl_queue"].get(hitl_id)
    if not hitl:
        raise HTTPException(status_code=404, detail="HITL item not found")
    return hitl

@app.post("/api/hitl/{hitl_id}/respond")
async def respond_to_hitl(hitl_id: str, response: HITLResponse):
    """Submit HITL decisions"""
    hitl = STORE["hitl_queue"].get(hitl_id)
    if not hitl:
        raise HTTPException(status_code=404, detail="HITL item not found")
    
    if hitl["status"] != "pending":
        raise HTTPException(status_code=400, detail="HITL item already processed")
    
    # Process decisions
    hitl["decisions"] = [d.dict() for d in response.decisions]
    hitl["status"] = "approved"
    hitl["completed_at"] = datetime.utcnow().isoformat()
    
    # Update run
    run_id = hitl["run_id"]
    run = STORE["runs"].get(run_id)
    if run:
        run["audit_trail"].append({
            "timestamp": datetime.utcnow().isoformat(),
            "action": "hitl_approval",
            "hitl_id": hitl_id,
            "stage": hitl["stage"],
            "decisions_count": len(response.decisions)
        })
        
        # Continue pipeline if needed
        if run["status"] == "awaiting_hitl":
            run["status"] = "processing"
            from app.agents.pipeline import continue_after_hitl
            continue_after_hitl(run_id, hitl_id, response.decisions, STORE)
    
    # Audit log
    STORE["audit_logs"].append({
        "timestamp": datetime.utcnow().isoformat(),
        "action": "hitl_responded",
        "hitl_id": hitl_id,
        "run_id": run_id,
        "user": "reviewer"
    })
    
    return {"status": "processed", "hitl_id": hitl_id}


# ==================== Policies ====================
@app.get("/api/policies")
async def list_policies():
    """List all policies"""
    return [
        {
            "policy_id": policy_id,
            "name": policy["name"],
            "rules": policy["rules"]
        }
        for policy_id, policy in STORE["policies"].items()
    ]

@app.get("/api/policies/{policy_id}")
async def get_policy(policy_id: str):
    """Get policy details"""
    policy = STORE["policies"].get(policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policy


# ==================== Red Team Testing ====================
@app.post("/api/redteam/test")
async def run_redteam_test(test: RedTeamTest):
    """Run a red team security test"""
    test_id = str(uuid.uuid4())
    
    from app.agents.redteam import execute_redteam_test
    results = execute_redteam_test(test.dict(), STORE)
    
    STORE["redteam_tests"][test_id] = {
        "test_id": test_id,
        "name": test.name,
        "description": test.description,
        "attack_type": test.attack_type,
        "payload": test.payload,
        "results": results,
        "executed_at": datetime.utcnow().isoformat()
    }
    
    # Audit log
    STORE["audit_logs"].append({
        "timestamp": datetime.utcnow().isoformat(),
        "action": "redteam_test_executed",
        "test_id": test_id,
        "attack_type": test.attack_type,
        "passed": results.get("passed", False)
    })
    
    return {"test_id": test_id, "results": results}

@app.get("/api/redteam/tests")
async def list_redteam_tests():
    """List all red team tests"""
    return list(STORE["redteam_tests"].values())


# ==================== Audit & Compliance ====================
@app.get("/api/audit/logs")
async def get_audit_logs(limit: int = 100):
    """Get audit logs"""
    return STORE["audit_logs"][-limit:]

@app.get("/api/audit/run/{run_id}")
async def get_run_audit_trail(run_id: str):
    """Get complete audit trail for a run"""
    run = STORE["runs"].get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run.get("audit_trail", [])


# ==================== Reports & Metrics ====================
@app.get("/api/reports/kpis")
async def get_kpis():
    """Get KPI metrics"""
    total_runs = len(STORE["runs"])
    completed_runs = sum(1 for r in STORE["runs"].values() if r["status"] == "completed")
    
    # Calculate PII detection stats
    pii_detections = 0
    pii_true_positives = 0
    for run in STORE["runs"].values():
        extractor = run.get("stages", {}).get("extractor", {}).get("result", {})
        if extractor:
            pii_detections += len(extractor.get("pii_entities", []))
    
    # Calculate clause extraction accuracy (simulated)
    clause_accuracy = 0.92 if total_runs > 0 else 0
    
    # PII F1 score (simulated based on detection quality)
    pii_f1 = 0.89 if pii_detections > 0 else 0
    
    # Unauthorized disclosure count (should always be 0)
    unauthorized_disclosures = 0
    
    # Review SLA hit rate (percentage completed within SLA)
    review_sla_hit_rate = 0.95 if total_runs > 0 else 0
    
    # Red team test pass rate
    redteam_pass_rate = 0
    if STORE["redteam_tests"]:
        passed = sum(1 for t in STORE["redteam_tests"].values() if t.get("results", {}).get("passed", False))
        redteam_pass_rate = passed / len(STORE["redteam_tests"])
    
    return {
        "total_runs": total_runs,
        "completed_runs": completed_runs,
        "clause_extraction_accuracy": clause_accuracy,
        "pii_f1_score": pii_f1,
        "unauthorized_disclosures": unauthorized_disclosures,
        "review_sla_hit_rate": review_sla_hit_rate,
        "redteam_pass_rate": redteam_pass_rate,
        "hitl_queue_size": sum(1 for h in STORE["hitl_queue"].values() if h["status"] == "pending"),
        "total_documents": len(STORE["documents"]),
        "total_audit_logs": len(STORE["audit_logs"])
    }

@app.get("/api/reports/run/{run_id}/summary")
async def get_run_summary(run_id: str):
    """Get detailed summary for a specific run"""
    run = STORE["runs"].get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    
    doc = STORE["documents"].get(run["doc_id"])
    
    return {
        "run_id": run_id,
        "document": {
            "doc_id": run["doc_id"],
            "name": doc.get("name", "Unknown") if doc else "Unknown"
        },
        "status": run["status"],
        "started_at": run["started_at"],
        "completed_at": run.get("completed_at"),
        "stages": run["stages"],
        "hitl_required": run["hitl_required"],
        "audit_trail_count": len(run.get("audit_trail", [])),
        "policies_applied": len(run.get("policies", []))
    }


# ==================== Chatbot & Q&A ====================
@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_documents(chat_msg: ChatMessage):
    """Chat with legal documents - includes security monitoring"""
    from app.agents.chatbot import ChatbotAgent
    
    conversation_id = chat_msg.conversation_id or str(uuid.uuid4())
    
    # Get document context if specified
    document_context = None
    if chat_msg.document_ids:
        # Combine content from all specified documents
        combined_content = []
        for doc_id in chat_msg.document_ids:
            doc = STORE["documents"].get(doc_id)
            if doc:
                combined_content.append(doc["content"])
        
        if combined_content:
            document_context = {
                "content": "\n\n---\n\n".join(combined_content),
                "doc_ids": chat_msg.document_ids
            }
    
    # Initialize conversation if new
    if conversation_id not in STORE["conversations"]:
        STORE["conversations"][conversation_id] = {
            "conversation_id": conversation_id,
            "created_at": datetime.utcnow().isoformat(),
            "messages": [],
            "document_ids": chat_msg.document_ids or [],
            "security_events": []
        }
    
    # Process chat message
    chatbot = ChatbotAgent()
    result = chatbot.chat(
        message=chat_msg.message,
        document_context=document_context,
        conversation_id=conversation_id
    )
    
    # Store message
    message_entry = {
        "message": chat_msg.message,
        "response": result["response"],
        "blocked": result["blocked"],
        "security_scan": result["security_scan"],
        "timestamp": result["timestamp"]
    }
    
    STORE["conversations"][conversation_id]["messages"].append(message_entry)
    STORE["chat_messages"].append({
        **message_entry,
        "conversation_id": conversation_id
    })
    
    # Log security events
    if result["security_scan"]["threats_detected"]:
        security_event = {
            "conversation_id": conversation_id,
            "message": chat_msg.message,
            "threats": result["security_scan"]["threats"],
            "risk_score": result["security_scan"]["risk_score"],
            "timestamp": result["timestamp"]
        }
        STORE["conversations"][conversation_id]["security_events"].append(security_event)
        
        # Audit log
        STORE["audit_logs"].append({
            "timestamp": datetime.utcnow().isoformat(),
            "action": "chat_security_alert",
            "conversation_id": conversation_id,
            "threat_count": result["security_scan"]["threat_count"],
            "risk_score": result["security_scan"]["risk_score"]
        })
    
    return ChatResponse(
        response=result["response"],
        conversation_id=conversation_id,
        blocked=result["blocked"],
        security_scan=result["security_scan"],
        timestamp=result["timestamp"]
    )

@app.get("/api/chat/conversations")
async def list_conversations():
    """List all chat conversations"""
    return [
        {
            "conversation_id": conv_id,
            "created_at": conv["created_at"],
            "message_count": len(conv["messages"]),
            "security_events": len(conv["security_events"]),
            "document_ids": conv.get("document_ids", [])
        }
        for conv_id, conv in STORE["conversations"].items()
    ]

@app.get("/api/chat/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get conversation details"""
    conv = STORE["conversations"].get(conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv

@app.delete("/api/chat/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete a conversation"""
    if conversation_id in STORE["conversations"]:
        del STORE["conversations"][conversation_id]
        return {"status": "deleted"}
    raise HTTPException(status_code=404, detail="Conversation not found")

@app.get("/api/chat/security-events")
async def get_chat_security_events():
    """Get all chat security events"""
    events = []
    for conv_id, conv in STORE["conversations"].items():
        for event in conv.get("security_events", []):
            events.append({
                **event,
                "conversation_id": conv_id
            })
    return sorted(events, key=lambda x: x["timestamp"], reverse=True)


# ==================== Export & Artifacts ====================
@app.get("/api/export/run/{run_id}/redline")
async def export_redline(run_id: str, format: str = "md"):
    """Export redline document with tracked changes"""
    run = STORE["runs"].get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    
    drafter = run.get("stages", {}).get("drafter", {}).get("result", {})
    if not drafter:
        raise HTTPException(status_code=400, detail="Draft not available")
    
    redline_content = drafter.get("redline_document", "")
    
    return {
        "run_id": run_id,
        "format": format,
        "content": redline_content,
        "changes_count": drafter.get("changes_count", 0)
    }

@app.get("/api/export/run/{run_id}/final")
async def export_final(run_id: str):
    """Export final approved document"""
    run = STORE["runs"].get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    
    if run["status"] != "completed":
        raise HTTPException(status_code=400, detail="Run not completed")
    
    final_output = run.get("final_output", {})
    
    return {
        "run_id": run_id,
        "content": final_output.get("document", ""),
        "redactions_applied": final_output.get("redactions_count", 0),
        "risk_level": final_output.get("overall_risk", "unknown")
    }

