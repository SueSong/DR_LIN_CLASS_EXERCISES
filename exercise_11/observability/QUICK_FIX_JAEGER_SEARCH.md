# Quick Fix: Finding End-to-End Latency in Jaeger

## Issue #1: Fix Your Filter ⚠️

**Current filter (WRONG):**
```
Tags: http.status_code=200 error=true
```

This is contradictory! You can't have both success (200) AND an error.

**To find SUCCESS requests (for latency):**
```
Tags: http.status_code=200
```

**To find FAILED requests (for error rate):**
```
Tags: http.status_code>=400
```
or
```
Tags: error=true
```

**To see ALL requests:**
- **Remove the Tags filter entirely** (clear it)

---

## Issue #2: You're Looking at Child Spans

**What you're seeing:**
- Operation: `model.generate_advice`
- Duration: `998µs`, `1ms` (very short!)
- These are **internal operation spans**, NOT end-to-end requests

**What you NEED:**
- Operation: `POST /api/coach/start` or `GET /api/coach/stream`
- Duration: Should be **1-3 seconds** (for SLO p95 ≤ 2.5s)
- These are the **root/end-to-end spans**

---

## Step-by-Step: Find End-to-End Spans

### Step 1: Clear Conflicting Filters

1. In Jaeger UI, **clear the Tags filter** (remove `http.status_code=200 error=true`)
2. Leave only:
   - Service: `child-growth-assistant`
   - Operation: `all` (or try specific operations)

### Step 2: Change Operation Filter

**Try these operations one at a time:**

**Option A: HTTP Endpoints**
- Operation: `POST /api/coach/start`
- Operation: `GET /api/coach/stream`

**Option B: Look for HTTP Method Tags**
- Keep Operation: `all`
- Add Tag filter: `http.method=POST`
- This will show HTTP POST requests (like starting sessions)

### Step 3: Check Duration Filter

Set **Min Duration** filter:
- Minimum: `100ms` (to exclude very fast health checks)
- Maximum: `5s` (to focus on normal requests)

This will filter out:
- Very fast traces (< 100ms)
- Extremely slow traces (> 5s)

### Step 4: Look at Trace List

**What to look for:**

✅ **GOOD - Root spans:**
```
child-growth-assistant: POST /api/coach/start
Duration: 1.2s
Spans: 5
```

✅ **GOOD - Root spans:**
```
child-growth-assistant: GET /api/coach/stream  
Duration: 2.1s
Spans: 8
```

❌ **BAD - Child spans (what you're seeing now):**
```
child-growth-assistant: model.generate_advice
Duration: 998µs  ← Too short! This is internal only.
Spans: 3
```

---

## Step 5: Click on a Root Span

When you click a root span, you should see:

**Timeline view:**
```
[════════════════════════════] 1.2s ← ROOT SPAN
  ├─[═] guard.check_message (15ms)
  ├─[══] retrieval.retrieve (45ms)  
  └─[════════════════] model.generate_advice (1100ms)
```

**The ROOT span duration = your end-to-end latency!**

---

## Quick Search Configuration

### For Success Requests (Latency):
```
Service: child-growth-assistant
Operation: all (or POST /api/coach/start)
Tags: http.status_code=200
Min Duration: 100ms
Max Duration: (leave empty)
Lookback: Last 6 Hours
Limit: 100
```

### For Failed Requests (Error Rate):
```
Service: child-growth-assistant
Operation: all
Tags: http.status_code>=400
(or)
Tags: error=true
Lookback: Last 6 Hours
Limit: 100
```

---

## Why Your Durations Are So Short

You're seeing `998µs`, `1ms` because:

1. **Those are internal spans** (`model.generate_advice`)
2. They don't include:
   - HTTP request overhead
   - Guard checks
   - Retrieval time
   - Network time
   - Response serialization

**Root spans include ALL of that**, which is why they're 1-3 seconds.

---

## Quick Test

**Try this filter combination:**

```
Service: child-growth-assistant
Operation: all
Tags: http.method=POST
Min Duration: 500ms
Max Duration: (empty)
```

This should show you POST requests with durations that include the full request time.

---

## Summary

1. ✅ **Remove** `error=true` from Tags (or remove entire Tags filter)
2. ✅ **Add** `http.method=POST` or `http.method=GET` to Tags
3. ✅ **Set Min Duration** to `500ms` or `1s`
4. ✅ **Look for operations** like `POST /api/coach/start` in the trace list
5. ✅ **Duration should be 1-3 seconds** (not microseconds!)
6. ✅ **Click trace** → Check root span duration = end-to-end latency

**That root span duration is what you use for p95 calculation!** 🎯

