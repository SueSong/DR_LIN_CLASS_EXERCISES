# Where to Find Billing Configuration Values

## Configuration File: `billing/ledger.py`

All configuration values are defined at the **top** of `billing/ledger.py`:

### Line 17: Token Estimation
```python
CHARS_PER_TOKEN = 4.0
```
**Location**: `billing/ledger.py` line 17  
**What it does**: Characters per token ratio (~4 chars = 1 token)  
**To change**: Edit this line

---

### Lines 21-22: Cost Pricing
```python
INPUT_COST_PER_MILLION = 30.0   # $30 per 1M input tokens
OUTPUT_COST_PER_MILLION = 60.0  # $60 per 1M output tokens
```
**Location**: `billing/ledger.py` lines 21-22  
**What it does**: Cost per 1 million tokens (input and output)  
**To change**: Edit these lines

---

### Line 63: Daily Budget
```python
self.daily_budget_usd = 100.0  # $100/day default
```
**Location**: `billing/ledger.py` line 63 (inside `__init__` method)  
**What it does**: Default daily budget limit  
**To change**: Edit this line OR use API/dashboard

---

## How to Change Values

### Method 1: Edit the File Directly

Open `billing/ledger.py` and modify:

```python
# Line 17 - Token estimation
CHARS_PER_TOKEN = 4.0  # Change to your ratio

# Lines 21-22 - Cost pricing
INPUT_COST_PER_MILLION = 30.0   # Change to your model's pricing
OUTPUT_COST_PER_MILLION = 60.0  # Change to your model's pricing

# Line 63 - Daily budget (in __init__ method)
self.daily_budget_usd = 100.0  # Change default budget
```

### Method 2: Change Budget via API (No Code Edit)

The **daily budget** can also be changed via API without editing code:

```bash
# Set budget to $50/day
curl -X POST http://localhost:8011/api/billing/budget \
  -H "Content-Type: application/json" \
  -d '{"daily_budget_usd": 50.0}'
```

Or via admin dashboard:
- Visit: http://localhost:3082/admin/billing
- Use the "Update Budget" form

---

## Quick Reference

| Value | Location | Line | Can Change Via API? |
|-------|----------|------|---------------------|
| Token Estimation | `ledger.py` | 17 | ❌ No (code only) |
| Input Cost | `ledger.py` | 21 | ❌ No (code only) |
| Output Cost | `ledger.py` | 22 | ❌ No (code only) |
| Daily Budget | `ledger.py` | 63 | ✅ Yes (API/dashboard) |

---

## Example: Changing to Different Model Pricing

If you're using a different model (e.g., GPT-3.5 which is cheaper):

```python
# In billing/ledger.py

# GPT-3.5 Turbo pricing example
INPUT_COST_PER_MILLION = 0.5    # $0.50 per 1M input tokens
OUTPUT_COST_PER_MILLION = 1.5   # $1.50 per 1M output tokens
```

Then restart your backend server for changes to take effect.

