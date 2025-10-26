# Class 6 - Student Tasks for Exercise 9
## Legal Document Review Multi-Agent System with Security Testing

### 📚 Course Context
**Class 6 Focus:** Multi-Agent Systems, AI Security, PII Protection, Red Team Testing

**Learning Objectives:**
- Understand multi-agent architectures
- Implement PII detection and redaction
- Learn prompt injection and security vulnerabilities
- Practice red team testing methodologies
- Build Human-in-the-Loop (HITL) workflows
- Master audit trail and compliance logging

---

## 🎯 Task Overview

Students will complete **10 tasks** of varying difficulty:
- **Tasks 1-3:** Basic (Understanding & Setup)
- **Tasks 4-6:** Intermediate (Implementation)
- **Tasks 7-8:** Advanced (Security)
- **Tasks 9-10:** Expert (Custom Features)

**Estimated Time:** 8-12 hours total

---

## Task 1: Setup & System Exploration (30 minutes)
**Difficulty:** ⭐ Basic

### Objectives
- Set up the exercise environment
- Understand the system architecture
- Test all major features

### Steps
1. **Start the system**
   ```bash
   cd exercise_9/backend
   uvicorn app.main:app --reload --port 8000
   
   # In another terminal
   cd exercise_9/frontend
   npm install
   npm run dev
   ```

2. **Verify all pages work:**
   - [ ] Home page (/)
   - [ ] Documents (/documents)
   - [ ] Review (/review)
   - [ ] Chat (/chat)
   - [ ] HITL Queue (/hitl)
   - [ ] Red Team (/redteam)
   - [ ] Audit (/audit)
   - [ ] Reports (/reports)

3. **Upload sample documents**
   - Upload `data/sample_documents/nda_with_pii.md`
   - Upload `data/sample_documents/service_agreement.md`

### Deliverables
- [ ] Screenshot of all 8 pages working
- [ ] List of 5 observations about the system
- [ ] Document the multi-agent pipeline flow

---

## Task 2: Multi-Agent Pipeline Analysis (45 minutes)
**Difficulty:** ⭐ Basic

### Objectives
- Understand how agents work together
- Trace data flow through the pipeline
- Identify agent responsibilities

### Steps
1. **Read the code:**
   - `backend/app/agents/pipeline.py`
   - `backend/app/agents/classifier.py`
   - `backend/app/agents/extractor.py`
   - `backend/app/agents/reviewer.py`
   - `backend/app/agents/drafter.py`

2. **Run a document review:**
   - Upload NDA with PII
   - Start review with all policies
   - Observe each agent's output

3. **Document the pipeline:**
   - Create a flowchart showing:
     - Agent execution order
     - Data passed between agents
     - HITL interruption points
     - Final output generation

### Deliverables
- [ ] Pipeline flowchart (diagram or markdown)
- [ ] Table showing what each agent does
- [ ] Explanation of when HITL is triggered
- [ ] Screenshot of a complete review run

**Example Table Format:**
```
| Agent      | Input             | Processing           | Output              |
|------------|-------------------|----------------------|---------------------|
| Classifier | Raw document      | Type detection       | doc_type, sensitivity |
| Extractor  | Document + class  | PII extraction       | clauses[], pii[]     |
| ...        | ...               | ...                  | ...                 |
```

---

## Task 3: PII Detection Testing (1 hour)
**Difficulty:** ⭐⭐ Basic-Intermediate

### Objectives
- Test PII detection capabilities
- Understand different PII types
- Evaluate detection accuracy

### Steps
1. **Create test document** with various PII types:
   - SSN: 123-45-6789
   - Email: john.doe@company.com
   - Phone: (555) 123-4567
   - Credit Card: 4532-1234-5678-9012
   - Address: 123 Main Street, City, State
   - Bank Account: 1234567890

2. **Test each redaction mode:**
   - Mask mode
   - Generalize mode
   - Refuse mode

3. **Document results:**
   - Which PII types were detected?
   - Which were missed?
   - Are the redactions appropriate?

### Deliverables
- [ ] Test document (markdown file)
- [ ] Test results table showing:
  - PII type
  - Detection success (Yes/No)
  - Redacted output
  - Risk level assigned
- [ ] Analysis: Strengths and weaknesses of current detection

---

## Task 4: Add New PII Pattern (1.5 hours)
**Difficulty:** ⭐⭐ Intermediate

### Objectives
- Extend PII detection capabilities
- Understand regex patterns
- Test custom detection

### Assignment
Add detection for **Passport Numbers** (format: AB1234567)

### Steps
1. **Add pattern** to `backend/app/agents/extractor.py`:
   ```python
   "passport": r"\b[A-Z]{2}\d{7}\b"
   ```

2. **Add redaction logic** in `_redact_value()`:
   ```python
   elif pii_type == "passport":
       return "***" + value[-4:]  # Keep last 4
   ```

3. **Test your implementation:**
   - Create document with passport numbers
   - Run review
   - Verify detection and redaction

### Deliverables
- [ ] Modified `extractor.py` with new pattern
- [ ] Test document with passport numbers
- [ ] Screenshot showing successful detection
- [ ] Write explanation: Why this pattern works

**Bonus:** Add detection for:
- Driver's License
- IP Addresses
- Crypto wallet addresses

---

## Task 5: Create Custom Policy (2 hours)
**Difficulty:** ⭐⭐ Intermediate

### Objectives
- Understand policy enforcement
- Create custom business rules
- Integrate with reviewer agent

### Assignment
Create a **"Payment Terms Policy"** that:
- Flags payment amounts > $50,000
- Requires specific payment terms (NET 30, NET 60)
- Checks for payment protection clauses

### Steps
1. **Add policy** to `backend/app/main.py`:
   ```python
   "payment_policy": {
       "name": "Payment Terms Policy",
       "rules": {
           "max_amount": 50000,
           "required_terms": ["NET 30", "NET 60"],
           "require_protection": True
       }
   }
   ```

2. **Add policy checks** in `backend/app/agents/reviewer.py`:
   - Detect payment amounts in clauses
   - Check for payment terms
   - Flag violations

3. **Test the policy:**
   - Create document with payment terms
   - Run review
   - Verify policy violations are detected

### Deliverables
- [ ] Policy definition in `main.py`
- [ ] Policy checking code in `reviewer.py`
- [ ] Test document with violations
- [ ] Screenshot showing policy violation detection
- [ ] Documentation: How the policy works

---

## Task 6: Chat Security Testing (2 hours)
**Difficulty:** ⭐⭐⭐ Intermediate-Advanced

### Objectives
- Understand prompt injection attacks
- Test chatbot security defenses
- Find vulnerabilities

### Steps
1. **Test all example prompts:**
   - Normal questions (4 examples)
   - Prompt injections (6 examples)
   - Jailbreak attempts (4 examples)

2. **Create 5 NEW attack scenarios:**
   - Try to extract PII
   - Attempt role manipulation
   - Test encoding bypasses
   - Try delimiter injection
   - Attempt system prompt extraction

3. **Document results:**
   - Which attacks were blocked?
   - Which attacks succeeded?
   - What patterns were detected?
   - What risk scores were assigned?

### Deliverables
- [ ] Test results spreadsheet:
  ```
  | Attack | Blocked? | Pattern Detected | Risk Score | Notes |
  |--------|----------|------------------|------------|-------|
  | ...    | ...      | ...              | ...        | ...   |
  ```
- [ ] 5 new attack prompts (with results)
- [ ] Analysis: Security strengths and weaknesses
- [ ] Recommendations for improvement

**Challenge:** Find at least ONE successful bypass!

---

## Task 7: Red Team Test Suite (2.5 hours)
**Difficulty:** ⭐⭐⭐ Advanced

### Objectives
- Create comprehensive security tests
- Test all attack vectors
- Build regression test suite

### Assignment
Create **5 new red team tests** covering:
1. PII reconstruction
2. Encoding bypass
3. Persona attack
4. Data extraction
5. Custom vulnerability

### Steps
1. **Study existing tests** in `backend/app/agents/redteam.py`

2. **Implement new tests:**
   ```python
   def test_your_attack(payload, store):
       # Your test logic
       if vulnerability_found:
           return {
               "passed": False,
               "vulnerability": "...",
               "severity": "high",
               "recommendation": "..."
           }
       return {"passed": True, "details": "..."}
   ```

3. **Add to `execute_redteam_test()`:**
   ```python
   elif attack_type == "your_attack":
       return test_your_attack(payload, store)
   ```

4. **Run all tests via UI or API**

### Deliverables
- [ ] Modified `redteam.py` with 5 new tests
- [ ] Test scenarios JSON file
- [ ] Test execution results (all tests)
- [ ] Report: Vulnerabilities found
- [ ] Recommendations: How to fix each issue

**Grading Criteria:**
- Tests actually work (40%)
- Tests find real issues (30%)
- Code quality (15%)
- Documentation (15%)

---

## Task 8: HITL Workflow Implementation (2 hours)
**Difficulty:** ⭐⭐⭐ Advanced

### Objectives
- Understand human-in-the-loop workflows
- Implement approval mechanisms
- Create audit trails

### Assignment
Add a **new HITL trigger** for high-value contracts

### Requirements
- Trigger HITL if financial amount > $100,000
- Show amount and terms for approval
- Log all approval decisions
- Continue pipeline after approval

### Steps
1. **Add detection** in `reviewer.py`:
   ```python
   def _check_high_value(self, clauses):
       # Extract financial amounts
       # Check if > threshold
       # Create HITL items
   ```

2. **Create HITL request** in `pipeline.py`

3. **Test the workflow:**
   - Create document with $150,000 amount
   - Run review
   - Verify HITL queue has item
   - Approve via UI
   - Verify pipeline continues

### Deliverables
- [ ] Modified code (reviewer.py, pipeline.py)
- [ ] Test document with high-value terms
- [ ] Screenshot of HITL queue
- [ ] Screenshot of approval process
- [ ] Audit log showing approval
- [ ] Documentation: How the workflow works

---

## Task 9: Advanced PII Detection with Context (3 hours)
**Difficulty:** ⭐⭐⭐⭐ Expert

### Objectives
- Implement context-aware detection
- Reduce false positives
- Use advanced pattern matching

### Assignment
Improve PII detection to be **context-aware**

### Requirements
1. **Name Detection:**
   - Distinguish between person names and company names
   - Don't flag "Terms" or "Party A" as names
   - Use title context (Mr., Dr., CEO)

2. **Email Detection:**
   - Distinguish between email in signatures vs body
   - Different risk levels for different contexts

3. **Number Detection:**
   - Detect account numbers only in financial context
   - Don't flag arbitrary numbers

### Implementation Ideas
```python
def _extract_pii_with_context(self, content):
    # Split into sections
    # Analyze context around matches
    # Adjust risk based on context
    # Return enhanced PII entities
```

### Deliverables
- [ ] Enhanced `extractor.py` with context awareness
- [ ] Test documents showing:
  - False positive reduction
  - Maintained true positive rate
- [ ] Comparison table: Before vs After
- [ ] Algorithm explanation document
- [ ] Unit tests for edge cases

**Bonus:** Add machine learning-based NER using spaCy

---

## Task 10: Custom Feature - Your Choice (3-4 hours)
**Difficulty:** ⭐⭐⭐⭐ Expert

### Objectives
- Apply all learned concepts
- Build a complete feature
- Demonstrate mastery

### Assignment
Choose ONE feature to implement:

#### Option A: Document Comparison
- Upload 2 versions of same contract
- Highlight differences
- Assess risk of changes
- Generate change summary

#### Option B: Smart Clause Extraction
- Use ML/NER to extract clauses
- Classify clause types (liability, term, payment, etc.)
- Create clause library
- Suggest standard clauses

#### Option C: Automated Negotiation Suggestions
- Analyze risky clauses
- Suggest alternative language
- Provide negotiation talking points
- Generate redline with improvements

#### Option D: Multi-language Support
- Add translation capability
- PII detection in other languages
- Multi-language chat
- Language-specific policies

#### Option E: Your Own Idea
- Propose a custom feature
- Get instructor approval
- Implement it

### Deliverables
- [ ] Feature design document
- [ ] Implementation (backend + frontend)
- [ ] Tests demonstrating functionality
- [ ] User documentation
- [ ] Video demo (3-5 minutes)
- [ ] Code review-ready pull request

---

## 📊 Grading Rubric

### Task Completion (50%)
- All required steps completed
- Deliverables submitted
- Code works as specified

### Code Quality (20%)
- Clean, readable code
- Proper comments
- Follows existing patterns
- Error handling

### Documentation (15%)
- Clear explanations
- Good formatting
- Screenshots included
- Complete analysis

### Security Awareness (10%)
- Identifies vulnerabilities
- Proposes fixes
- Considers edge cases

### Innovation (5%)
- Creative solutions
- Bonus features
- Unique insights

---

## 🎓 Learning Outcomes

By completing these tasks, students will:

✅ **Understand Multi-Agent Systems**
- Agent coordination
- Data flow between agents
- Error handling and recovery

✅ **Master PII Detection**
- Pattern matching with regex
- Context-aware detection
- Risk classification
- Redaction strategies

✅ **Learn Security Testing**
- Prompt injection attacks
- Jailbreak techniques
- Red team methodologies
- Vulnerability assessment

✅ **Implement HITL Workflows**
- Human approval gates
- Decision tracking
- Audit trails
- Compliance logging

✅ **Build Production Systems**
- API design
- Frontend development
- Testing strategies
- Documentation

---

## 📝 Submission Guidelines

### For Each Task

1. **Code Changes**
   - Create a branch: `student-name/task-X`
   - Commit frequently with clear messages
   - Push to repository

2. **Documentation**
   - Create `TASK_X_REPORT.md`
   - Include all required deliverables
   - Add screenshots/diagrams
   - Explain your approach

3. **Testing**
   - Provide test cases
   - Show test results
   - Document any issues found

### Final Submission

- [ ] All task branches pushed
- [ ] All report files submitted
- [ ] Video demo (optional but recommended)
- [ ] Self-assessment document

---

## 🆘 Getting Help

### Resources
- **Documentation:** All markdown files in exercise_9/
- **Code Examples:** Existing agents in `backend/app/agents/`
- **API Docs:** http://localhost:8000/docs

### Office Hours
- Ask questions about tasks
- Get code review feedback
- Discuss design decisions

### Collaboration Policy
- You may discuss approaches
- You may NOT share code directly
- You MUST write your own implementation
- Cite any external resources used

---

## 🏆 Extra Credit Opportunities

### Extra Credit 1: Performance Optimization
- Profile the system
- Identify bottlenecks
- Implement optimizations
- Measure improvements

**Worth:** +5%

### Extra Credit 2: Real LLM Integration
- Integrate GPT-4 or Claude API
- Replace simulated responses
- Add streaming responses
- Handle rate limits

**Worth:** +10%

### Extra Credit 3: Deployment Package
- Create Docker Compose setup
- Add environment configuration
- Write deployment guide
- Include monitoring

**Worth:** +5%

### Extra Credit 4: Security Research Paper
- Research LLM security
- Document attack vectors
- Propose defenses
- Write 5-page paper

**Worth:** +5%

---

## 📅 Suggested Timeline

| Week | Tasks | Time |
|------|-------|------|
| Week 1 | Tasks 1-3 | 2-3 hours |
| Week 2 | Tasks 4-5 | 3-4 hours |
| Week 3 | Tasks 6-7 | 4-5 hours |
| Week 4 | Tasks 8-9 | 5-6 hours |
| Week 5 | Task 10 + Polish | 4-5 hours |

**Total:** 18-23 hours over 5 weeks

---

## ✅ Task Checklist Template

Copy this for tracking:

```markdown
## My Progress

### Week 1
- [ ] Task 1: Setup & Exploration (✓ Completed / ⏳ In Progress / ⏸ Not Started)
- [ ] Task 2: Pipeline Analysis
- [ ] Task 3: PII Testing

### Week 2
- [ ] Task 4: New PII Pattern
- [ ] Task 5: Custom Policy

### Week 3
- [ ] Task 6: Chat Security
- [ ] Task 7: Red Team Suite

### Week 4
- [ ] Task 8: HITL Workflow
- [ ] Task 9: Advanced PII

### Week 5
- [ ] Task 10: Custom Feature
- [ ] Final Documentation
- [ ] Video Demo
```

---

## 🎯 Success Criteria

To pass this exercise, students must:
- ✅ Complete Tasks 1-8 (minimum)
- ✅ Submit all required deliverables
- ✅ Write working, tested code
- ✅ Demonstrate understanding in reports
- ✅ Present findings to class

**A Grade:** All 10 tasks + excellent quality
**B Grade:** Tasks 1-9 + good quality
**C Grade:** Tasks 1-8 + acceptable quality

---

## 🎊 Final Notes

This is a **comprehensive, real-world project** that teaches:
- Multi-agent AI systems
- Security in AI applications
- Production code practices
- Documentation skills

**Take your time, ask questions, and enjoy learning!** 🚀

Good luck! 💪

