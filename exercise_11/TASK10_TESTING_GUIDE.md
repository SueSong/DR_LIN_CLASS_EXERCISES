# Task 10: Testing Guide - Token/Cost Watchdog

## Prerequisites

Before testing, make sure:
1. ✅ Backend server is running (`http://localhost:8011`)
2. ✅ Frontend server is running (`http://localhost:3082`)
3. ✅ You're ready to make some test requests

---

## Test 1: Over-Budget Request Returns Lite Mode

**Goal**: Verify that when budget is exceeded, requests return lite mode with notice.

### Step 1: Set a Very Low Budget

**Option A: Via API (Recommended)**
```bash
curl -X POST http://localhost:8011/api/billing/budget \
  -H "Content-Type: application/json" \
  -d "{\"daily_budget_usd\": 0.01}"
```

**Option B: Via Admin Dashboard**
1. Visit: http://localhost:3082/admin/billing
2. In "Set Budget" form, enter: `0.01`
3. Click "Update Budget"

### Step 2: Make Test Requests

**Via Frontend:**
1. Open: http://localhost:3082/coach/chat
2. Start a session (enter name, click "Start Coaching Session")
3. Send a message like: "How to handle bedtime resistance?"
4. **Expected**: You should receive a **lite mode response** with a notice

**Via API (SSE):**
```bash
curl -X POST http://localhost:8011/api/coach/stream \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"How to handle bedtime?\", \"session_id\": \"test_session_1\"}"
```

**What to Look For:**
- ✅ Response is shorter/simplified
- ✅ Notice mentions "Daily budget exceeded" or "lite mode"
- ✅ Response still provides helpful guidance (just shorter)

### Step 3: Verify in Backend Logs

Check backend terminal - you should see billing information:
```
[HITL DEBUG] Message: 'How to handle bedtime?...', Classification: safe, Session: test_session_1
```

---

## Test 2: Daily Report Generation

**Goal**: Verify CSV reports are generated correctly.

### Step 1: Make Some Requests

Generate some test data:
1. Make several requests via frontend or API
2. Mix of full mode and lite mode requests (if budget exceeded)

### Step 2: Generate Report

**Via Script:**
```bash
cd exercise_11
python billing/generate_nightly_report.py --today
```

**Via API:**
```bash
# Get today's date first (e.g., 2025-11-01)
curl http://localhost:8011/api/billing/report/csv/2025-11-01 --output report.csv
```

### Step 3: Check Generated File

```bash
# Check if file exists
ls billing/reports/billing_report_*.csv

# View contents (Windows PowerShell)
Get-Content billing\reports\billing_report_*.csv

# Or open in Excel/spreadsheet app
```

**Expected CSV Structure:**
```csv
turn_id,session_id,timestamp,input_tokens,output_tokens,total_tokens,cost_usd,model_mode,was_over_budget
turn_...,sess_123,2025-11-01T...,100,500,600,0.000045,full,false
```

---

## Test 3: Admin Dashboard

**Goal**: Verify admin dashboard shows budget status and sparkline.

### Step 1: Open Dashboard

Visit: http://localhost:3082/admin/billing

### Step 2: Verify Display

**Check for:**
- ✅ Budget Status card showing:
  - Current cost
  - Budget limit
  - Remaining budget
  - Budget used percentage
  - Progress bar

- ✅ Sparkline Chart:
  - Shows 7-day cost trend
  - Visual line chart
  - Dates displayed

- ✅ Daily Statistics:
  - Total turns
  - Total cost
  - Total tokens
  - Full mode vs lite mode counts

### Step 3: Test Budget Update

1. Enter a new budget value (e.g., `50.0`)
2. Click "Update Budget"
3. **Expected**: Success message, budget status updates

### Step 4: Verify Auto-Refresh

- Dashboard should auto-refresh every 30 seconds
- Or click "Refresh Data" button manually

---

## Test 4: Budget Status API

**Goal**: Verify API endpoints work correctly.

### Test Budget Status Endpoint

```bash
# Get current budget status
curl http://localhost:8011/api/billing/budget/status
```

**Expected Response:**
```json
{
  "is_over_budget": true,
  "current_cost_usd": 0.015,
  "budget_limit_usd": 0.01,
  "budget_remaining_usd": -0.005,
  "budget_used_percent": 150.0,
  "date": "2025-11-01"
}
```

### Test Daily Stats Endpoint

```bash
# Get today's statistics
curl http://localhost:8011/api/billing/daily

# Get specific date
curl http://localhost:8011/api/billing/daily?target_date=2025-11-01
```

**Expected Response:**
```json
{
  "date": "2025-11-01",
  "total_turns": 10,
  "total_cost_usd": 0.015,
  "total_input_tokens": 1000,
  "total_output_tokens": 5000,
  "full_mode_turns": 5,
  "lite_mode_turns": 5,
  "over_budget_turns": 5,
  "budget_limit_usd": 0.01,
  "budget_remaining_usd": -0.005,
  "is_over_budget": true,
  "current_cost_usd": 0.015
}
```

### Test Sparkline Endpoint

```bash
# Get 7-day sparkline data
curl http://localhost:8011/api/billing/sparkline?days=7
```

**Expected Response:**
```json
{
  "days": 7,
  "start_date": "2025-10-25",
  "end_date": "2025-11-01",
  "data": [0.01, 0.02, 0.015, 0.03, 0.025, 0.02, 0.015],
  "labels": ["2025-10-25", "2025-10-26", ...]
}
```

---

## Test 5: Under Budget (Normal Operation)

**Goal**: Verify normal full mode operation when under budget.

### Step 1: Reset Budget

```bash
# Set normal budget
curl -X POST http://localhost:8011/api/billing/budget \
  -H "Content-Type: application/json" \
  -d "{\"daily_budget_usd\": 100.0}"
```

### Step 2: Make Requests

1. Send several normal requests
2. **Expected**: Full detailed responses (not lite mode)
3. No budget notices

### Step 3: Check Status

```bash
curl http://localhost:8011/api/billing/budget/status
```

**Expected**: `is_over_budget: false`

---

## Test 6: Integration Test (Full Flow)

**Goal**: Test the complete flow from request to billing tracking.

### Step 1: Clear Previous Data (Optional)

Restart backend server to clear in-memory ledger:
```bash
# Stop backend (Ctrl+C)
# Start backend again
```

### Step 2: Set Budget

```bash
curl -X POST http://localhost:8011/api/billing/budget \
  -H "Content-Type: application/json" \
  -d "{\"daily_budget_usd\": 1.0}"
```

### Step 3: Make Requests Until Over Budget

1. Make requests via frontend
2. After each request, check budget status:
   ```bash
   curl http://localhost:8011/api/billing/budget/status
   ```
3. **Watch for transition**: First requests should be full mode, then switch to lite mode

### Step 4: Verify Lite Mode Triggered

Once `is_over_budget: true`:
- Next request should return lite mode
- Notice should appear in response

---

## Quick Test Checklist

Run these quick tests:

```bash
# 1. Set low budget
curl -X POST http://localhost:8011/api/billing/budget \
  -H "Content-Type: application/json" \
  -d "{\"daily_budget_usd\": 0.01}"

# 2. Check status
curl http://localhost:8011/api/billing/budget/status

# 3. Make a request (should get lite mode)
curl -X POST http://localhost:8011/api/coach/stream \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"test\", \"session_id\": \"test\"}"

# 4. Check daily stats
curl http://localhost:8011/api/billing/daily

# 5. Generate report
python billing/generate_nightly_report.py --today

# 6. Check CSV file exists
ls billing/reports/*.csv
```

---

## Troubleshooting

### Issue: API returns 404
**Fix**: Make sure backend is running on port 8011

### Issue: Dashboard doesn't load
**Fix**: 
- Check frontend is running on port 3082
- Check browser console for errors
- Verify CORS is enabled

### Issue: No lite mode even with low budget
**Fix**: 
- Check budget was actually set: `curl http://localhost:8011/api/billing/budget/status`
- Make sure you're making SAFE requests (not BLOCKED/ESCALATE)
- Check backend logs for billing debug info

### Issue: CSV not generated
**Fix**:
- Check `billing/reports/` directory exists
- Check file permissions
- Run script with `--today` flag to generate for today

---

## Expected Test Results

### ✅ Test 1: Over-Budget → Lite Mode
- Low budget set
- Request made
- Lite mode response received
- Notice included

### ✅ Test 2: Daily Report
- Report script runs successfully
- CSV file created
- CSV contains turn records

### ✅ Test 3: Admin Dashboard
- Dashboard loads
- Shows budget status
- Sparkline chart visible
- Budget update works

### ✅ Test 4: API Endpoints
- All endpoints return valid JSON
- Data matches expectations

### ✅ Test 5: Under Budget
- Normal requests work
- Full mode responses
- No lite mode

---

## Success Criteria

**Task 10 passes if:**

1. ✅ Over-budget requests return lite mode with notice
2. ✅ Daily CSV report is generated successfully
3. ✅ Admin dashboard shows sparkline and statistics
4. ✅ All API endpoints work correctly

---

## Next Steps After Testing

1. **Schedule nightly reports**: Set up cron/Task Scheduler
2. **Adjust pricing**: Update cost constants if using different model
3. **Monitor costs**: Check dashboard regularly
4. **Review reports**: Analyze CSV files for cost trends

