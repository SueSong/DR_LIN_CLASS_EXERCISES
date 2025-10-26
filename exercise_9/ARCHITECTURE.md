# Architecture Documentation - Exercise 9

## System Overview

The Legal Document Review system implements a **multi-agent architecture** where specialized AI agents work sequentially to analyze, assess, and redact legal documents.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (Next.js/React)                │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │
│  │Documents │ │  Review  │ │   HITL   │ │ Red Team │      │
│  │   UI     │ │    UI    │ │   Queue  │ │   Tests  │      │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTP/REST API
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                        │
│  ┌───────────────────────────────────────────────────────┐ │
│  │                  API Layer                            │ │
│  │  /api/documents  /api/run  /api/hitl  /api/redteam  │ │
│  └───────────────────────────────────────────────────────┘ │
│                            │                                │
│  ┌───────────────────────────────────────────────────────┐ │
│  │              Multi-Agent Pipeline                     │ │
│  │                                                        │ │
│  │  ┌──────────┐      ┌──────────┐      ┌──────────┐   │ │
│  │  │Classifier│─────→│Extractor │─────→│ Reviewer │   │ │
│  │  │  Agent   │      │  Agent   │      │  Agent   │   │ │
│  │  └──────────┘      └──────────┘      └──────────┘   │ │
│  │       │                  │                  │         │ │
│  │       │                  ▼                  │         │ │
│  │       │            ┌──────────┐             │         │ │
│  │       │            │   HITL   │◄────────────┘         │ │
│  │       │            │  Check   │                       │ │
│  │       │            └──────────┘                       │ │
│  │       │                  │                            │ │
│  │       └──────────────────┴──────────────┐             │ │
│  │                                         ▼             │ │
│  │                                   ┌──────────┐        │ │
│  │                                   │ Drafter  │        │ │
│  │                                   │  Agent   │        │ │
│  │                                   └──────────┘        │ │
│  └───────────────────────────────────────────────────────┘ │
│                            │                                │
│  ┌───────────────────────────────────────────────────────┐ │
│  │               Supporting Modules                      │ │
│  │                                                        │ │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐     │ │
│  │  │    PII     │  │   Policy   │  │  Red Team  │     │ │
│  │  │ Detection  │  │ Enforcement│  │   Testing  │     │ │
│  │  └────────────┘  └────────────┘  └────────────┘     │ │
│  │                                                        │ │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐     │ │
│  │  │   Audit    │  │    KPI     │  │   HITL     │     │ │
│  │  │    Logs    │  │  Tracking  │  │   Queue    │     │ │
│  │  └────────────┘  └────────────┘  └────────────┘     │ │
│  └───────────────────────────────────────────────────────┘ │
│                            │                                │
│  ┌───────────────────────────────────────────────────────┐ │
│  │               Data Store (In-Memory)                  │ │
│  │  documents | runs | policies | audit_logs | hitl_queue│ │
│  └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Component Architecture

### 1. Frontend Layer

**Technology**: Next.js 14, React 18, TypeScript, Tailwind CSS

**Pages**:
- `/` - Home/Dashboard
- `/documents` - Document upload and management
- `/review` - Document review workflow
- `/hitl` - Human-in-the-Loop approval queue
- `/redteam` - Security testing interface
- `/audit` - Audit log viewer
- `/reports` - KPI dashboard

**Key Components**:
- `Navigation.tsx` - Global navigation
- `api.ts` - API client library

**State Management**: React hooks (useState, useEffect)

### 2. Backend Layer

**Technology**: FastAPI (Python 3.11+), Pydantic, Uvicorn

**Main Modules**:

#### A. API Layer (`app/main.py`)
- REST endpoints for all operations
- Request/response validation
- CORS middleware
- In-memory data storage

#### B. Multi-Agent Pipeline (`app/agents/pipeline.py`)
- Orchestrates agent execution
- Handles data flow between agents
- Manages HITL interruption points
- Error handling and recovery

#### C. Agent Modules

**Classifier Agent** (`app/agents/classifier.py`)
- **Purpose**: Determine document type and sensitivity
- **Input**: Raw document content
- **Output**: Classification result with metadata
- **Methods**:
  - `_detect_document_type()` - Pattern matching for doc types
  - `_detect_sensitivity()` - High/medium/low classification
  - `_detect_financial_terms()` - Financial content detection
  - `_detect_health_data()` - HIPAA-relevant content

**Extractor Agent** (`app/agents/extractor.py`)
- **Purpose**: Extract clauses and PII entities
- **Input**: Document + classification
- **Output**: Structured clauses and PII list
- **Methods**:
  - `_extract_clauses()` - Document segmentation
  - `_extract_pii()` - Regex-based PII detection
  - `_extract_key_terms()` - Legal term identification
  - `_redact_value()` - PII redaction logic

**Reviewer Agent** (`app/agents/reviewer.py`)
- **Purpose**: Assess risks and policy compliance
- **Input**: Document + classification + extraction
- **Output**: Risk assessment and recommendations
- **Methods**:
  - `_assess_clauses()` - Per-clause risk analysis
  - `_check_policy_violations()` - Policy compliance check
  - `_assess_overall_risk()` - Aggregate risk calculation
  - `_generate_recommendations()` - Action items

**Drafter Agent** (`app/agents/drafter.py`)
- **Purpose**: Create redacted/edited versions
- **Input**: All previous agent outputs
- **Output**: Final document with redactions
- **Methods**:
  - `_apply_pii_redactions()` - Apply PII masking
  - `_apply_recommended_edits()` - Policy-driven edits
  - `_add_disclaimers()` - Required legal text
  - `_create_redline()` - Track changes document

#### D. Supporting Modules

**Red Team Testing** (`app/agents/redteam.py`)
- Security vulnerability testing
- Attack simulation (reconstruction, bypass, persona, extraction)
- Pass/fail determination
- Recommendation generation

**Audit System** (built into `main.py`)
- Logs all system actions
- Timestamps and user attribution
- Searchable and filterable
- Compliance-ready format

**HITL Queue** (built into `main.py`)
- Stores items requiring human approval
- Status tracking (pending/approved/rejected)
- Decision capture with rationale
- Resume workflow after approval

## Data Flow

### Document Review Flow

```
1. User uploads document
   └→ POST /api/documents/upload
      └→ Store in documents{}
         └→ Generate doc_id

2. User starts review
   └→ POST /api/run (doc_id, policy_ids)
      └→ Create run_id
         └→ Execute pipeline

3. Pipeline execution
   ├─→ Classifier
   │   ├─→ Analyze content
   │   └─→ Return {doc_type, sensitivity, risk_factors}
   │
   ├─→ Extractor
   │   ├─→ Parse clauses
   │   ├─→ Detect PII
   │   └─→ Return {clauses[], pii_entities[], key_terms[]}
   │   └─→ HITL Check → If high-risk PII → Create HITL item
   │
   ├─→ Reviewer
   │   ├─→ Assess each clause
   │   ├─→ Check policies
   │   └─→ Return {overall_risk, violations[], recommendations[]}
   │   └─→ HITL Check → If high risk → Create HITL item
   │
   └─→ Drafter
       ├─→ Apply PII redactions
       ├─→ Apply edits
       ├─→ Add disclaimers
       └─→ Return {final_document, redline_document}
       └─→ HITL Check → If external sharing → Create HITL item

4. HITL Approval (if needed)
   ├─→ User reviews items in queue
   ├─→ Approve/reject/modify each item
   ├─→ POST /api/hitl/{hitl_id}/respond
   └─→ Pipeline resumes from interruption point

5. Final output
   └─→ GET /api/run/{run_id}
       └─→ Return complete results with audit trail
```

### PII Detection Flow

```
Document Text
   │
   ├─→ For each PII pattern:
   │   ├─→ Regex search
   │   ├─→ Extract matches
   │   ├─→ Get surrounding context
   │   ├─→ Assess risk level
   │   └─→ Determine redaction mode
   │
   └─→ Create PII entity:
       {
         id, type, text, context,
         risk_level, redaction_mode,
         redacted_value
       }
```

### HITL Decision Flow

```
Agent detects high-risk item
   │
   ├─→ Create HITL item
   │   ├─→ Generate hitl_id
   │   ├─→ Store in hitl_queue{}
   │   ├─→ Set run status = "awaiting_hitl"
   │   └─→ Log to audit trail
   │
   ├─→ User views HITL queue
   │   └─→ GET /api/hitl/queue
   │
   ├─→ User reviews details
   │   └─→ GET /api/hitl/{hitl_id}
   │
   ├─→ User makes decisions
   │   ├─→ For each item: approve/reject/modify
   │   └─→ POST /api/hitl/{hitl_id}/respond
   │
   └─→ Pipeline resumes
       ├─→ Apply HITL decisions
       └─→ Continue from next agent
```

## Design Patterns

### 1. Pipeline Pattern
Sequential processing with data transformation at each stage.

```python
def execute_pipeline(run_id, document, policies, store):
    # Stage 1
    result1 = classifier.classify(document)
    
    # Stage 2 (uses Stage 1 output)
    result2 = extractor.extract(document, result1)
    
    # Stage 3 (uses Stage 1 & 2)
    result3 = reviewer.review(document, result1, result2)
    
    # Stage 4 (uses all previous)
    result4 = drafter.draft(document, result1, result2, result3)
```

### 2. Strategy Pattern
Multiple redaction strategies (mask/generalize/refuse).

```python
def _redact_value(value, pii_type, mode):
    if mode == "mask":
        return mask_value(value)
    elif mode == "generalize":
        return generalize_value(value)
    else:  # refuse
        return "[REDACTED]"
```

### 3. Chain of Responsibility
Agents process in sequence, each adding to the result.

### 4. Observer Pattern
Audit logging observes all system actions.

```python
STORE["audit_logs"].append({
    "timestamp": datetime.utcnow().isoformat(),
    "action": "document_uploaded",
    "details": {...}
})
```

## Security Architecture

### Defense in Depth

**Layer 1: Input Validation**
- File type checking
- Size limits
- Content validation

**Layer 2: PII Detection**
- Multiple pattern types
- Context analysis
- Risk classification

**Layer 3: Policy Enforcement**
- Rule-based checks
- Threshold validation
- Required elements

**Layer 4: HITL Gates**
- Human approval for high-risk
- Decision tracking
- Audit trail

**Layer 5: Red Team Testing**
- Continuous security testing
- Vulnerability detection
- Regression prevention

## Scalability Considerations

### Current Design (Classroom)
- In-memory storage
- Single-process execution
- Synchronous pipeline

### Production Recommendations

**1. Database Layer**
```
Replace in-memory STORE with:
- PostgreSQL for structured data
- MongoDB for documents
- Redis for caching
```

**2. Async Processing**
```
- Use Celery or RQ for background jobs
- Async/await for I/O operations
- WebSockets for real-time updates
```

**3. Horizontal Scaling**
```
- Load balancer (Nginx)
- Multiple backend instances
- Distributed task queue
- Shared database/cache
```

**4. Agent Parallelization**
```
- Run independent agents in parallel
- Use message queue (RabbitMQ/Kafka)
- Distributed tracing (OpenTelemetry)
```

## Performance Characteristics

### Typical Processing Times

| Operation | Time | Notes |
|-----------|------|-------|
| Document upload | 100-500ms | Depends on size |
| Classifier | 50-200ms | Regex-based, fast |
| Extractor | 200-500ms | PII scanning intensive |
| Reviewer | 100-300ms | Policy checks |
| Drafter | 150-400ms | Text transformation |
| **Total pipeline** | **500-1400ms** | Sequential execution |

### Optimization Opportunities

1. **Caching**: Cache policy rules, regex patterns
2. **Parallel PII Detection**: Process chunks in parallel
3. **Compiled Regex**: Pre-compile all patterns
4. **Batch Processing**: Process multiple documents together
5. **Incremental Updates**: Only reprocess changed sections

## Error Handling

### Strategy
```python
try:
    # Execute agent
    result = agent.process(input)
except Exception as e:
    # Log error
    log_error(agent_name, e)
    # Mark run as failed
    run["status"] = "failed"
    run["error"] = str(e)
    # Store partial results
    run["partial_results"] = {...}
```

### Recovery
- Partial results preserved
- Resume from last successful agent
- Manual intervention via HITL

## Testing Strategy

### Unit Tests
- Individual agent methods
- PII pattern matching
- Policy violation detection
- Redaction logic

### Integration Tests
- Full pipeline execution
- HITL workflow
- API endpoints
- Error scenarios

### Red Team Tests
- Security vulnerabilities
- Bypass attempts
- Edge cases
- Regression suite

## Monitoring & Observability

### Metrics to Track
- Pipeline execution time per stage
- PII detection rate (true/false positives)
- Policy violation frequency
- HITL approval time
- Red team test results
- API response times
- Error rates

### Logging
- Structured JSON logs
- Request/response logging
- Agent decision logs
- Error stack traces
- Audit trail

### Alerting
- High error rate
- Long HITL queue
- Red team test failures
- Unauthorized disclosure attempts
- Performance degradation

## Future Architecture Enhancements

1. **LLM Integration**
   - GPT-4/Claude for advanced analysis
   - Embeddings for semantic search
   - Context-aware PII detection

2. **Microservices**
   - Separate service per agent
   - API gateway
   - Service mesh (Istio)

3. **Event-Driven**
   - Event sourcing
   - CQRS pattern
   - Event bus (Kafka)

4. **ML Pipeline**
   - Training pipeline for custom NER
   - Model versioning
   - A/B testing
   - Continuous learning

5. **GraphQL API**
   - More flexible queries
   - Real-time subscriptions
   - Better frontend integration

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [Multi-Agent Systems](https://en.wikipedia.org/wiki/Multi-agent_system)
- [OWASP Security Patterns](https://owasp.org/)
- [Microservices Patterns](https://microservices.io/patterns/)

