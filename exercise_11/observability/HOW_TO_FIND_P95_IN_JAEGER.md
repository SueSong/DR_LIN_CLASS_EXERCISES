# How to See p95 and Failure Rate in Jaeger UI

## You're Currently Looking At...

❌ **Child operation spans:** `guard.check_message`, `model.generate_advice`

✅ **What you need:** **Root HTTP request spans** (end-to-end requests)

---

## Step-by-Step: Find End-to-End Spans

### Step 1: Change Operation Filter

**Current:** Operation = `guard.check_message` ❌

**Change to:**

1. In the **Operation** dropdown (top of left sidebar)
2. **Select: `POST /api/coach/start`** 
   - OR look for operations starting with `POST /` or `GET /`
   - OR select **"all"** first, then look for HTTP operations

**Why?** These are the **root/parent spans** that contain all child operations!

### Step 2: Look for HTTP Operations

After changing the operation filter, you should see traces like:

```
POST /api/coach/start          1.2s    [Trace ID]
POST /api/coach/start          0.9s    [Trace ID]
POST /api/coach/start          1.5s    [Trace ID]
```

**These durations (1.2s, 0.9s, 1.5s) are your END-TO-END latencies!**

### Step 3: Calculate p95 Manually

**From the trace list:**

1. **Sort by Duration** (click the "Duration" column header)
2. Count total traces shown (e.g., 100 traces)
3. Find the trace at **95th position** (when sorted longest to shortest)
4. Check its duration:
   - ✅ If < 2500ms (2.5s) → **PASS**
   - ❌ If ≥ 2500ms → **FAIL**

**Example:**
- 100 traces total
- Trace #5 (5th longest) = p95 position
- Its duration: 2.1s
- ✅ **2.1s < 2.5s → PASS!**

---

## Alternative: Use "All Operations" View

### If you can't find `POST /api/coach/start`:

1. **Set Operation = "all"** (or clear the filter)
2. **Look for traces with these names:**
   - `POST /api/coach/start`
   - `GET /api/coach/stream`
   - WebSocket operations (these also show end-to-end)

3. **Check the trace list** - the operation name should be an HTTP route

---

## Visual Guide: What You Should See

### ❌ What You See Now (Child Spans):
```
Operation: guard.check_message
├─ Trace: guard.check_message (15ms)  ← Too small!
├─ Trace: guard.check_message (12ms)
└─ Trace: guard.check_message (18ms)
```

### ✅ What You Need (Root Spans):
```
Operation: POST /api/coach/start
├─ Trace: POST /api/coach/start (1.2s)  ← END-TO-END!
├─ Trace: POST /api/coach/start (0.9s)
└─ Trace: POST /api/coach/start (1.5s)
```

---

## Step 4: Click on a Root Span Trace

When you click a trace like `POST /api/coach/start`, you'll see:

```
┌─────────────────────────────────────────────────────────┐
│ POST /api/coach/start                                    │
│ Duration: 1.2s  ← THIS IS END-TO-END LATENCY!           │
│                                                          │
│ Timeline View:                                           │
│ [════════════════════════════════] 1.2s                 │
│  ├─[══] guard.check_message (15ms)                      │
│  ├─[═══] retrieval.retrieve (45ms)                     │
│  └─[════════════════════] model.generate_advice (1100ms)│
│                                                          │
│ Tags:                                                    │
│   http.method: POST                                     │
│   http.route: /api/coach/start                          │
│   http.status_code: 200                                  │
└─────────────────────────────────────────────────────────┘
```

**The top-level span duration (1.2s) = your end-to-end latency!**

---

## Step 5: Check Failure Rate

### Find Failed Requests:

**Method 1: Add Tag Filter**

1. In Jaeger search, look for **"Tags"** section (below Operation)
2. Add tag:
   ```
   http.status_code>=400
   ```
3. Click "Find Traces"
4. Count how many traces appear (these are failures)

**Method 2: Visual Check**

1. Look for traces with **red error indicators** (⚠️)
2. Or traces where `http.status_code` is 400, 500, etc.

**Calculate:**
```
Total requests = All traces shown (when http.status_code filter is removed)
Failed requests = Traces with http.status_code >= 400
Failure rate = (Failed / Total) × 100%
```

**Example:**
- Total: 1000 traces
- Failed: 3 traces (http.status_code = 500)
- Failure rate: 3/1000 = 0.3% ✅ (< 1% → PASS)

---

## Quick Checklist

✅ **Found root spans:** Operation shows `POST /api/...` or HTTP routes  
✅ **See durations:** Trace list shows durations like 1.2s, 0.9s, etc.  
✅ **Can sort:** Click "Duration" column to sort by latency  
✅ **See errors:** Look for red indicators or http.status_code >= 400  

---

## Troubleshooting

**Don't see `POST /api/coach/start` in Operation dropdown?**

1. **Try "all operations"** first
2. **Look for any HTTP method** (POST, GET, etc.)
3. **Check if traces exist:** Set time range to "Last 1 hour"
4. **Verify backend is running:** Check that traces are being sent

**Duration shows "0µs" or very small values?**

- You're looking at **child spans** (like `guard.check_message`)
- Need to find the **parent/root span** that contains them
- Look for spans with `http.method` tags

**Want exact p95 calculation?**

- Export trace durations (if Jaeger allows)
- Or use k6 output (easier!): `k6 run coach_scenario.js`
- k6 shows: `p(95)=2.3s` directly

---

## Recommended: Use Both Methods

1. **Jaeger:** Visual inspection, trace debugging, span details
2. **k6 Output:** Exact p95 and failure rate calculations

**Best of both worlds!** 🎯

