# Quick Start Guide - 5 Minutes

## Step 1: Start the System (1 minute)

```bash
cd exercise_9
docker-compose up --build
```

Wait for services to start. You'll see:
- ✓ Backend running on http://localhost:8000
- ✓ Frontend running on http://localhost:3000

## Step 2: Open the UI (10 seconds)

Open browser: http://localhost:3000

## Step 3: Upload a Test Document (30 seconds)

1. Click **"Documents"** in navigation
2. Click **"Choose File"**
3. Select: `data/sample_documents/nda_with_pii.md`
4. Click **"Upload Document"**
5. ✓ Document appears in the list

## Step 4: Run Document Review (1 minute)

1. Click **"Start Review Process"** button
2. Or go to **"Review"** page
3. Select the uploaded document
4. Ensure all policies are checked
5. Click **"Start Multi-Agent Review"**
6. Watch the agents work! 🤖

## Step 5: Review Results (30 seconds)

You'll see results from all 4 agents:

**✓ Classifier**: Document type = `nda`, Sensitivity = `high`

**✓ Extractor**: Found PII (SSN, credit cards, emails, etc.)

**✓ Reviewer**: Risk assessment = `high`, Policy violations detected

**✓ Drafter**: Redactions applied, disclaimers added

## Step 6: Check HITL Queue (30 seconds)

1. Click **"HITL Queue"** in navigation
2. See pending approval for high-risk items
3. Click on the item to review
4. Approve/reject each flagged PII
5. Submit decisions

## Step 7: Run a Red Team Test (1 minute)

1. Click **"Red Team"** in navigation
2. Click **"Run Test"** on "SSN Reconstruction Attack"
3. View results - should PASS (attack blocked)
4. Try other attack scenarios

## Step 8: Check KPIs (30 seconds)

1. Click **"Reports"** in navigation
2. View key metrics:
   - Clause Extraction Accuracy: ~92%
   - PII F1 Score: ~89%
   - Unauthorized Disclosures: 0 ✓
   - Review SLA Hit Rate: ~95%

## Step 9: View Audit Trail (30 seconds)

1. Click **"Audit"** in navigation
2. See complete log of all actions
3. Filter by action type
4. Search logs

## That's It! 🎉

You've completed a full document review cycle.

## What to Try Next

- Upload your own documents
- Modify policies in backend code
- Create custom red team tests
- Add new PII patterns
- Extend the agents

## Common Issues

**Services won't start?**
```bash
docker-compose down
docker-compose up --build
```

**Port already in use?**
```bash
# Check what's using the port
lsof -i :8000
lsof -i :3000
# Kill the process or use different ports
```

**No documents showing?**
- Refresh the page
- Check backend logs: `docker-compose logs backend`

## Next Steps

Read the full documentation:
- [README.md](README.md) - Complete overview
- [SETUP.md](SETUP.md) - Detailed setup
- [STUDENT_GUIDE.md](STUDENT_GUIDE.md) - Learning activities
- [ARCHITECTURE.md](ARCHITECTURE.md) - Technical details

Happy coding! 🚀

