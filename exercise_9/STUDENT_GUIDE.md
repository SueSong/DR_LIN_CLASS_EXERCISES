# Student Guide - Exercise 9: Legal Document Review

## Learning Objectives

By completing this exercise, you will learn:

1. **Multi-Agent System Architecture**
   - How to design and coordinate multiple specialized agents
   - Agent communication and data passing
   - Sequential pipeline execution
   - Error handling across agent boundaries

2. **PII Detection & Protection**
   - Regex-based pattern matching for sensitive data
   - Different redaction strategies (mask/generalize/refuse)
   - Risk classification of PII types
   - Context-aware detection techniques

3. **Policy Enforcement**
   - Rule-based compliance checking
   - Policy violation detection
   - Required disclaimer validation
   - Threshold-based decision making

4. **Human-in-the-Loop (HITL)**
   - When to require human approval
   - Designing approval workflows
   - Audit trail creation
   - Decision tracking and reasoning

5. **Red Team Testing**
   - Adversarial testing methodologies
   - Common attack vectors (reconstruction, bypass, persona, extraction)
   - Security vulnerability assessment
   - Regression test creation

6. **Full-Stack Development**
   - REST API design with FastAPI
   - React/Next.js frontend development
   - State management in React
   - API integration

## Exploration Activities

### Activity 1: Understand the Agent Pipeline (30 minutes)

**Goal**: Trace a document through the entire multi-agent pipeline

1. Read `backend/app/agents/pipeline.py` - the orchestrator
2. Identify how agents are called in sequence
3. Find where HITL checks occur
4. Trace data flow from document to final output

**Questions to Answer**:
- What happens if an agent fails?
- How does the Classifier's output influence the Extractor?
- When exactly is HITL triggered?
- What data is passed between agents?

### Activity 2: Explore PII Detection (45 minutes)

**Goal**: Understand how PII is detected and redacted

1. Read `backend/app/agents/extractor.py`
2. Study the `PII_PATTERNS` dictionary
3. Examine the `_redact_value()` method
4. Test different PII patterns

**Experiments**:
- Add a new PII type (e.g., passport number)
- Try different redaction modes
- Test edge cases (malformed SSN, international phone numbers)
- See how context is extracted

**Challenge**: Create a PII pattern for driver's license numbers

### Activity 3: Test Red Team Scenarios (45 minutes)

**Goal**: Understand security testing and attack vectors

1. Read `backend/app/agents/redteam.py`
2. Run each predefined red team test
3. Analyze why some pass and some fail
4. Study the attack detection logic

**Tasks**:
- Run all 5 predefined tests via UI
- Examine results for each attack type
- Identify what makes an attack successful vs blocked
- Propose a new attack vector

**Challenge**: Design a new red team test for a bypass technique not covered

### Activity 4: Implement Custom Policy (60 minutes)

**Goal**: Add a new policy rule to the system

**Scenario**: Add a policy that flags documents containing crypto wallet addresses

1. **Add Pattern Detection** (`extractor.py`):
```python
# Add to PII_PATTERNS
"crypto_wallet": r"\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b",  # Bitcoin address
```

2. **Add Policy Rule** (`main.py`):
```python
"crypto_policy": {
    "name": "Cryptocurrency Policy",
    "rules": {
        "detect_wallets": True,
        "require_hitl": True,
        "allowed_usage": "none"
    }
}
```

3. **Add Reviewer Check** (`reviewer.py`):
```python
# In _check_policy_violations()
if "crypto_wallet" in [p["type"] for p in pii_entities]:
    violations.append({
        "type": "cryptocurrency_detected",
        "severity": "high",
        "description": "Document contains cryptocurrency wallet address",
        "policy": "Cryptocurrency Policy"
    })
```

4. **Test**: Upload a document with a Bitcoin address and verify it's flagged

### Activity 5: Analyze KPI Calculations (30 minutes)

**Goal**: Understand how performance metrics are calculated

1. Read `backend/app/main.py` - the `/api/reports/kpis` endpoint
2. Identify how each KPI is computed
3. Find what data sources are used
4. Consider edge cases

**Questions**:
- How is PII F1 score calculated? (Currently simulated - what would real calculation need?)
- Why is "unauthorized disclosures" always zero? (Is this realistic?)
- What defines "completed within SLA"?
- How could you make KPIs more accurate?

**Challenge**: Implement real F1 score calculation for PII detection

### Activity 6: Improve HITL Workflow (60 minutes)

**Goal**: Enhance the human review process

**Current State**: HITL queue shows items, user approves/rejects

**Enhancement Ideas**:
1. Add priority levels (critical/high/medium/low)
2. Implement timeout warnings for pending approvals
3. Add bulk approval for low-risk items
4. Show statistical recommendations

**Implementation**:
- Choose one enhancement
- Modify backend logic
- Update frontend UI
- Test workflow

### Activity 7: Create Test Documents (45 minutes)

**Goal**: Build comprehensive test cases

Create 3 new test documents:

1. **High-Risk NDA**
   - Multiple PII types (SSN, credit card, bank account)
   - Financial terms exceeding threshold
   - Forbidden advice language
   - Missing required disclaimers

2. **Clean Service Agreement**
   - No PII
   - Standard clauses
   - All required disclaimers present
   - Within all policy limits

3. **Tricky Edge Cases**
   - Partial PII (incomplete SSN)
   - Lookalike characters (unicode)
   - Encoded content (base64)
   - False positives

**Process**:
1. Create markdown files in `data/sample_documents/`
2. Upload via UI
3. Run review process
4. Analyze agent results
5. Verify correct classification and flagging

### Activity 8: Red Team Your Own System (90 minutes)

**Goal**: Find vulnerabilities through adversarial testing

**Methodology**:
1. **Brainstorm attacks**: List 5 ways to bypass PII detection
2. **Implement tests**: Add to `redteam.py` or test via UI
3. **Document findings**: Which attacks succeed?
4. **Propose fixes**: How would you prevent each attack?
5. **Implement one fix**: Choose the highest priority

**Example Attack Vectors**:
- Leetspeak variations (e.g., `3m@il@ddr3ss.c0m`)
- Whitespace injection (`S SN: 1 2 3-4 5-6 7 8 9`)
- Concatenation across lines
- Homoglyph substitution (Cyrillic а vs Latin a)
- JSON/XML encoding
- Comment hiding (`<!-- SSN: 123-45-6789 -->`)

## Code Deep Dives

### Deep Dive 1: Agent Coordination

**File**: `backend/app/agents/pipeline.py`

Key concepts:
- Sequential execution with data passing
- Error handling and recovery
- HITL interruption points
- Resume after HITL approval

**Exercise**: Add a 5th agent (e.g., "Translator" for multi-language support)

### Deep Dive 2: PII Pattern Matching

**File**: `backend/app/agents/extractor.py`

Key concepts:
- Regex patterns for structured data
- Context extraction (surrounding text)
- Risk-based classification
- Multiple redaction strategies

**Exercise**: Improve name detection (current pattern is too simple)

### Deep Dive 3: Risk Assessment Logic

**File**: `backend/app/agents/reviewer.py`

Key concepts:
- Multi-factor risk calculation
- Policy violation detection
- Recommendation generation
- Risk score aggregation

**Exercise**: Add a risk scoring system (0-100) instead of high/medium/low

## Discussion Questions

1. **Multi-Agent Design**
   - Why use multiple specialized agents instead of one general agent?
   - What are the trade-offs of sequential vs parallel execution?
   - How would you handle agent failures gracefully?

2. **PII Protection**
   - When should you mask vs generalize vs refuse?
   - How do you balance security with usability?
   - What are the limitations of regex-based detection?
   - Would ML improve PII detection? How?

3. **HITL Philosophy**
   - What types of decisions should always require human approval?
   - How do you prevent HITL from becoming a bottleneck?
   - What's the right balance between automation and human oversight?

4. **Red Team Testing**
   - How often should red team tests be run?
   - Who should conduct red team testing?
   - How do you prioritize fixing discovered vulnerabilities?

5. **Compliance & Audit**
   - What information must be logged for compliance?
   - How long should audit logs be retained?
   - What are the privacy implications of logging PII detection?

## Extension Projects

### Project 1: LLM Integration (Advanced)

Integrate an LLM (GPT-4, Claude, etc.) for:
- Advanced clause analysis
- Natural language risk assessment
- Contextual PII detection
- Recommendation generation

### Project 2: Collaborative Review (Advanced)

Add multi-user support:
- Multiple reviewers
- Consensus-based approval
- Role-based permissions
- Review assignments

### Project 3: PDF Support (Medium)

Add PDF document processing:
- PDF text extraction
- OCR for scanned documents
- Layout preservation in output
- Metadata extraction

### Project 4: Real-time Collaboration (Advanced)

Add WebSocket support for:
- Live document editing
- Real-time PII highlighting
- Collaborative review sessions
- Live KPI dashboard

### Project 5: ML-Based PII Detection (Advanced)

Replace regex with ML:
- Train NER model for PII
- Use spaCy or Hugging Face Transformers
- Compare accuracy vs regex
- Handle contextual PII

## Assessment Criteria

You will be evaluated on:

1. **Understanding** (40%)
   - Can you explain the multi-agent architecture?
   - Do you understand PII detection strategies?
   - Can you trace data flow through the system?

2. **Implementation** (40%)
   - Did you complete the activities?
   - Is your code clean and well-documented?
   - Do your enhancements work correctly?

3. **Critical Thinking** (20%)
   - Did you identify limitations?
   - Did you propose meaningful improvements?
   - Did you find security vulnerabilities?

## Resources

### RegEx Resources
- [Regex101](https://regex101.com/) - Test regex patterns
- [RegExr](https://regexr.com/) - Learn regex with visual feedback

### Security Testing
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Red Team Guide](https://redteam.guide/)

### Multi-Agent Systems
- [Multi-Agent Systems Design Patterns](https://martinfowler.com/articles/patterns-of-distributed-systems/)
- [Agent Coordination Patterns](https://www.enterpriseintegrationpatterns.com/)

### Compliance
- [GDPR Guidelines](https://gdpr.eu/)
- [HIPAA Security Rule](https://www.hhs.gov/hipaa/for-professionals/security/)

## Next Steps

After completing this exercise:

1. Review your code with peers
2. Present one enhancement you made
3. Discuss security findings
4. Propose real-world applications
5. Consider how this scales to production

## Getting Help

- Review the README.md for setup issues
- Check SETUP.md for configuration problems
- Read code comments for implementation details
- Ask instructor for clarification
- Collaborate with classmates

Good luck! 🚀

