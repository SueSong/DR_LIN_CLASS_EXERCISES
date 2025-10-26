# Exercise 8: HITL Contract Redlining Orchestrator

**Week 5 - Multi-Agent Orchestration with Human-in-the-Loop**

A comprehensive legal document review system demonstrating advanced agentic patterns including Manager–Worker, Reviewer/Referee, Planner–Executor, Tool Router, and Blackboard orchestration with Human-in-the-Loop (HITL) approval gates.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [API Endpoints](#api-endpoints)
- [Frontend Pages](#frontend-pages)
- [Learning Objectives](#learning-objectives)
- [Implementation Guide](#implementation-guide)

---

## 🎯 Overview

This exercise builds a production-ready legal contract redlining system that:
- **Parses** legal documents (NDA, MSA, DPA) into clauses
- **Assesses** risk levels (HIGH/MEDIUM/LOW) against policy rules
- **Generates** redline proposals with rationale and policy references
- **Requires** human approval at two HITL gates (Risk Gate, Final Approval)
- **Exports** redlined documents in multiple formats (DOCX, PDF, Markdown)
- **Tracks** metrics, costs, and quality indicators
- **Supports** replay and debugging of agent workflows

---

## ✨ Key Features

### 🤖 **Agent Patterns**
- **Manager–Worker**: Task decomposition with parallel workers for clause parsing and risk tagging
- **Planner–Executor**: Multi-step sequential plans with replayable state and checkpoints
- **Reviewer/Referee**: Checklist-driven review with referee arbitration for contested clauses
- **Tool Router**: Policy lookup vs LLM-based analysis routing
- **Blackboard**: Centralized shared memory for agent coordination

### 🚦 **HITL Gates**
- **Risk Gate**: Human approval for high-risk clauses before proceeding
- **Final Approval Gate**: Review and approve all redline proposals before export
- **Soft Gates**: Optional human checkpoints for quality assurance

### 📊 **Observability**
- Real-time agent timeline and execution trace
- Cost tracking per run, document, and agent path
- Quality metrics (pass rate, precision, mitigation rate)
- SLO monitoring (latency, quality, cost)
- Replay functionality for debugging

### 📝 **Document Management**
- Upload contracts (PDF, DOCX, Markdown, TXT)
- Create and manage policy playbooks
- Export redlined documents in multiple formats
- Track document processing history

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (Next.js)                    │
│  ┌─────────┬─────────┬──────┬──────┬─────────┬────────┐   │
│  │Documents│Playbooks│ Run  │ HITL │Finalize │Reports │   │
│  └─────────┴─────────┴──────┴──────┴─────────┴────────┘   │
└───────────────────────┬─────────────────────────────────────┘
                        │ HTTP/REST API
┌───────────────────────▼─────────────────────────────────────┐
│                     Backend (FastAPI)                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Orchestration Layer                      │  │
│  │  ┌────────────┬──────────────┬─────────────────┐    │  │
│  │  │  Manager   │  Planner     │   Reviewer      │    │  │
│  │  │  Agent     │  Agent       │   Agent         │    │  │
│  │  └────────────┴──────────────┴─────────────────┘    │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Blackboard (Shared Memory)               │  │
│  │  • Clauses  • Assessments  • Proposals  • History    │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                    Tools Layer                        │  │
│  │  • Clause Parser  • Risk Analyzer  • Redline Gen     │  │
│  │  • Policy Lookup  • Document Export                  │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
exercise_8/
├── backend/                      # FastAPI backend server
│   ├── app/
│   │   └── main.py              # Main FastAPI application
│   │       • Run orchestration endpoints
│   │       • HITL gate endpoints (risk, final approval)
│   │       • Blackboard API (shared memory)
│   │       • Document upload/list
│   │       • Playbook CRUD
│   │       • Export redline (DOCX/PDF/MD)
│   │       • Reports and metrics
│   │       • Replay functionality
│   ├── requirements.txt         # Python dependencies
│   │   • fastapi, uvicorn
│   │   • pydantic, pydantic-settings
│   │   • httpx (for external calls)
│   │   • python-multipart (file uploads)
│   └── Dockerfile              # Backend container config
│
├── frontend/                    # Next.js frontend application
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx      # Root layout with navigation
│   │   │   ├── page.tsx        # Home page (dashboard)
│   │   │   │   • Feature cards
│   │   │   │   • Quick start guide
│   │   │   │   • Agent patterns overview
│   │   │   │
│   │   │   ├── documents/
│   │   │   │   └── page.tsx    # Document management
│   │   │   │       • Upload documents (drag & drop)
│   │   │   │       • List uploaded documents
│   │   │   │       • View/delete documents
│   │   │   │       • Mock data: 3 pre-loaded docs
│   │   │   │
│   │   │   ├── playbooks/
│   │   │   │   └── page.tsx    # Playbook management
│   │   │   │       • Create playbooks (JSON rules)
│   │   │   │       • List existing playbooks
│   │   │   │       • View/edit/delete playbooks
│   │   │   │       • Example templates
│   │   │   │
│   │   │   ├── run/
│   │   │   │   ├── page.tsx    # Run configuration
│   │   │   │   │   • Select document
│   │   │   │   │   • Choose agent path
│   │   │   │   │   • Select playbook (optional)
│   │   │   │   │   • Start review workflow
│   │   │   │   │
│   │   │   │   └── [id]/
│   │   │   │       └── page.tsx # Run detail view
│   │   │   │           • Summary cards (doc, agent, score, status)
│   │   │   │           • Agent timeline
│   │   │   │           • Risk assessments table
│   │   │   │           • Redline proposals
│   │   │   │
│   │   │   ├── hitl/
│   │   │   │   └── page.tsx    # Risk Gate (HITL)
│   │   │   │       • Pending runs list
│   │   │   │       • 8 risk assessments (1H, 3M, 4L)
│   │   │   │       • Clause text, rationale, impact
│   │   │   │       • Approve/reject each clause
│   │   │   │       • Comments per clause
│   │   │   │       • Submit risk approval
│   │   │   │
│   │   │   ├── finalize/
│   │   │   │   └── page.tsx    # Final Approval Gate
│   │   │   │       • Pending reviews list
│   │   │   │       • Executive summary
│   │   │   │       • 5 redline proposals (before/after)
│   │   │   │       • Approve/reject proposals
│   │   │   │       • Final approval notes
│   │   │   │       • Export options (DOCX/PDF/MD)
│   │   │   │       • Download links
│   │   │   │
│   │   │   ├── replay/
│   │   │   │   └── page.tsx    # Replay & Debug
│   │   │   │       • Run selection
│   │   │   │       • Step-by-step trace
│   │   │   │       • Edit inputs (what-if)
│   │   │   │       • Replay comparison
│   │   │   │       • Mock trace data
│   │   │   │
│   │   │   └── reports/
│   │   │       └── page.tsx    # Reports & Analytics
│   │   │           • Summary cards (runs, success, score, cost)
│   │   │           • Latency distribution (P50/P95/P99)
│   │   │           • Quality metrics
│   │   │           • Agent path comparison
│   │   │           • Recent runs list
│   │   │           • SLO status
│   │   │
│   │   ├── components/
│   │   │   └── Navigation.tsx  # Top navigation bar
│   │   │       • Links to all pages
│   │   │       • Active page highlighting
│   │   │
│   │   └── lib/
│   │       └── api.ts          # API client functions
│   │           • Document APIs (upload, list)
│   │           • Playbook APIs (create, list, delete)
│   │           • Run APIs (start, get, list)
│   │           • HITL APIs (risk approve, final approve)
│   │           • Export APIs (redline)
│   │           • Blackboard APIs (get state)
│   │
│   ├── package.json            # Frontend dependencies
│   │   • next, react, react-dom
│   │   • axios (HTTP client)
│   │   • lucide-react (icons)
│   │   • tailwindcss (styling)
│   │   • react-dropzone (file upload)
│   │   • react-markdown (rendering)
│   │
│   ├── tailwind.config.ts      # Tailwind CSS configuration
│   ├── tsconfig.json           # TypeScript configuration
│   └── Dockerfile              # Frontend container config
│
├── data/                        # Sample data for classroom
│   ├── contracts/
│   │   └── nda.md              # Sample NDA contract (Markdown)
│   ├── policies/
│   │   └── policy_book.json    # Sample policy rules
│   │       • Liability caps
│   │       • Data retention
│   │       • Indemnity exclusions
│   │       • Required clauses
│   └── checklists/
│       └── reviewer.yaml       # Reviewer checklist
│
├── docker-compose.yml          # Docker orchestration
│   • Backend service (port 8004)
│   • Frontend service (port 3004)
│   • Volume mounts for development
│
└── README.md                   # This file
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.11+** (for backend)
- **Node.js 20+** (for frontend)
- **Docker & Docker Compose** (optional, for containerized setup)

### Option 1: Local Development (Recommended for Students)

#### **1. Start Backend**

```bash
# Navigate to backend directory
cd exercise_8/backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start FastAPI server
uvicorn app.main:app --reload --port 8004
```

Backend will be available at: **http://localhost:8004**
- API docs: http://localhost:8004/docs
- Health check: http://localhost:8004/health

#### **2. Start Frontend** (in a new terminal)

```bash
# Navigate to frontend directory
cd exercise_8/frontend

# Install dependencies
npm install

# Start Next.js development server
npm run dev -- --port 3004
```

Frontend will be available at: **http://localhost:3004**

### Option 2: Docker Compose (Production-like)

```bash
# From exercise_8 directory
docker-compose up --build

# Or run in background
docker-compose up -d --build

# Stop services
docker-compose down
```

Services:
- **Frontend**: http://localhost:3004
- **Backend**: http://localhost:8004

---

## 🔌 API Endpoints

### **Run Orchestration**
```
POST   /api/run                    # Start a new review run
GET    /api/run/{run_id}           # Get run details
GET    /api/runs                   # List all runs
```

### **Document Management**
```
POST   /api/documents              # Upload document
GET    /api/documents              # List documents
GET    /api/documents/{doc_id}     # Get document
DELETE /api/documents/{doc_id}     # Delete document
```

### **Playbook Management**
```
POST   /api/playbooks              # Create playbook
GET    /api/playbooks              # List playbooks
GET    /api/playbooks/{id}         # Get playbook
DELETE /api/playbooks/{id}         # Delete playbook
```

### **HITL Gates**
```
POST   /api/hitl/risk-approve      # Approve/reject risk assessments
POST   /api/hitl/final-approve     # Final approval for redlines
GET    /api/blackboard/{run_id}    # Get shared state
```

### **Export**
```
POST   /api/export/redline         # Export redlined document
                                    # Formats: docx, pdf, md
```

### **Reports & Analytics**
```
GET    /api/reports/slos           # Get SLO metrics
GET    /api/reports/performance    # Performance metrics
GET    /api/reports/quality        # Quality metrics
GET    /api/reports/cost           # Cost analysis
```

### **Replay & Debug**
```
GET    /api/replay/{run_id}        # Get replay data
POST   /api/replay/{run_id}        # Replay with modifications
```

---

## 🖥️ Frontend Pages

### **Home** (`/`)
Dashboard with feature cards, quick start guide, and agent patterns overview.

### **Documents** (`/documents`)
- Upload documents via drag & drop
- View uploaded documents with metadata
- Delete documents
- **Mock Data**: 3 pre-loaded documents

### **Playbooks** (`/playbooks`)
- Create policy playbooks (JSON format)
- View and edit existing playbooks
- Delete playbooks
- Example templates provided

### **Run Configuration** (`/run`)
- Select document to review
- Choose agent path (Manager–Worker, Planner–Executor, Reviewer/Referee)
- Select optional playbook
- Start review workflow

### **Run Detail** (`/run/[id]`)
- Summary cards (document, agent, score, status)
- Agent timeline with step-by-step execution
- Risk assessments table
- Redline proposals

### **Risk Gate (HITL)** (`/hitl`)
- Pending runs awaiting risk approval
- 8 risk assessments (1 HIGH, 3 MEDIUM, 4 LOW)
- Clause text, risk rationale, impact assessment
- Approve/reject each clause
- Add comments per clause
- Submit risk approval

### **Final Approval Gate** (`/finalize`)
- Pending reviews awaiting final approval
- Executive summary with recommendations
- 5 detailed redline proposals (before/after comparison)
- Approve/reject each proposal
- Final approval notes
- Export options (DOCX, PDF, Markdown)
- Download links for generated files

### **Replay & Debug** (`/replay`)
- Select previous run
- View step-by-step execution trace
- Edit inputs for what-if scenarios
- Replay with modifications
- Compare original vs replay results

### **Reports & Analytics** (`/reports`)
- Summary metrics (runs, success rate, avg score, cost)
- Latency distribution (P50, P95, P99)
- Quality metrics (pass rate, precision, mitigation rate)
- Agent path performance comparison
- Recent runs list
- SLO status (latency, quality, cost)

---

## 🎓 Learning Objectives

### **Week 5 Focus Areas**

1. **Multi-Agent Orchestration**
   - Implement Manager–Worker pattern for parallel task execution
   - Build Planner–Executor with replayable state
   - Create Reviewer/Referee with checklist-driven validation

2. **Human-in-the-Loop (HITL)**
   - Design approval gates for high-risk decisions
   - Implement soft gates for quality assurance
   - Track human decisions and rationale

3. **Blackboard Pattern**
   - Centralized shared memory for agent coordination
   - State management across multiple agents
   - Conflict resolution and consensus building

4. **Tool Routing**
   - Rule-based vs LLM-based tool selection
   - Policy lookup optimization
   - Dynamic tool composition

5. **Observability & Debugging**
   - Trace agent execution paths
   - Cost tracking per operation
   - Quality metrics and SLOs
   - Replay functionality for debugging

6. **Production Patterns**
   - Error handling and recovery
   - Idempotency and retry logic
   - Circuit breakers for external calls
   - Rate limiting and throttling

---

## 🛠️ Implementation Guide

### **For Students**

The current implementation includes:
- ✅ **Complete UI** with mock data
- ✅ **All frontend pages** fully functional
- ✅ **Navigation** between pages
- ✅ **Mock workflows** for testing

**Your Task**: Implement the backend logic to replace mock data with real functionality.

### **Backend Implementation Steps**

1. **Document Processing**
   - Parse uploaded documents into clauses
   - Extract clause headings and text
   - Store in blackboard

2. **Risk Assessment**
   - Analyze each clause against policy rules
   - Assign risk levels (HIGH/MEDIUM/LOW)
   - Generate rationale and policy references

3. **Redline Generation**
   - Create redline proposals for risky clauses
   - Generate before/after text
   - Include rationale and policy references

4. **HITL Gates**
   - Implement risk approval workflow
   - Track human decisions
   - Implement final approval workflow

5. **Export**
   - Generate DOCX with redlines
   - Generate PDF summary memo
   - Generate CSV decision card

6. **Metrics & Reporting**
   - Track latency per run
   - Calculate cost per operation
   - Compute quality metrics
   - Store historical data

### **Agent Implementation Patterns**

#### **Manager–Worker**
```python
# Manager decomposes task
clauses = parse_document(doc)
tasks = [{"clause": c, "policy": p} for c in clauses]

# Workers process in parallel
with ThreadPoolExecutor() as executor:
    results = executor.map(assess_risk, tasks)
```

#### **Planner–Executor**
```python
# Planner creates multi-step plan
plan = [
    {"step": "parse", "agent": "parser"},
    {"step": "assess", "agent": "risk_analyzer"},
    {"step": "redline", "agent": "redline_gen"},
]

# Executor runs plan with checkpoints
for step in plan:
    result = execute_step(step)
    blackboard.save_checkpoint(step, result)
```

#### **Reviewer/Referee**
```python
# Reviewer checks against checklist
for item in checklist:
    result = review_clause(clause, item)
    if result.contested:
        # Referee arbitrates
        decision = referee.arbitrate(clause, result)
```

---

## 📊 Mock Data Overview

The frontend currently uses mock data to demonstrate functionality:

- **Documents**: 3 sample contracts (SaaS MSA, NDA, DPA)
- **Playbooks**: 2 policy playbooks (SaaS, GDPR)
- **Risk Assessments**: 8 clauses (1 HIGH, 3 MEDIUM, 4 LOW)
- **Redline Proposals**: 5 detailed proposals with before/after
- **Run History**: 4-step agent timeline
- **Reports**: Complete metrics and analytics

All mock data includes realistic legal contract language and policy references for educational purposes.

---

## 🔍 Key Concepts

### **Blackboard Pattern**
Centralized shared memory where agents read/write state:
```python
blackboard = {
    "clauses": [...],
    "assessments": [...],
    "proposals": [...],
    "history": [...],
}
```

### **HITL Gates**
Human approval checkpoints:
- **Risk Gate**: Review high-risk clauses before proceeding
- **Final Gate**: Approve all redlines before export
- **Soft Gate**: Optional quality checks

### **Agent Coordination**
Multiple agents working together:
- **Parser Agent**: Extract clauses from document
- **Risk Analyzer**: Assess risk levels
- **Redline Generator**: Create redline proposals
- **Reviewer Agent**: Validate against checklist
- **Referee Agent**: Arbitrate contested decisions

---

## 📝 Notes

- **In-Memory State**: Blackboard is in-memory for classroom simplicity. Replace with database (PostgreSQL, Redis) for production.
- **Mock Data**: Frontend uses mock data to work standalone. Implement backend APIs to replace mocks.
- **Sample Contracts**: All legal documents are safe classroom samples, not real contracts.
- **Policy Rules**: Example policies demonstrate concepts, not actual legal requirements.
- **Cost Tracking**: Mock cost calculations for demonstration. Integrate with actual LLM providers for real costs.

---

## 🎯 Success Criteria

Students should be able to:
1. ✅ Upload a legal contract
2. ✅ Create a policy playbook
3. ✅ Start a review run with agent path selection
4. ✅ Approve/reject clauses at Risk Gate
5. ✅ Approve/reject proposals at Final Gate
6. ✅ Export redlined document
7. ✅ View metrics and reports
8. ✅ Replay previous runs for debugging

---

## 🤝 Support

For questions or issues:
- Check the API documentation at http://localhost:8004/docs
- Review mock data in frontend pages for expected data structures
- Examine `data/` directory for sample contracts and policies

---

## 📚 Additional Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Next.js Docs**: https://nextjs.org/docs
- **Tailwind CSS**: https://tailwindcss.com/docs
- **Agent Patterns**: See course materials for detailed pattern explanations

---

**Happy Coding! 🚀**