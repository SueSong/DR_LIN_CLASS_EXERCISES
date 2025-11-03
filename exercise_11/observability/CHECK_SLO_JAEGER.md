# How to Check SLO Metrics from Jaeger UI

Task 7 SLO Requirements:
- **p95 latency ≤ 2.5 seconds**
- **failure rate ≤ 1%**

## Important Note

⚠️ **Jaeger shows traces, not aggregated metrics.** To get exact p95 and failure rates, you have two options:

1. **Manual calculation from Jaeger** (shown below)
2. **Use k6/Locust test output** (already provides these metrics!)
3. **Set up metrics export to Prometheus/Grafana** (for automated monitoring)

---

## Method 1: Check SLO from k6 Test Output (Easiest! ✅)

Your k6 test already calculates these metrics!

```bash
cd exercise_11/load/k6
k6 run coach_scenario.js
```

**Look for these lines in the output:**
```
http_req_duration......: avg=1.2s    min=500ms   med=1.1s    max=3.5s    p(95)=2.3s
http_req_failed........: 0.00%  ✓ 0.00% < 1.00%
```

✅ **p95 < 2.5s** → Pass!  
✅ **failure rate < 1%** → Pass!

---

## Method 2: Manual Calculation from Jaeger UI

### Step 1: Run Load Test

```bash
cd exercise_11/load/k6
k6 run coach_scenario.js --duration 30s
```

This generates traces for the last 30 seconds.

### Step 2: Open Jaeger UI

1. Go to: **http://localhost:16686**
2. Select service: **`child-growth-assistant`**
3. Set time range: **Last 1 hour** (or adjust to cover your test period)
4. Click **"Find Traces"**

### Step 3: Identify the Root Spans

You need to find the **end-to-end request spans**. These are typically:
- `POST /api/coach/start` - For starting sessions
- WebSocket spans - For coach chat requests

**Look for spans with operation name:**
- `POST /api/coach/start`
- `GET /api/coach/stream` (if using SSE)

### Step 4: Calculate p95 Latency

**Option A: Quick Visual Check**

1. **Sort traces by duration** (click "Duration" column header)
2. Count total traces shown
3. Find the trace at **95th percentile** position
4. Check its duration

**Example:**
- If you have 100 traces
- The 95th trace (when sorted longest to shortest) is your p95
- Check if its duration < 2500ms (2.5s)

**Option B: Use Trace Search Filters**

1. In Jaeger search, add tag filter:
   ```
   http.method=POST
   ```
2. Look at the trace list
3. Note durations of all traces
4. Calculate manually: Sort durations, take value at 95th percentile

**Option C: Export and Calculate**

1. In Jaeger UI, you can't directly export, but you can:
   - Note down durations from multiple pages
   - Or use browser DevTools to extract JSON
2. Calculate p95 in Python/Excel:
   ```python
   durations = [1500, 1200, 2300, ...]  # in milliseconds
   durations.sort()
   p95_index = int(len(durations) * 0.95)
   p95 = durations[p95_index]
   print(f"p95: {p95}ms")
   ```

### Step 5: Calculate Failure Rate

**Identify Failed Requests:**

Failed requests typically have:
- **HTTP status 4xx or 5xx**
- **Error tags** in the span

**In Jaeger UI:**

1. Look for traces with **red error indicators** (⚠️ or red color)
2. Check span tags for:
   - `http.status_code >= 400`
   - `error=true`
   - `error.message` (if present)

**Count failures:**

1. **Total requests** = Count all traces shown
2. **Failed requests** = Count traces with errors
3. **Failure rate** = (Failed requests / Total requests) × 100%

**Example:**
- Total traces: 1000
- Failed traces: 5
- Failure rate: 5/1000 = 0.5% ✅ (< 1%)

---

## Method 3: View Individual Span Durations

### Finding End-to-End Latency

1. Click on any trace
2. Look at the **root span** (top-level HTTP request)
3. Check its **duration** (shown at the top or in timeline)

### Trace Structure

```
Trace: POST /api/coach/start
├── Duration: 1.2s  ← This is the end-to-end latency
├── span: guard.check_message (15ms)
├── span: retrieval.retrieve (45ms)
└── span: model.generate_advice (1100ms)
```

**For WebSocket traces:**
- Look for the WebSocket connection span
- Or the `model.generate_advice` span duration
- This represents end-to-end latency

---

## Method 4: Using Jaeger Trace Comparison

### Filter by Time Range

1. Set time range to cover your load test period
2. Use filters:
   - **Service:** `child-growth-assistant`
   - **Operation:** `POST /api/coach/start` or WebSocket operation
3. Sort by duration (longest first)

### Filter by Error Status

1. Add tag filter:
   ```
   http.status_code>=400
   ```
   or
   ```
   error=true
   ```
2. Count how many traces match

---

## Recommended Approach

### For Task 7 Submission:

1. **Use k6 output** (Method 1) - It's already calculated!
   ```bash
   k6 run coach_scenario.js --duration 15m
   ```
   Look for:
   - `p(95)` value in `http_req_duration`
   - `rate` in `http_req_failed`

2. **Take screenshots from Jaeger** showing:
   - Trace timeline view
   - Span attributes showing latency
   - Error traces (if any)

3. **Document in your report:**
   ```
   SLO Results (15-minute load test):
   - p95 latency: 2.1s ✅ (target: ≤ 2.5s)
   - Failure rate: 0.3% ✅ (target: ≤ 1%)
   ```

---

## Quick Checklist

After running k6 load test:

- [ ] k6 shows `p(95) < 2500ms` in output
- [ ] k6 shows `http_req_failed rate < 0.01` (1%)
- [ ] Jaeger UI shows traces for the test period
- [ ] No red error indicators in Jaeger (or very few)
- [ ] Trace durations visually appear reasonable (< 3s most)

---

## Troubleshooting

**Can't see traces in Jaeger?**
- Check backend logs: Should see "OTLP exporter configured"
- Verify Jaeger is running: `docker ps | grep jaeger`
- Check time range in Jaeger UI (set to "Last 1 hour")

**Traces missing durations?**
- Ensure OpenTelemetry instrumentation is enabled
- Check that FastAPI instrumentation is working
- Verify spans are being created (check backend console output)

**Need exact metrics?**
- Use k6 output - it's most accurate
- Or set up Prometheus metrics export (separate setup)

---

## Example k6 Output Interpretation

```
http_req_duration......: avg=1.2s    min=500ms   med=1.1s    max=3.5s    p(95)=2.3s    p(99)=3.0s
http_req_failed........: 0.00%  ✓ 0.00% < 1.00%
```

✅ **p95 = 2.3s** (< 2.5s target) → **PASS**  
✅ **failure rate = 0.00%** (< 1% target) → **PASS**

For 15-minute test:
```bash
k6 run coach_scenario.js --duration 15m --vus 10
```

This will show you the exact metrics you need for Task 7! 🎯

