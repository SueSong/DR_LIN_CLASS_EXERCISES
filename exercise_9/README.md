# Exercise 9: Legal Document Review Multi-Agent System

## Overview

A comprehensive legal document review system featuring a **multi-agent architecture** with PII protection, policy enforcement, HITL (Human-in-the-Loop) workflows, and red team security testing.

### Multi-Agent Architecture

The system uses four specialized AI agents working in sequence:

1. **Classifier Agent**: Determines document type (NDA, contract, etc.) and sensitivity level
2. **Extractor Agent**: Identifies clauses, PII entities, and key legal terms
3. **Reviewer Agent**: Assesses risks and checks policy compliance
4. **Drafter Agent**: Creates redacted/edited versions with tracked changes

## Key Features

### 🛡️ PII Protection
- **Automatic Detection**: Detects SSN, tax IDs, credit cards, bank accounts, emails, phones, addresses, names
- **Multiple Redaction Modes**:
  - **Mask**: `123-45-6789` → `***-**-6789`
  - **Generalize**: `john@email.com` → `[EMAIL]`
  - **Refuse**: Complete removal `[REDACTED]`
- **Risk-Based Classification**: High/Medium/Low risk levels for each PII type
- **Context-Aware**: Maintains context for better detection accuracy

### ✅ Policy Enforcement
- **Forbidden Advice Detection**: Identifies unauthorized legal/tax/medical advice
- **Required Disclaimers**: Ensures legal disclaimer and confidentiality notices
- **Third-Party Sharing Controls**: Blocks unauthorized data sharing
- **Financial Thresholds**: Flags amounts exceeding policy limits
- **Health Data Protection**: HIPAA-compliant handling

### 👥 Human-in-the-Loop (HITL)
- **Smart Triggers**: Automatically requires human approval for:
  - High-risk PII detection
  - High-risk clauses
  - Policy violations
  - External document sharing
- **Approval Workflows**: Review, approve, reject, or modify proposed actions
- **Complete Audit Trail**: Every decision is logged with timestamp and rationale

### 🔴 Red Team Testing
Comprehensive security testing suite to prevent data leaks:

- **Reconstruction Attacks**: Attempts to reconstruct redacted PII
- **Encoding Bypass**: Base64, ROT13, Unicode homoglyph attacks
- **Persona Attacks**: Impersonation of authority figures (counsel, executives)
- **Bulk Extraction**: Mass data extraction attempts
- **Regression Tests**: Every found leak becomes a permanent test

## Architecture

```
Frontend (Next.js/React)
    ↓
Backend (FastAPI)
    ↓
Multi-Agent Pipeline:
    Classifier → Extractor → Reviewer → Drafter
    ↓
HITL Queue (when needed)
    ↓
Final Output (redacted document)
```

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Or: Python 3.11+ and Node.js 18+

### Using Docker (Recommended)

```bash
# Start all services
docker-compose up --build

# Backend: http://localhost:8000
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/docs
```

### Manual Setup

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Usage Guide

### 1. Upload Documents
- Navigate to **Documents** page
- Upload legal documents (.txt, .md, .doc, .docx)
- Sample documents provided in `data/sample_documents/`

### 2. Start Review
- Go to **Review** page
- Select document and applicable policies
- Click "Start Multi-Agent Review"
- View results from each agent

### 3. HITL Approval
- If high-risk items detected, review appears in **HITL Queue**
- Review each flagged item
- Approve, reject, or modify proposed actions
- Add comments for audit trail

### 4. Red Team Testing
- Visit **Red Team** page
- Run predefined security tests
- View attack detection results
- Verify system blocks bypass attempts

### 5. Monitor KPIs
- Check **Reports** page for:
  - Clause extraction accuracy
  - PII F1 score
  - Unauthorized disclosure count (target: ZERO)
  - Review SLA hit rate
  - Red team test pass rate

### 6. Audit Trail
- **Audit** page shows complete activity log
- Filter by action type
- Search across all fields
- Export for compliance

## API Endpoints

### Documents
- `POST /api/documents/upload` - Upload document
- `GET /api/documents` - List documents
- `GET /api/documents/{doc_id}` - Get document

### Review
- `POST /api/run` - Start review run
- `GET /api/run/{run_id}` - Get run results

### HITL
- `GET /api/hitl/queue` - Get pending approvals
- `GET /api/hitl/{hitl_id}` - Get HITL details
- `POST /api/hitl/{hitl_id}/respond` - Submit decisions

### Red Team
- `POST /api/redteam/test` - Run security test
- `GET /api/redteam/tests` - List test results

### Policies
- `GET /api/policies` - List policies
- `GET /api/policies/{policy_id}` - Get policy details

### Reports
- `GET /api/reports/kpis` - Get KPI metrics
- `GET /api/audit/logs` - Get audit logs

### Export
- `GET /api/export/run/{run_id}/redline` - Export redline document
- `GET /api/export/run/{run_id}/final` - Export final document

## Key Performance Indicators (KPIs)

| KPI | Target | Description |
|-----|--------|-------------|
| **Clause Extraction Accuracy** | ≥90% | Accuracy of clause identification |
| **PII F1 Score** | ≥85% | Balance of PII precision & recall |
| **Unauthorized Disclosures** | 0 | Number of data leaks |
| **Review SLA Hit Rate** | ≥95% | Reviews completed within SLA |
| **Red Team Pass Rate** | ≥90% | Security tests blocked by system |

## Sample Documents

Located in `data/sample_documents/`:

1. **nda_with_pii.md** - NDA with multiple PII types (high-risk test case)
2. **service_agreement.md** - Standard MSA with financial terms

## Red Team Test Scenarios

Located in `data/test_cases/redteam_scenarios.json`:

- **RT001**: SSN Reconstruction Attack
- **RT002**: Base64 Encoding Bypass
- **RT003**: Character Substitution Bypass
- **RT004**: Outside Counsel Persona Attack
- **RT005**: Executive Authority Bypass
- **RT006**: Bulk SSN Extraction
- **RT007**: Credit Card Mining
- **RT008**: ROT13 Encoding Bypass
- **RT009**: Unicode Homoglyph Attack
- **RT010**: Timing Attack
- **RT011**: Compliance Officer Impersonation
- **RT012**: Policy Confusion Attack

## Development

### Project Structure
```
exercise_9/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   └── agents/
│   │       ├── classifier.py     # Document classification
│   │       ├── extractor.py      # PII & clause extraction
│   │       ├── reviewer.py       # Risk assessment
│   │       ├── drafter.py        # Redaction & editing
│   │       ├── pipeline.py       # Agent orchestration
│   │       └── redteam.py        # Security testing
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx          # Home page
│   │   │   ├── documents/        # Document management
│   │   │   ├── review/           # Review workflow
│   │   │   ├── hitl/             # HITL queue
│   │   │   ├── redteam/          # Red team testing
│   │   │   ├── audit/            # Audit logs
│   │   │   └── reports/          # KPI dashboard
│   │   ├── components/
│   │   └── lib/
│   │       └── api.ts            # API client
│   ├── package.json
│   └── Dockerfile
├── data/
│   ├── sample_documents/
│   └── test_cases/
├── docker-compose.yml
└── README.md
```

### Adding Custom Policies

Edit `backend/app/main.py` and add to `DEFAULT_POLICIES`:

```python
"custom_policy": {
    "name": "Custom Policy Name",
    "rules": {
        "custom_rule": "value",
        "threshold": 100
    }
}
```

### Extending PII Detection

Add patterns to `backend/app/agents/extractor.py`:

```python
PII_PATTERNS = {
    "custom_pii": r"your_regex_pattern",
    # ...
}
```

## Security Considerations

- **Never deploy with in-memory storage in production** - Use a proper database
- **Implement authentication/authorization** - Current version has no auth
- **Enable HTTPS** - Use TLS/SSL in production
- **Rate limiting** - Prevent abuse and DDoS
- **Audit log retention** - Comply with regulatory requirements
- **Encryption at rest** - Encrypt stored documents and PII

## Compliance Features

- ✅ Complete audit trail of all actions
- ✅ HITL approval for high-risk operations
- ✅ PII redaction with multiple modes
- ✅ Policy enforcement engine
- ✅ Red team testing suite
- ✅ Zero unauthorized disclosure target
- ✅ Tracked changes (redline documents)
- ✅ KPI monitoring dashboard

## Learning Objectives

Students will learn:

1. **Multi-Agent System Design**: Coordinating specialized agents
2. **PII Detection & Redaction**: Regex-based pattern matching
3. **Policy Enforcement**: Rule-based compliance checking
4. **HITL Workflows**: When and how to involve humans
5. **Red Team Testing**: Adversarial security testing
6. **Audit Trails**: Compliance logging
7. **KPI Monitoring**: Measuring system performance
8. **Full-Stack Development**: FastAPI + React/Next.js

## Troubleshooting

### Backend won't start
```bash
# Check Python version
python --version  # Should be 3.11+

# Reinstall dependencies
pip install -r backend/requirements.txt
```

### Frontend won't start
```bash
# Check Node version
node --version  # Should be 18+

# Clear and reinstall
rm -rf frontend/node_modules
cd frontend && npm install
```

### CORS errors
- Ensure backend is running on port 8000
- Check `NEXT_PUBLIC_API_URL` in frontend environment

### No documents in list
- Upload a document via the Documents page
- Or use sample documents from `data/sample_documents/`

## Future Enhancements

- [ ] LLM integration for advanced clause analysis
- [ ] Multi-language support
- [ ] PDF document processing
- [ ] Collaborative review workflows
- [ ] Integration with document management systems
- [ ] Machine learning for PII detection
- [ ] Real-time collaboration
- [ ] Advanced visualization of risk metrics

## 🎓 For Instructors & Students

This exercise is designed for **Class 6** of the AI training curriculum. Complete teaching materials are included:

### For Students
- **[CLASS_6_STUDENT_TASKS.md](CLASS_6_STUDENT_TASKS.md)** - 10 progressive tasks (18-23 hours)
  - Tasks 1-3: Basic (Setup, Pipeline, PII Testing)
  - Tasks 4-5: Intermediate (New PII Pattern, Custom Policy)
  - Tasks 6-7: Advanced (Chat Security, Red Team Suite)
  - Tasks 8-9: Expert (HITL Workflow, Advanced PII)
  - Task 10: Capstone (Custom Feature)
  
- **[STUDENT_QUICK_REFERENCE.md](STUDENT_QUICK_REFERENCE.md)** - Printable cheat sheet
  - Quick start commands
  - Important file locations
  - Code snippets
  - Troubleshooting guide

### For Instructors
- **[CLASS_6_INSTRUCTOR_GUIDE.md](CLASS_6_INSTRUCTOR_GUIDE.md)** - Complete teaching guide
  - 5-week lecture plans
  - Lab session activities
  - Answer keys for all tasks
  - Grading rubrics
  - Common mistakes & teaching tips
  - Office hours FAQ

- **[CLASS_6_MATERIALS_SUMMARY.md](CLASS_6_MATERIALS_SUMMARY.md)** - Materials overview
  - Learning objectives
  - Assessment strategy
  - Expected outcomes
  - Quick start guide for instructors

### Additional Guides
- **[CHATBOT_GUIDE.md](CHATBOT_GUIDE.md)** - Complete guide to the chat assistant feature
- **[REDTEAM_TESTING_GUIDE.md](REDTEAM_TESTING_GUIDE.md)** - Red team testing methodology

### Quick Start for Class
1. Students: Read `CLASS_6_STUDENT_TASKS.md` and `STUDENT_QUICK_REFERENCE.md`
2. Instructors: Read `CLASS_6_INSTRUCTOR_GUIDE.md` for answers and teaching plan
3. Everyone: Follow `QUICKSTART.md` for system setup

---

## License

Educational use only - Part of AI Training Class 1

## Support

For questions or issues, please refer to the course materials or instructor.

