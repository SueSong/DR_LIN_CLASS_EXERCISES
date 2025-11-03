# How to Get p95 and Failure Rate from Jaeger UI

## What You're Currently Seeing

In your screenshot, you're looking at:
- **Operation:** `guard.check_message` (individual guard spans)
- **Duration:** ~1ms (very fast - just the guard check itself)

❌ **This is NOT the end-to-end latency!**

For SLO metrics (p95 ≤ 2.5s), you need **end-to-end request spans**, not individual operation spans.

---

## Step-by-Step: Finding End-to-End Latency in Jaeger

### Step 1: Change Your Search Filters

**Don't filter by operation!** Instead:

1. **Service:** Keep `child-growth-assistant`
2. **Operation:** Change to **"all"** (or leave empty)
3. **Time Range:** Set to cover your load test period (e.g., "Last 1 hour")

**Why?** You need to see ALL traces, including the root HTTP/WebSocket requests that contain the full end-to-end latency.

### Step 2: Look for Root HTTP Spans

After clicking "Find Traces", look for traces with operation names like:

- `POST /api/coach/start` ← Session start requests
- `GET /api/coach/stream` ← SSE streaming requests
- `WebSocket /ws/coach/{session_id}` ← WebSocket connections

These are the **parent spans** that contain the full request duration.

### Step 3: Identify End-to-End Latency

**Option A: Look at Trace List**

In the trace list, each trace shows its **total duration**:
```
child-growth-assistant: POST /api/coach/start abc123
3 Spans | 1.2s | Today 1:17:35 pm
                      ↑
                 This is the end-to-end latency!
```

**Option B: Click on a Trace**

1. Click any trace
2. Look at the **root span** (top-most span in the timeline)
3. Check its **Duration** (shown in the span details)

**Example Trace Structure:**
```
POST /api/coach/start (Duration: 1.2s)  ← ROOT SPAN - This is end-to-end!
├── guard.check_message (15ms)
├── retrieval.retrieve (45ms)
└── model.generate_advice (1100ms)
```

---

## How to Calculate p95 from Jaeger UI

### Method 1: Manual Calculation (Small Sample)

If you have < 100 traces visible:

1. **Note down all durations** from the trace list
   ```
   Trace 1: 1.1s
   Trace 2: 1.3s
   Trace 3: 0.9s
   Trace 4: 2.1s
   Trace 5: 1.5s
   ... (continue for all traces)
   ```

2. **Sort durations** (highest to lowest)
   ```
   2.1s, 1.5s, 1.3s, 1.1s, 0.9s, ...
   ```

3. **Find 95th percentile**
   - If you have 100 traces: position 95
   - If you have 50 traces: position 47-48 (round up)
   - Formula: `position = ceil(total_count * 0.95)`

4. **Check if p95 < 2.5s**

### Method 2: Use Duration Filter (Quick Check)

1. In Jaeger search panel, set **"Max Duration"** filter:
   - Try: `2.5s` (your SLO target)
2. Click "Find Traces"
3. **Count how many traces are shown**

**Interpretation:**
- If **< 5% of traces** have duration > 2.5s → **PASS** ✅
- If **≥ 5% of traces** have duration > 2.5s → **FAIL** ❌

**Quick Test:**
- Remove Max Duration filter → Note total count (e.g., 1000)
- Set Max Duration = `2.5s` → Note count (e.g., 980)
- Calculate: (1000 - 980) / 1000 = 2% → **PASS** ✅ (less than 5%)

### Method 3: Use Sort Feature

1. Click **"Sort: Most Recent"** dropdown
2. Change to **"Longest First"** or **"Shortest First"**
3. Scroll to position 95 (or 5% from bottom if sorted longest first)
4. Check that trace's duration

---

## How to Calculate Failure Rate

### Step 1: Identify Failed Requests

Failed requests in Jaeger typically show:
- **Red indicator** (⚠️ or error icon)
- **Error tags** when you click the trace:
  - `http.status_code >= 400`
  - `error=true`
  - `error.message` (contains error details)

### Step 2: Count Failures

**Method A: Visual Count**

1. Scan the trace list for red error indicators
2. Count how many have errors
3. Note total traces shown

**Method B: Use Tag Filter**

1. In search panel, add tag:
   ```
   http.status_code>=400
   ```
2. Click "Find Traces"
3. Count the filtered results = **Failed requests**

4. Remove the filter
5. Count all traces = **Total requests**

6. Calculate:
   ```
   Failure Rate = (Failed requests / Total requests) × 100%
   ```

**Example:**
- Total requests: 1000
- Failed requests: 3
- Failure rate: 3/1000 = 0.3% ✅ (< 1% target)

---

## What Your Screenshot Shows

From your screenshot:
- **Operation:** `guard.check_message`
- **Durations:** ~1ms (0.998ms, 1ms)

❌ **These are individual guard spans, NOT end-to-end requests!**

### To Fix This:

1. **Clear the Operation filter** (select "all")
2. **Look for traces with operation:**
   - `POST /api/coach/start`
   - `GET /api/coach/stream`
   - Or WebSocket operations
3. **Check their durations** (should be in seconds, not milliseconds)

---

## Recommended Workflow for Task 7

### 1. Run Load Test First

```bash
cd exercise_11/load/k6
k6 run coach_scenario.js --duration 15m --vus 10
```

**This gives you the exact metrics:**
```
http_req_duration p(95)=2.3s  ← Use this!
http_req_failed rate=0.00%    ← Use this!
```

### 2. Then Verify in Jaeger

1. Open Jaeger: http://localhost:16686
2. **Service:** `child-growth-assistant`
3. **Operation:** **"all"** (don't filter!)
4. **Time Range:** Set to cover your 15-minute test
5. **Sort by:** "Longest First"
6. **Check:** Are most traces < 2.5s? ✅
7. **Check:** Any red error indicators? Count them.

### 3. Document Results

```
SLO Compliance (15-minute load test):
- p95 latency: 2.3s ✅ (from k6 output, target: ≤ 2.5s)
- Failure rate: 0.0% ✅ (from k6 output, target: ≤ 1%)
- Verified in Jaeger: All traces < 2.5s, no errors visible
```

---

## Quick Reference: What to Look For

| What You See | What It Means | Action |
|-------------|---------------|--------|
| `guard.check_message` | Individual guard span (~1ms) | ❌ Not end-to-end |
| `retrieval.retrieve` | Individual RAG span (~50ms) | ❌ Not end-to-end |
| `model.generate_advice` | Individual model span (~1s) | ❌ Not end-to-end |
| `POST /api/coach/start` | Root HTTP request | ✅ **This is it!** |
| `GET /api/coach/stream` | Root SSE request | ✅ **This is it!** |
| WebSocket operation | Root WebSocket | ✅ **This is it!** |

---

## Troubleshooting

**"I only see short durations (< 10ms)"**
→ You're filtering by individual operation spans. Remove operation filter!

**"I don't see HTTP request spans"**
→ FastAPI auto-instrumentation should create them. Check:
- Is FastAPIInstrumentor enabled? (should see in backend logs)
- Try filtering by service only, not operation

**"How do I know which is the root span?"**
→ Root span is usually:
- The top-most span in the trace timeline
- Has operation name matching HTTP method + path
- Contains child spans (guard, retrieval, model)

---

## Pro Tip

**For Task 7, use k6 output as your primary source!**

Jaeger is great for:
- ✅ Debugging individual slow requests
- ✅ Understanding trace structure
- ✅ Visualizing system behavior

k6 is better for:
- ✅ Exact p95 calculation
- ✅ Exact failure rate
- ✅ SLO compliance verification

Use both: **k6 for metrics, Jaeger for visualization!** 🎯

