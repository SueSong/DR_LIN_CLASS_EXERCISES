"""
Multi-Agent Pipeline Orchestrator
Coordinates: Classifier → Extractor → Reviewer → Drafter
"""
from datetime import datetime
from typing import Dict, Any, List
from .classifier import ClassifierAgent
from .extractor import ExtractorAgent
from .reviewer import ReviewerAgent
from .drafter import DrafterAgent


def execute_pipeline(run_id: str, document: Dict[str, Any], policies: List[Dict[str, Any]], store: Dict[str, Any]):
    """
    Execute the full multi-agent pipeline
    """
    run = store["runs"][run_id]
    
    try:
        # Stage 1: Classifier - Determine document type and sensitivity
        run["audit_trail"].append({
            "timestamp": datetime.utcnow().isoformat(),
            "stage": "classifier",
            "action": "started"
        })
        
        classifier = ClassifierAgent()
        classification_result = classifier.classify(document, policies)
        
        run["stages"]["classifier"] = {
            "status": "completed",
            "result": classification_result,
            "completed_at": datetime.utcnow().isoformat()
        }
        
        run["audit_trail"].append({
            "timestamp": datetime.utcnow().isoformat(),
            "stage": "classifier",
            "action": "completed",
            "result": {
                "doc_type": classification_result.get("doc_type"),
                "sensitivity": classification_result.get("sensitivity_level")
            }
        })
        
        # Stage 2: Extractor - Extract clauses, PII, and entities
        run["audit_trail"].append({
            "timestamp": datetime.utcnow().isoformat(),
            "stage": "extractor",
            "action": "started"
        })
        
        extractor = ExtractorAgent()
        extraction_result = extractor.extract(document, classification_result, policies)
        
        run["stages"]["extractor"] = {
            "status": "completed",
            "result": extraction_result,
            "completed_at": datetime.utcnow().isoformat()
        }
        
        run["audit_trail"].append({
            "timestamp": datetime.utcnow().isoformat(),
            "stage": "extractor",
            "action": "completed",
            "result": {
                "clauses_found": len(extraction_result.get("clauses", [])),
                "pii_entities": len(extraction_result.get("pii_entities", []))
            }
        })
        
        # Check if HITL is needed for high-risk PII
        if extraction_result.get("requires_hitl", False):
            _create_hitl_request(run_id, "extractor", extraction_result, store)
            run["status"] = "awaiting_hitl"
            run["hitl_required"] = True
            return
        
        # Stage 3: Reviewer - Assess risks and policy compliance
        run["audit_trail"].append({
            "timestamp": datetime.utcnow().isoformat(),
            "stage": "reviewer",
            "action": "started"
        })
        
        reviewer = ReviewerAgent()
        review_result = reviewer.review(
            document,
            classification_result,
            extraction_result,
            policies
        )
        
        run["stages"]["reviewer"] = {
            "status": "completed",
            "result": review_result,
            "completed_at": datetime.utcnow().isoformat()
        }
        
        run["audit_trail"].append({
            "timestamp": datetime.utcnow().isoformat(),
            "stage": "reviewer",
            "action": "completed",
            "result": {
                "risk_level": review_result.get("overall_risk"),
                "policy_violations": len(review_result.get("policy_violations", [])),
                "recommendations": len(review_result.get("recommendations", []))
            }
        })
        
        # Check if HITL is needed for high risk
        if review_result.get("requires_hitl", False) or review_result.get("overall_risk") == "high":
            _create_hitl_request(run_id, "reviewer", review_result, store)
            run["status"] = "awaiting_hitl"
            run["hitl_required"] = True
            return
        
        # Stage 4: Drafter - Create redacted/edited version
        run["audit_trail"].append({
            "timestamp": datetime.utcnow().isoformat(),
            "stage": "drafter",
            "action": "started"
        })
        
        drafter = DrafterAgent()
        draft_result = drafter.draft(
            document,
            classification_result,
            extraction_result,
            review_result,
            policies
        )
        
        run["stages"]["drafter"] = {
            "status": "completed",
            "result": draft_result,
            "completed_at": datetime.utcnow().isoformat()
        }
        
        run["audit_trail"].append({
            "timestamp": datetime.utcnow().isoformat(),
            "stage": "drafter",
            "action": "completed",
            "result": {
                "changes_count": draft_result.get("changes_count", 0),
                "redactions_count": draft_result.get("redactions_count", 0)
            }
        })
        
        # Check if final HITL approval needed before external sharing
        if draft_result.get("requires_final_hitl", False):
            _create_hitl_request(run_id, "drafter", draft_result, store)
            run["status"] = "awaiting_hitl"
            run["hitl_required"] = True
            return
        
        # Pipeline completed
        run["status"] = "completed"
        run["completed_at"] = datetime.utcnow().isoformat()
        run["final_output"] = {
            "document": draft_result.get("final_document"),
            "redactions_count": draft_result.get("redactions_count"),
            "overall_risk": review_result.get("overall_risk")
        }
        
        run["audit_trail"].append({
            "timestamp": datetime.utcnow().isoformat(),
            "stage": "pipeline",
            "action": "completed"
        })
        
    except Exception as e:
        run["status"] = "failed"
        run["error"] = str(e)
        run["audit_trail"].append({
            "timestamp": datetime.utcnow().isoformat(),
            "stage": "pipeline",
            "action": "failed",
            "error": str(e)
        })


def continue_after_hitl(run_id: str, hitl_id: str, decisions: List[Any], store: Dict[str, Any]):
    """
    Continue pipeline execution after HITL approval
    """
    run = store["runs"][run_id]
    hitl = store["hitl_queue"][hitl_id]
    
    stage = hitl["stage"]
    
    # Apply HITL decisions to the stage results
    if stage in run["stages"]:
        run["stages"][stage]["result"]["hitl_decisions"] = [d.dict() for d in decisions]
    
    # Get the document and policies again
    document = store["documents"][run["doc_id"]]
    policies = run["policies"]
    
    # Resume from the next stage
    if stage == "extractor":
        # Continue to reviewer
        reviewer = ReviewerAgent()
        review_result = reviewer.review(
            document,
            run["stages"]["classifier"]["result"],
            run["stages"]["extractor"]["result"],
            policies
        )
        run["stages"]["reviewer"] = {
            "status": "completed",
            "result": review_result,
            "completed_at": datetime.utcnow().isoformat()
        }
        
        if review_result.get("requires_hitl", False):
            _create_hitl_request(run_id, "reviewer", review_result, store)
            return
        
    if stage in ["extractor", "reviewer"]:
        # Continue to drafter
        drafter = DrafterAgent()
        draft_result = drafter.draft(
            document,
            run["stages"]["classifier"]["result"],
            run["stages"]["extractor"]["result"],
            run["stages"]["reviewer"]["result"],
            policies
        )
        run["stages"]["drafter"] = {
            "status": "completed",
            "result": draft_result,
            "completed_at": datetime.utcnow().isoformat()
        }
        
        if draft_result.get("requires_final_hitl", False):
            _create_hitl_request(run_id, "drafter", draft_result, store)
            return
    
    # Complete the run
    run["status"] = "completed"
    run["completed_at"] = datetime.utcnow().isoformat()
    drafter_result = run["stages"]["drafter"]["result"]
    reviewer_result = run["stages"]["reviewer"]["result"]
    
    run["final_output"] = {
        "document": drafter_result.get("final_document"),
        "redactions_count": drafter_result.get("redactions_count"),
        "overall_risk": reviewer_result.get("overall_risk")
    }


def _create_hitl_request(run_id: str, stage: str, stage_result: Dict[str, Any], store: Dict[str, Any]):
    """
    Create a HITL (Human-in-the-Loop) request for approval
    """
    import uuid
    hitl_id = str(uuid.uuid4())
    
    # Extract items that need review based on stage
    items = []
    if stage == "extractor":
        items = stage_result.get("pii_entities", [])
    elif stage == "reviewer":
        items = stage_result.get("high_risk_items", [])
    elif stage == "drafter":
        items = stage_result.get("proposed_changes", [])
    
    store["hitl_queue"][hitl_id] = {
        "hitl_id": hitl_id,
        "run_id": run_id,
        "stage": stage,
        "items": items,
        "status": "pending",
        "created_at": datetime.utcnow().isoformat()
    }
    
    store["audit_logs"].append({
        "timestamp": datetime.utcnow().isoformat(),
        "action": "hitl_created",
        "hitl_id": hitl_id,
        "run_id": run_id,
        "stage": stage,
        "items_count": len(items)
    })

