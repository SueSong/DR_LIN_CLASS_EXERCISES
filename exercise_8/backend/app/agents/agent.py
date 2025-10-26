"""
Agent Base Class

An Agent represents an individual worker with specific capabilities.
Each agent can:
- Execute tasks independently
- Read from and write to the shared Blackboard
- Report its status and results
"""

from typing import Dict, Any, Optional, List
from enum import Enum
from pydantic import BaseModel, Field


class AgentStatus(str, Enum):
    """Agent execution status"""
    IDLE = "idle"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    WAITING = "waiting"


class AgentResult(BaseModel):
    """Result of agent execution"""
    agent_name: str
    status: AgentStatus
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time_ms: Optional[float] = None


class Agent:
    """
    Base Agent class for multi-agent orchestration.
    
    Students should inherit from this class to create specialized agents:
    - ParserAgent: Extracts clauses from documents
    - RiskAnalyzerAgent: Assesses risk levels
    - RedlineGeneratorAgent: Creates redline proposals
    - ReviewerAgent: Validates against checklists
    - RefereeAgent: Arbitrates contested decisions
    
    Example:
        class ParserAgent(Agent):
            def __init__(self):
                super().__init__(
                    name="parser",
                    role="document_parser",
                    capabilities=["parse_clauses", "extract_headings"]
                )
            
            def execute(self, task: Dict[str, Any], blackboard: Dict[str, Any]) -> AgentResult:
                # Parse document into clauses
                doc_text = task.get("document_text")
                clauses = self._parse_clauses(doc_text)
                
                # Write to blackboard
                blackboard["clauses"] = clauses
                
                return AgentResult(
                    agent_name=self.name,
                    status=AgentStatus.SUCCESS,
                    output={"clause_count": len(clauses)}
                )
    """
    
    def __init__(
        self,
        name: str,
        role: str,
        capabilities: List[str],
        description: Optional[str] = None
    ):
        """
        Initialize an Agent.
        
        Args:
            name: Unique identifier for this agent
            role: The agent's role (e.g., "parser", "risk_analyzer")
            capabilities: List of capabilities this agent has
            description: Optional description of what this agent does
        """
        self.name = name
        self.role = role
        self.capabilities = capabilities
        self.description = description or f"Agent: {name}"
        self.status = AgentStatus.IDLE
    
    def can_handle(self, task_type: str) -> bool:
        """
        Check if this agent can handle a specific task type.
        
        Args:
            task_type: The type of task to check
            
        Returns:
            True if this agent has the capability to handle this task
        """
        return task_type in self.capabilities
    
    def execute(self, task: Dict[str, Any], blackboard: Dict[str, Any]) -> AgentResult:
        """
        Execute a task. This method should be overridden by subclasses.
        
        Args:
            task: Task specification with parameters
            blackboard: Shared state/memory accessible to all agents
            
        Returns:
            AgentResult with execution status and output
            
        Raises:
            NotImplementedError: If not overridden by subclass
        """
        raise NotImplementedError(
            f"Agent {self.name} must implement the execute() method"
        )
    
    def validate_task(self, task: Dict[str, Any]) -> bool:
        """
        Validate that a task has all required parameters.
        Override this method to add custom validation.
        
        Args:
            task: Task specification to validate
            
        Returns:
            True if task is valid, False otherwise
        """
        return "type" in task
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get agent information for debugging/monitoring.
        
        Returns:
            Dictionary with agent metadata
        """
        return {
            "name": self.name,
            "role": self.role,
            "capabilities": self.capabilities,
            "description": self.description,
            "status": self.status.value
        }


# Example Agent Implementations (Students should complete these)

class ParserAgent(Agent):
    """
    Parses legal documents into structured clauses.
    
    TODO for students:
    - Implement clause extraction logic
    - Handle different document formats (PDF, DOCX, MD)
    - Extract clause headings and IDs
    """
    
    def __init__(self):
        super().__init__(
            name="parser",
            role="document_parser",
            capabilities=["parse_clauses", "extract_headings"],
            description="Extracts clauses from legal documents"
        )
    
    def execute(self, task: Dict[str, Any], blackboard: Dict[str, Any]) -> AgentResult:
        """
        Parse document into clauses.
        
        Expected task format:
        {
            "type": "parse_clauses",
            "document_text": "...",
            "document_id": "doc_001"
        }
        """
        self.status = AgentStatus.RUNNING
        
        try:
            # TODO: Implement parsing logic
            # For now, return a simple example
            doc_text = task.get("document_text", "")
            
            # Example: Split by double newlines (students should improve this)
            clauses = [
                {
                    "clause_id": f"clause_{i+1}",
                    "heading": f"Section {i+1}",
                    "text": clause.strip()
                }
                for i, clause in enumerate(doc_text.split("\n\n"))
                if clause.strip()
            ]
            
            # Write to blackboard
            blackboard["clauses"] = clauses
            blackboard["document_id"] = task.get("document_id")
            
            self.status = AgentStatus.SUCCESS
            return AgentResult(
                agent_name=self.name,
                status=AgentStatus.SUCCESS,
                output={"clause_count": len(clauses)}
            )
            
        except Exception as e:
            self.status = AgentStatus.FAILED
            return AgentResult(
                agent_name=self.name,
                status=AgentStatus.FAILED,
                error=str(e)
            )


class RiskAnalyzerAgent(Agent):
    """
    Analyzes clauses for legal/business risks.
    
    TODO for students:
    - Implement risk assessment logic
    - Compare clauses against policy rules
    - Assign risk levels (HIGH/MEDIUM/LOW)
    - Generate rationale for each assessment
    """
    
    def __init__(self):
        super().__init__(
            name="risk_analyzer",
            role="risk_assessor",
            capabilities=["assess_risk", "policy_check"],
            description="Assesses legal and business risks in contract clauses"
        )
    
    def execute(self, task: Dict[str, Any], blackboard: Dict[str, Any]) -> AgentResult:
        """
        Assess risk levels for clauses.
        
        Expected task format:
        {
            "type": "assess_risk",
            "policy_rules": {...}
        }
        """
        self.status = AgentStatus.RUNNING
        
        try:
            # TODO: Implement risk assessment logic
            clauses = blackboard.get("clauses", [])
            policy_rules = task.get("policy_rules", {})
            
            assessments = []
            for clause in clauses:
                # Example: Simple keyword-based risk assessment
                # Students should implement more sophisticated logic
                risk_level = self._assess_clause_risk(clause, policy_rules)
                
                assessments.append({
                    "clause_id": clause["clause_id"],
                    "risk_level": risk_level,
                    "rationale": f"Assessment based on policy rules",
                    "policy_refs": []
                })
            
            # Write to blackboard
            blackboard["assessments"] = assessments
            
            self.status = AgentStatus.SUCCESS
            return AgentResult(
                agent_name=self.name,
                status=AgentStatus.SUCCESS,
                output={"assessment_count": len(assessments)}
            )
            
        except Exception as e:
            self.status = AgentStatus.FAILED
            return AgentResult(
                agent_name=self.name,
                status=AgentStatus.FAILED,
                error=str(e)
            )
    
    def _assess_clause_risk(self, clause: Dict[str, Any], policy_rules: Dict[str, Any]) -> str:
        """
        Assess risk level for a single clause.
        
        TODO: Implement sophisticated risk assessment
        """
        # Simple example - students should improve this
        text = clause.get("text", "").lower()
        
        if "unlimited" in text or "all damages" in text:
            return "HIGH"
        elif "indemnify" in text or "warranty" in text:
            return "MEDIUM"
        else:
            return "LOW"


class RedlineGeneratorAgent(Agent):
    """
    Generates redline proposals for risky clauses.
    
    TODO for students:
    - Implement redline generation logic
    - Create before/after text versions
    - Generate rationale for each change
    - Reference applicable policies
    """
    
    def __init__(self):
        super().__init__(
            name="redline_generator",
            role="redline_creator",
            capabilities=["generate_redlines", "create_proposals"],
            description="Creates redline proposals for contract improvements"
        )
    
    def execute(self, task: Dict[str, Any], blackboard: Dict[str, Any]) -> AgentResult:
        """
        Generate redline proposals.
        
        Expected task format:
        {
            "type": "generate_redlines",
            "policy_rules": {...}
        }
        """
        self.status = AgentStatus.RUNNING
        
        try:
            # TODO: Implement redline generation logic
            clauses = blackboard.get("clauses", [])
            assessments = blackboard.get("assessments", [])
            
            proposals = []
            for assessment in assessments:
                if assessment["risk_level"] in ["HIGH", "MEDIUM"]:
                    clause = next(
                        (c for c in clauses if c["clause_id"] == assessment["clause_id"]),
                        None
                    )
                    
                    if clause:
                        proposal = self._generate_proposal(clause, assessment)
                        proposals.append(proposal)
            
            # Write to blackboard
            blackboard["proposals"] = proposals
            
            self.status = AgentStatus.SUCCESS
            return AgentResult(
                agent_name=self.name,
                status=AgentStatus.SUCCESS,
                output={"proposal_count": len(proposals)}
            )
            
        except Exception as e:
            self.status = AgentStatus.FAILED
            return AgentResult(
                agent_name=self.name,
                status=AgentStatus.FAILED,
                error=str(e)
            )
    
    def _generate_proposal(self, clause: Dict[str, Any], assessment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a redline proposal for a single clause.
        
        TODO: Implement sophisticated redline generation
        """
        # Simple example - students should improve this
        return {
            "clause_id": clause["clause_id"],
            "original_text": clause["text"],
            "proposed_text": f"[REDLINED] {clause['text']}",
            "rationale": "Proposed change to mitigate risk",
            "variant": "conservative"
        }
