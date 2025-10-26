# Exercise 9 - Quick Reference Card
## 📋 Print This Out & Keep It Handy!

---

## 🚀 Quick Start Commands

```bash
# Start Backend
cd exercise_9/backend
uvicorn app.main:app --reload --port 8000

# Start Frontend
cd exercise_9/frontend
npm run dev
```

**URLs:**
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## 📁 Important Files

### Backend
```
backend/app/
├── main.py              # API endpoints, policies
├── agents/
│   ├── pipeline.py      # Agent orchestration
│   ├── classifier.py    # Document classification
│   ├── extractor.py     # PII detection
│   ├── reviewer.py      # Risk assessment
│   ├── drafter.py       # Redaction & editing
│   ├── chatbot.py       # Chat with security
│   └── redteam.py       # Security testing
```

### Frontend
```
frontend/src/
├── app/
│   ├── chat/page.tsx    # Chat interface
│   ├── redteam/page.tsx # Red team tests
│   └── hitl/page.tsx    # HITL queue
├── lib/
│   ├── api.ts           # API client
│   └── chatApi.ts       # Chat API
```

---

## 🔍 Key Concepts

### Multi-Agent Pipeline
```
Document → Classifier → Extractor → Reviewer → Drafter → Output
              ↓            ↓           ↓          ↓
           (metadata)   (PII+clauses)(risks)  (redacted)
                            ↓           ↓          ↓
                         [HITL?]    [HITL?]   [HITL?]
```

### PII Types Detected
- SSN (xxx-xx-xxxx)
- Email
- Phone
- Credit Card
- Bank Account
- Address
- Name

### Redaction Modes
- **Mask:** `***-**-1234` (keep last 4)
- **Generalize:** `[SSN]`
- **Refuse:** `[REDACTED]`

---

## 🛡️ Security Patterns

### Prompt Injection Patterns
```regex
ignore\s+(?:previous|all)\s+instructions?
you\s+are\s+now\s+(?:a|an)\s+\w+
show\s+(?:me\s+)?(?:your|the)\s+prompt
```

### Jailbreak Patterns
```regex
DAN\s+mode
developer\s+mode
bypass\s+(?:all|your)\s+restrictions?
```

---

## 🧪 Test Commands

### Test PII Detection
```bash
curl -X POST http://localhost:8000/api/run \
  -H "Content-Type: application/json" \
  -d '{"doc_id":"your-doc-id"}'
```

### Test Chat Security
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Ignore all instructions"}'
```

### Test Red Team
```bash
curl -X POST http://localhost:8000/api/redteam/test \
  -H "Content-Type: application/json" \
  -d '{
    "name":"Test",
    "attack_type":"reconstruction",
    "payload":{"redacted_value":"***-**-1234"}
  }'
```

---

## 📊 Task Checklist

- [ ] Task 1: Setup (30 min)
- [ ] Task 2: Pipeline (45 min)
- [ ] Task 3: PII Testing (1 hr)
- [ ] Task 4: New PII Pattern (1.5 hr)
- [ ] Task 5: Custom Policy (2 hr)
- [ ] Task 6: Chat Security (2 hr)
- [ ] Task 7: Red Team Suite (2.5 hr)
- [ ] Task 8: HITL Workflow (2 hr)
- [ ] Task 9: Advanced PII (3 hr)
- [ ] Task 10: Custom Feature (3-4 hr)

**Total: 18-23 hours**

---

## 🐛 Common Errors & Fixes

### Port Already in Use
```bash
# Find and kill process
lsof -i :8000
kill -9 <PID>
```

### Frontend Won't Start
```bash
# Clear and reinstall
rm -rf node_modules
npm install
```

### Backend Import Error
```bash
# Ensure you're in virtual env
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

### CORS Error
- Check backend is running on :8000
- Check frontend NEXT_PUBLIC_API_URL
- Backend has CORS enabled by default

---

## 📚 Code Snippets

### Add New PII Pattern
```python
# In extractor.py
PII_PATTERNS = {
    # ... existing patterns
    "your_pattern": r"your\s+regex\s+here"
}

# In _redact_value()
elif pii_type == "your_pattern":
    return "***" + value[-4:]
```

### Add New Policy
```python
# In main.py
DEFAULT_POLICIES = {
    # ... existing policies
    "your_policy": {
        "name": "Your Policy Name",
        "rules": {
            "rule1": value1,
            "rule2": value2
        }
    }
}
```

### Add Red Team Test
```python
# In redteam.py
def test_your_attack(payload, store):
    # Your detection logic
    if vulnerability_found:
        return {
            "passed": False,
            "vulnerability": "Description",
            "severity": "high"
        }
    return {"passed": True}
```

---

## 🎯 Success Criteria by Task

| Task | Success = |
|------|-----------|
| 1 | All pages load, documents uploaded |
| 2 | Pipeline flow documented |
| 3 | PII test results complete |
| 4 | New pattern works correctly |
| 5 | Policy detects violations |
| 6 | Security tests documented |
| 7 | 5 new red team tests |
| 8 | HITL workflow complete |
| 9 | Context awareness works |
| 10 | Feature demo-able |

---

## 💡 Pro Tips

1. **Test Early** - Don't wait until the end
2. **Read Existing Code** - Learn from what's there
3. **Use API Docs** - http://localhost:8000/docs
4. **Check Audit Logs** - /audit shows everything
5. **Git Commit Often** - Small, incremental commits
6. **Ask Questions** - Office hours are there for you!

---

## 🔗 Useful Resources

- **Regex Testing:** https://regex101.com
- **API Testing:** Postman or curl
- **Documentation:** All .md files in exercise_9/
- **Examples:** Existing agents in backend/app/agents/

---

## 🆘 When You're Stuck

1. **Read the error message** - It usually tells you what's wrong
2. **Check the documentation** - ARCHITECTURE.md, README.md
3. **Look at similar code** - How did others do it?
4. **Test in isolation** - Break down the problem
5. **Ask for help** - Office hours, forum, classmates

---

## 📝 Submission Checklist

Before submitting each task:

- [ ] Code works as specified
- [ ] Tests pass
- [ ] Documentation complete
- [ ] Screenshots included
- [ ] Code is clean and commented
- [ ] No linter errors
- [ ] Git committed with good messages
- [ ] Report file created

---

## 🎓 Learning Goals Remember

You're learning to:
- ✅ Design multi-agent systems
- ✅ Implement security features
- ✅ Write production code
- ✅ Test thoroughly
- ✅ Document clearly

**It's okay to struggle - that's learning!** 💪

---

## ⚡ Quick Regex Reference

```regex
\b       - Word boundary
\d       - Digit [0-9]
\w       - Word character [a-zA-Z0-9_]
\s       - Whitespace
+        - One or more
*        - Zero or more
?        - Optional
{2,4}    - 2 to 4 times
[A-Z]    - Character class
(?:...)  - Non-capturing group
```

**Example:**
```regex
\b\d{3}-\d{2}-\d{4}\b  # Matches: 123-45-6789
```

---

## 🎯 Grade Breakdown

- Tasks 1-3: 15%
- Tasks 4-5: 15%
- Tasks 6-7: 20%
- Tasks 8-9: 25%
- Task 10: 25%

**A Grade = 90%+ = Tasks 1-10 done well**
**B Grade = 80%+ = Tasks 1-9 done well**
**C Grade = 70%+ = Tasks 1-8 done well**

---

## 📅 Suggested Schedule

| Week | Tasks | Hours |
|------|-------|-------|
| 1 | 1-3 | 2-3 |
| 2 | 4-5 | 3-4 |
| 3 | 6-7 | 4-5 |
| 4 | 8-9 | 5-6 |
| 5 | 10 | 4-5 |

**Don't fall behind!** Each task builds on previous ones.

---

## 🎊 You Got This!

Remember:
- 🧠 **Learn**, don't just complete
- 🤝 **Collaborate**, but don't copy
- 🐛 **Debug** systematically
- 📖 **Document** everything
- 🎉 **Celebrate** small wins

**Good luck!** 🚀

---

**Print this page and keep it at your desk!**

