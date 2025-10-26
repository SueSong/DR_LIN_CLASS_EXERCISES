# Multi-Agent Orchestration Framework

This framework provides a clean, educational structure for building multi-agent systems with the Blackboard pattern.

## 📚 Core Concepts

### **Agent**
An individual worker with specific capabilities. Each agent can:
- Execute tasks independently
- Read from and write to the shared Blackboard
- Report its status and results

### **Team**
A collection of agents working together. Teams support different execution patterns:
- **Sequential**: Agents execute one after another
- **Parallel**: Agents execute simultaneously  
- **Manager-Worker**: Manager delegates to workers
- **Pipeline**: Output of one agent feeds into next

### **Coordinator**
Orchestrates the entire workflow. The Coordinator:
- Manages the Blackboard (shared memory)
- Routes tasks to appropriate teams
- Tracks execution history
- Handles HITL (Human-in-the-Loop) gates
- Maintains run state

### **Blackboard**
Shared memory accessible to all agents. Contains:
- Document text and metadata
- Parsed clauses
- Risk assessments
- Redline proposals
- Execution history

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Coordinator                          │
│  • Manages Blackboard (shared memory)                   │
│  • Routes tasks to teams                                │
│  • Handles HITL gates                                   │
└───────────────────┬─────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
┌───────▼────────┐      ┌──────▼───────┐
│  Sequential    │      │ Manager-     │
│  Team          │      │ Worker Team  │
│  ┌──────────┐ │      │ ┌──────────┐ │
│  │ Parser   │ │      │ │ Manager  │ │
│  │ Agent    │ │      │ │ Agent    │ │
│  └────┬─────┘ │      │ └────┬─────┘ │
│       │       │      │      │       │
│  ┌────▼─────┐ │      │ ┌────▼─────┐ │
│  │ Risk     │ │      │ │ Worker 1 │ │
│  │ Analyzer │ │      │ │ Worker 2 │ │
│  └────┬─────┘ │      │ │ Worker 3 │ │
│       │       │      │ └──────────┘ │
│  ┌────▼─────┐ │      └──────────────┘
│  │ Redline  │ │
│  │ Generator│ │
│  └──────────┘ │
└────────────────┘

         │
         ▼
┌─────────────────────────────────────┐
│         Blackboard                  │
│  • clauses: [...]                   │
│  • assessments: [...]               │
│  • proposals: [...]                 │
│  • history: [...]                   │
└─────────────────────────────────────┘
```

---

## 📁 File Structure

```
app/agents/
├── __init__.py           # Package exports
├── agent.py              # Agent base class + example agents
├── team.py               # Team class with execution patterns
├── coordinator.py        # Coordinator for orchestration
└── README.md            # This file
```

---

## 🚀 Quick Start

### 1. Create Agents

```python
from app.agents.agent import Agent, AgentStatus, AgentResult

class MyCustomAgent(Agent):
    def __init__(self):
        super().__init__(
            name="my_agent",
            role="custom_processor",
            capabilities=["process_data", "analyze"],
            description="Does custom processing"
        )
    
    def execute(self, task: Dict[str, Any], blackboard: Dict[str, Any]) -> AgentResult:
        self.status = AgentStatus.RUNNING
        
        try:
            # Do your work here
            data = task.get("data")
            result = self._process(data)
            
            # Write to blackboard
            blackboard["my_results"] = result
            
            self.status = AgentStatus.SUCCESS
            return AgentResult(
                agent_name=self.name,
                status=AgentStatus.SUCCESS,
                output={"processed": len(result)}
            )
        except Exception as e:
            self.status = AgentStatus.FAILED
            return AgentResult(
                agent_name=self.name,
                status=AgentStatus.FAILED,
                error=str(e)
            )
```

### 2. Create a Team

```python
from app.agents.team import Team, TeamPattern
from app.agents.agent import ParserAgent, RiskAnalyzerAgent, RedlineGeneratorAgent

# Create team
team = Team(
    name="review_team",
    pattern=TeamPattern.SEQUENTIAL
)

# Add agents
team.add_agent(ParserAgent())
team.add_agent(RiskAnalyzerAgent())
team.add_agent(RedlineGeneratorAgent())

# Execute team
task = {"type": "review_document", "document_text": "..."}
blackboard = {}
result = team.execute(task, blackboard)
```

### 3. Use the Coordinator

```python
from app.agents import Coordinator

# Initialize coordinator
coordinator = Coordinator()

# Register team
coordinator.register_team(team)

# Start a run
run_id = coordinator.start_run(
    doc_id="doc_001",
    document_text="...",
    agent_path="sequential"
)

# Get results
blackboard = coordinator.get_blackboard(run_id)
print(blackboard["assessments"])
```

---

## 🎓 Student Tasks

### **Task 1: Implement Agent Logic**

Complete the TODOs in the example agents:

1. **ParserAgent**: 
   - Parse documents into structured clauses
   - Extract clause headings and IDs
   - Handle different formats (PDF, DOCX, MD)

2. **RiskAnalyzerAgent**:
   - Implement sophisticated risk assessment
   - Compare clauses against policy rules
   - Generate detailed rationale

3. **RedlineGeneratorAgent**:
   - Create meaningful redline proposals
   - Generate before/after text
   - Reference applicable policies

### **Task 2: Create New Agents**

Implement additional agents:

```python
class ReviewerAgent(Agent):
    """
    Validates clauses against a checklist.
    
    TODO:
    - Load checklist from YAML
    - Check each clause against checklist items
    - Flag violations
    """
    pass

class RefereeAgent(Agent):
    """
    Arbitrates contested decisions.
    
    TODO:
    - Identify conflicting assessments
    - Apply tiebreaker logic
    - Generate consensus decision
    """
    pass
```

### **Task 3: Implement Parallel Execution**

Update `Team._execute_parallel()` to use threading or asyncio:

```python
from concurrent.futures import ThreadPoolExecutor

def _execute_parallel(self, task, blackboard):
    with ThreadPoolExecutor(max_workers=len(self.agents)) as executor:
        futures = [
            executor.submit(agent.execute, task, blackboard)
            for agent in self.agents
        ]
        results = [future.result() for future in futures]
    
    return {
        "team": self.name,
        "pattern": self.pattern.value,
        "results": [r.dict() for r in results],
        "success": all(r.status == AgentStatus.SUCCESS for r in results)
    }
```

### **Task 4: Implement Manager-Worker Pattern**

Create a proper manager agent:

```python
class ManagerAgent(Agent):
    """
    Decomposes tasks and delegates to workers.
    """
    def execute(self, task, blackboard):
        # Decompose document into chunks
        clauses = self._split_into_clauses(task["document_text"])
        
        # Create subtasks for workers
        blackboard["subtasks"] = [
            {"clause": clause, "task_type": "assess_risk"}
            for clause in clauses
        ]
        
        return AgentResult(
            agent_name=self.name,
            status=AgentStatus.SUCCESS,
            output={"subtask_count": len(clauses)}
        )
```

### **Task 5: Add Checkpoints**

Implement checkpoint/snapshot functionality:

```python
class Coordinator:
    def save_checkpoint(self, run_id: str, step: str):
        """Save blackboard snapshot at checkpoint"""
        blackboard = self.blackboards[run_id]
        
        if "checkpoints" not in blackboard:
            blackboard["checkpoints"] = []
        
        blackboard["checkpoints"].append({
            "step": step,
            "timestamp": datetime.now().isoformat(),
            "state": blackboard.copy()
        })
    
    def restore_checkpoint(self, run_id: str, checkpoint_index: int):
        """Restore blackboard to a previous checkpoint"""
        blackboard = self.blackboards[run_id]
        checkpoint = blackboard["checkpoints"][checkpoint_index]
        self.blackboards[run_id] = checkpoint["state"].copy()
```

---

## 🔍 Example Workflow

Here's how a complete document review works:

```python
# 1. Initialize coordinator
coordinator = Coordinator()

# 2. Create and register team
team = Team("review_team", TeamPattern.SEQUENTIAL)
team.add_agent(ParserAgent())
team.add_agent(RiskAnalyzerAgent())
team.add_agent(RedlineGeneratorAgent())
coordinator.register_team(team)

# 3. Start run
run_id = coordinator.start_run(
    doc_id="doc_001",
    document_text="[Full contract text...]",
    agent_path="sequential",
    policy_rules={"liability_cap": "12 months fees"}
)

# 4. Agents execute automatically:
#    - ParserAgent: Extracts clauses -> writes to blackboard["clauses"]
#    - RiskAnalyzerAgent: Assesses risk -> writes to blackboard["assessments"]
#    - RedlineGeneratorAgent: Creates proposals -> writes to blackboard["proposals"]

# 5. Check if HITL approval needed
run = coordinator.get_run(run_id)
if run["status"] == "awaiting_risk_approval":
    # Human reviews high-risk clauses
    coordinator.approve_risk(
        run_id=run_id,
        approved_clauses=["clause_1", "clause_2"],
        rejected_clauses=["clause_3"]
    )

# 6. Final approval
if run["status"] == "awaiting_final_approval":
    coordinator.approve_final(
        run_id=run_id,
        approved_proposals=["prop_1", "prop_2"],
        rejected_proposals=[]
    )

# 7. Get final results
blackboard = coordinator.get_blackboard(run_id)
print(f"Clauses: {len(blackboard['clauses'])}")
print(f"Assessments: {len(blackboard['assessments'])}")
print(f"Proposals: {len(blackboard['proposals'])}")
```

---

## 📊 Blackboard Schema

The blackboard follows this structure:

```python
{
    "run_id": "run_20250107_123456_doc_001",
    "doc_id": "doc_001",
    "document_text": "...",
    "agent_path": "sequential",
    "playbook_id": "playbook_001",
    "policy_rules": {...},
    
    # Agent outputs
    "clauses": [
        {
            "clause_id": "clause_1",
            "heading": "Limitation of Liability",
            "text": "..."
        }
    ],
    "assessments": [
        {
            "clause_id": "clause_1",
            "risk_level": "HIGH",
            "rationale": "...",
            "policy_refs": ["POL-001"]
        }
    ],
    "proposals": [
        {
            "clause_id": "clause_1",
            "original_text": "...",
            "proposed_text": "...",
            "rationale": "...",
            "variant": "conservative"
        }
    ],
    
    # Execution tracking
    "history": [
        {
            "step": "parser_execution",
            "agent": "parser",
            "status": "success",
            "timestamp": "2025-01-07T12:34:56"
        }
    ],
    
    # HITL approvals
    "risk_approval": {
        "approved": ["clause_1"],
        "rejected": ["clause_2"],
        "comments": {...},
        "timestamp": "..."
    },
    "final_approval": {
        "approved": ["prop_1"],
        "rejected": [],
        "notes": "...",
        "timestamp": "..."
    }
}
```

---

## 🎯 Best Practices

1. **Agent Design**
   - Keep agents focused on single responsibility
   - Use descriptive capability names
   - Always return AgentResult with proper status

2. **Team Organization**
   - Choose appropriate pattern for your use case
   - Sequential: When order matters
   - Parallel: When agents are independent
   - Manager-Worker: When task decomposition is needed

3. **Blackboard Usage**
   - Use clear, consistent key names
   - Document your blackboard schema
   - Don't overwrite other agents' data

4. **Error Handling**
   - Always catch exceptions in agent.execute()
   - Return FAILED status with error message
   - Log errors to history

5. **Testing**
   - Test agents individually first
   - Then test teams
   - Finally test full coordinator workflow

---

## 🔧 Debugging Tips

### View Team Info
```python
team_info = team.get_info()
print(f"Team: {team_info['name']}")
print(f"Agents: {len(team_info['agents'])}")
print(f"Capabilities: {team_info['capabilities']}")
```

### View Blackboard History
```python
blackboard = coordinator.get_blackboard(run_id)
for step in blackboard["history"]:
    print(f"{step['timestamp']}: {step['step']} - {step['status']}")
```

### Check Coordinator Stats
```python
stats = coordinator.get_stats()
print(f"Total runs: {stats['total_runs']}")
print(f"Teams: {stats['registered_teams']}")
print(f"By status: {stats['runs_by_status']}")
```

---

## 📚 Further Reading

- **Blackboard Pattern**: https://en.wikipedia.org/wiki/Blackboard_(design_pattern)
- **Multi-Agent Systems**: https://en.wikipedia.org/wiki/Multi-agent_system
- **Manager-Worker Pattern**: https://en.wikipedia.org/wiki/Master%E2%80%93slave_(technology)

---

**Happy Coding! 🚀**
