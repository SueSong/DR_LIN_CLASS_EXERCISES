# Billing & Cost Watchdog System

## Overview

The billing system tracks token usage and costs per turn/request, enforces daily budget caps, and provides "lite mode" fallback when over budget.

## Components

### 1. `billing/ledger.py`
**Purpose**: Core billing ledger that tracks all token usage and costs.

**Key Features**:
- Records each turn/request with token counts and cost
- Calculates costs based on token estimation (input + output)
- Tracks daily budgets and checks if over budget
- Generates daily CSV reports
- Provides sparkline data for visualization

**Usage**:
```python
from billing.ledger import get_ledger

ledger = get_ledger()
turn_record = ledger.record_turn(
    session_id="sess_123",
    input_text="How to handle bedtime?",
    output_text="Full advice here...",
    model_mode="full",  # or "lite"
    was_over_budget=False
)

# Check budget
is_over, current_cost, budget = ledger.is_over_budget()
```

### 2. `billing/lite_mode.py`
**Purpose**: Provides simplified responses when budget is exceeded.

**Key Features**:
- Generates shorter, cost-effective responses
- Includes budget limit notice
- Still provides helpful guidance, just more concise

### 3. `backend/app/api/billing.py`
**Purpose**: REST API endpoints for billing management.

**Endpoints**:
- `GET /api/billing/daily` - Get daily cost statistics
- `GET /api/billing/budget/status` - Get current budget status
- `POST /api/billing/budget` - Set daily budget limit
- `GET /api/billing/report` - Get summary report (last N days)
- `GET /api/billing/report/csv/{date}` - Download CSV report
- `GET /api/billing/sparkline` - Get sparkline data for charts

### 4. `billing/generate_nightly_report.py`
**Purpose**: Script to generate daily CSV reports (run via cron/scheduler).

**Usage**:
```bash
# Generate report for yesterday (default)
python billing/generate_nightly_report.py

# Generate report for today
python billing/generate_nightly_report.py --today
```

**Cron Setup** (Linux/Mac):
```bash
# Run at midnight every day
0 0 * * * cd /path/to/exercise_11 && python billing/generate_nightly_report.py
```

### 5. `frontend/src/app/admin/billing/page.tsx`
**Purpose**: Admin dashboard for viewing billing data and sparkline chart.

**Access**: http://localhost:3082/admin/billing

**Features**:
- Real-time budget status
- Daily cost statistics
- Sparkline visualization (7-day trend)
- Update budget limit
- Auto-refresh every 30 seconds

## How It Works

### Budget Checking Flow

1. **Request comes in** (SSE or WebSocket)
2. **Check budget**: `ledger.is_over_budget()`
3. **If over budget**:
   - Use `generate_lite_mode_response()` for advice
   - Send budget notice to user
   - Record turn with `was_over_budget=True`
4. **If under budget**:
   - Use full RAG content
   - Record turn with `was_over_budget=False`
5. **Record all turns**: Every request is recorded with cost tracking

### Cost Calculation

**Token Estimation**:
- Uses character count approximation: ~4 characters per token
- `input_tokens = len(input_text) / 4`
- `output_tokens = len(output_text) / 4`

**Cost Calculation**:
- Input: $30 per 1M tokens
- Output: $60 per 1M tokens
- `cost = (input_tokens / 1M * $30) + (output_tokens / 1M * $60)`

**Note**: These are example pricing. Adjust `INPUT_COST_PER_MILLION` and `OUTPUT_COST_PER_MILLION` in `ledger.py` based on your actual model pricing.

## Configuration

### Default Budget
Default daily budget: **$100/day**

**Change budget via API**:
```bash
curl -X POST http://localhost:8011/api/billing/budget \
  -H "Content-Type: application/json" \
  -d '{"daily_budget_usd": 50.0}'
```

Or via admin dashboard: http://localhost:3082/admin/billing

### Cost Pricing
Edit `billing/ledger.py`:
```python
INPUT_COST_PER_MILLION = 30.0   # $30 per 1M input tokens
OUTPUT_COST_PER_MILLION = 60.0  # $60 per 1M output tokens
```

## Testing

### Test Over-Budget Scenario

1. **Set a very low budget**:
   ```bash
   curl -X POST http://localhost:8011/api/billing/budget \
     -H "Content-Type: application/json" \
     -d '{"daily_budget_usd": 0.01}'
   ```

2. **Make a request** - Should receive lite mode response with notice

3. **Check budget status**:
   ```bash
   curl http://localhost:8011/api/billing/budget/status
   ```

### Verify Daily Report

```bash
# Generate report for today
python billing/generate_nightly_report.py --today

# Check generated CSV
ls billing/reports/billing_report_YYYY-MM-DD.csv
```

## Integration Points

### SSE Endpoint (`backend/app/api/sse.py`)
- Checks budget before generating advice
- Uses lite mode when over budget
- Records all turns in ledger
- Sends budget notice event when in lite mode

### WebSocket Endpoint (`backend/app/api/websocket.py`)
- Same integration as SSE
- Adds `budget_notice` to response JSON when in lite mode

## Pass Criteria

✅ **Task 10 passes if:**

1. **Over-budget requests return lite mode**:
   - Set budget to $0.01
   - Make a request
   - Should receive lite mode response with notice

2. **Daily report generated**:
   - Run `generate_nightly_report.py`
   - CSV file created in `billing/reports/`
   - Contains all turns for that day

3. **Admin dashboard shows sparkline**:
   - Visit http://localhost:3082/admin/billing
   - See cost trend chart
   - See budget status

## File Structure

```
billing/
├── ledger.py                    # Core billing ledger
├── lite_mode.py                 # Lite mode response generator
├── generate_nightly_report.py   # Nightly report script
├── reports/                     # Generated CSV reports
│   └── billing_report_YYYY-MM-DD.csv
└── README.md                    # This file

backend/app/api/
└── billing.py                   # Billing API endpoints

frontend/src/app/admin/billing/
└── page.tsx                      # Admin dashboard
```

## Next Steps

1. **Schedule nightly reports**: Set up cron job to run `generate_nightly_report.py` daily
2. **Adjust pricing**: Update cost constants in `ledger.py` to match your model
3. **Persist to database**: Current implementation uses in-memory storage. For production, use a database.
4. **Add alerts**: Email/Slack notifications when budget exceeded

