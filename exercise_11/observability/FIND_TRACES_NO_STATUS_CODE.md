# Finding Traces Without HTTP Status Code Filter

## Why `http.status_code=200` Shows No Results

**Possible reasons:**

1. **WebSocket traces don't have HTTP status codes**
   - Your k6 test uses WebSocket (`/ws/coach/{session_id}`)
   - WebSocket connections don't have HTTP status codes in the same way
   - The status code might be `101` (WebSocket upgrade) or not set at all

2. **FastAPI instrumentation might not be setting status code tags**
   - Some versions/configurations don't add `http.status_code` automatically
   - Status codes might be in a different tag format

3. **Traces might be created before HTTP response**
   - If instrumentation happens during request, status code might not be available yet

---

## Solution: Remove HTTP Status Code Filter

**Try these filters instead:**

### Filter Option 1: Operation Name

**Clear Tags filter entirely** and use Operation filter:

```
Service: child-growth-assistant
Operation: (try each of these)
  - POST /api/coach/start
  - /api/coach/start
  - GET /api/coach/stream
  - /api/coach/stream
  - WebSocket operations (if visible)
```

### Filter Option 2: Duration Only

**Remove Tags filter, use Duration:**

```
Service: child-growth-assistant
Operation: all
Tags: (leave EMPTY or remove)
Min Duration: 500ms
Max Duration: (leave empty)
```

This will show all traces longer than 500ms, which is what you need for SLO.

### Filter Option 3: Service Only

**Simplest filter:**

```
Service: child-growth-assistant
Operation: all
Tags: (leave EMPTY)
Lookback: Last 1 hour
Limit: 100
```

Just see ALL traces from your service, then manually look for long durations.

---

## What Operations to Look For

Since your k6 test does:

1. `POST /api/coach/start` - HTTP request (should have status code)
2. WebSocket connection - No HTTP status code

**In Jaeger, look for:**

**HTTP Operations:**
- `POST /api/coach/start`
- `/api/coach/start`
- `POST /api/coach/stream` (if using SSE)

**WebSocket Operations:**
- `/ws/coach/{session_id}`
- `WebSocket /ws/coach/{session_id}`
- `GET /ws/coach/{session_id}`

These might NOT have `http.status_code` tags.

---

## Step-by-Step: Find Your Traces

### Step 1: Minimal Filter

```
Service: child-growth-assistant
Operation: all
Tags: (EMPTY - remove all text)
Min Duration: 500ms
Lookback: Last 6 hours
```

Click "Find Traces"

### Step 2: Check What Operations Appear

In the trace list, look at the **Operation** column. You should see:

- Various operation names
- Some will have short durations (< 100ms) - skip these
- Some will have long durations (500ms - 3s) - **these are your end-to-end spans!**

### Step 3: Identify Root Spans

Look for traces with:

✅ **Good signs (root spans):**
- Duration: 500ms - 3s
- Multiple spans inside (check "Spans" count)
- Operation name contains route path (`/api/coach/` or `/ws/coach/`)

❌ **Bad signs (child spans):**
- Duration: < 100ms (microseconds)
- Operation: `guard.check_message`, `retrieval.retrieve`, `model.generate_advice`
- Only 1-3 spans total

### Step 4: Click on Long-Duration Traces

Click any trace with duration > 500ms. In the detail view:

1. **Look at the timeline** - The widest bar is usually the root span
2. **Check span tags** - Look for:
   - `http.method` (POST, GET)
   - `http.route` (the route path)
   - `http.url`
   - `websocket.path` (for WebSocket)

3. **The root span duration = end-to-end latency**

---

## Alternative: Use Different Tags

Instead of `http.status_code`, try:

**For HTTP requests:**
```
Tags: http.method=POST
```

**For finding errors:**
```
Tags: error=true
```

**For WebSocket:**
```
Tags: websocket
```
(or similar WebSocket-related tags)

---

## Quick Test Configuration

**Try this exact setup:**

```
Service: child-growth-assistant
Operation: all
Tags: (completely empty - delete everything)
Min Duration: 1s
Max Duration: (empty)
Lookback: Last 1 hour
Limit: 50
```

Then:

1. Click "Find Traces"
2. Sort by **Duration** (click Duration column header)
3. Look at traces with longest durations
4. These should be your end-to-end request spans!

---

## Why This Happens

**FastAPI instrumentation behavior:**
- HTTP endpoints: Usually get `http.status_code` tags
- WebSocket endpoints: Often DON'T get `http.status_code` tags
- Internal spans: Never get HTTP tags

Since your k6 test uses WebSocket, those traces won't have `http.status_code` tags, which is why the filter returns no results!

---

## Recommended Approach

**For Task 7 SLO checking:**

1. **Remove `http.status_code` filter** entirely
2. **Use Duration filter** instead:
   - Min: `500ms` or `1s`
   - This filters for actual request traces (not fast internal spans)

3. **Sort by Duration** in trace list
4. **Manually check** top 20-50 traces
5. **Use root span durations** for p95 calculation

**Or use k6 output** (still easiest!):
```bash
k6 run coach_scenario.js --duration 15m
```
Output shows p95 directly! ✅

---

## Summary

- ❌ **Don't filter by `http.status_code`** (especially for WebSocket traces)
- ✅ **Filter by Duration** (Min: 500ms)
- ✅ **Or filter by Operation** name
- ✅ **Or use no Tags filter** and just browse all traces
- ✅ **Look for long-duration traces** (> 500ms)
- ✅ **Root span duration = end-to-end latency**

Try removing the Tags filter completely and using Duration filter instead! 🎯

