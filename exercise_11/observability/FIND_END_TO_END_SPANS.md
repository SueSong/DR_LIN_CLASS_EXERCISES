# How to Find End-to-End Request Spans in Jaeger

## What are End-to-End Request Spans?

**End-to-end spans** are the **root/top-level spans** that represent a complete request from start to finish. They include all nested operations (guard, retrieval, model).

## Step-by-Step Guide

### Step 1: Open Jaeger UI

1. Go to: **http://localhost:16686**
2. Select service: **`child-growth-assistant`**
3. Set time range: **Last 1 hour** (or your test period)
4. Click **"Find Traces"**

### Step 2: Identify End-to-End Spans by Operation Name

Look for these **operation names** in the trace list:

#### For HTTP Requests:
- **`POST /api/coach/start`** - Starting a coaching session
- **`GET /healthz`** - Health checks
- **`GET /readyz`** - Readiness checks

#### For WebSocket:
- **`/ws/coach/{session_id}`** or **`GET /ws/coach/{session_id}`** - WebSocket connections

#### For SSE (Server-Sent Events):
- **`POST /api/coach/stream`** - Streaming advice endpoint

**These are your end-to-end spans!**

### Step 3: Filter by Operation (Easiest Way!)

**In Jaeger UI:**

1. Look for the **"Operation"** dropdown (next to Service dropdown)
2. Select one of these operations:
   - `POST /api/coach/start` ← Most common for k6 tests
   - `GET /ws/coach/{session_id}` ← For WebSocket traces
   - `POST /api/coach/stream` ← For SSE traces

3. Click **"Find Traces"**

**This filters to show only end-to-end request spans!**

### Step 4: View Trace Details

1. **Click on any trace** in the list
2. You'll see a **trace timeline** with nested spans:

```
Trace Timeline View:
┌─────────────────────────────────────────────────────────────┐
│ POST /api/coach/start                    [1.2s] ← ROOT SPAN │
│ ├── guard.check_message              [15ms]                 │
│ ├── retrieval.retrieve               [45ms]                  │
│ └── model.generate_advice            [1100ms]               │
└─────────────────────────────────────────────────────────────┘
```

**The top-level span (POST /api/coach/start) is your end-to-end span!**

**⚠️ If you only see child spans:**
If you see:
- `guard.check_message`
- `retrieval.retrieve`
- `model.generate_advice`

**These are CHILD spans - you need to look UP to find the PARENT span!**

**To find the root span:**
1. Look at the **left side** of the trace timeline
2. Find the **topmost/leftmost span** (no indentation)
3. That's your end-to-end span
4. It might be named:
   - `POST /api/coach/start`
   - `POST /api/coach/stream`
   - WebSocket operation
   - Or just show the HTTP method + path

**The root span contains all child spans and represents the full request!**

### Step 5: Read the End-to-End Duration

**Method 1: From Trace Timeline**
- The **topmost bar** shows the total duration
- Look at the **right side** - it shows duration in milliseconds/seconds

**Method 2: From Span Details**
1. Click the **root span** (top-level HTTP request)
2. Look at **"Duration"** field
3. Or check the **Tags** section for duration info

---

## Visual Guide: What to Look For

### In Trace List View:

```
┌────────────────────────────────────────────────────────────┐
│ Jaeger UI - Trace Search Results                          │
├────────────────────────────────────────────────────────────┤
│ Service: child-growth-assistant                           │
│ Operation: POST /api/coach/start  ← Filter by this!       │
│                                                             │
│ Trace List:                                                │
│ ┌──────────────────────────────────────────────────────┐  │
│ │ POST /api/coach/start         1.2s   [Trace ID]  ←──┐ │  │
│ └──────────────────────────────────────────────────────┘  │  │
│ ┌──────────────────────────────────────────────────────┐  │
│ │ POST /api/coach/start         0.9s   [Trace ID]  ←──┘ │  │
│ └──────────────────────────────────────────────────────┘  │  │
│                                                             │
│ These are END-TO-END spans!                                │
└────────────────────────────────────────────────────────────┘
```

### In Trace Detail View:

```
┌────────────────────────────────────────────────────────────┐
│ Trace Details                                              │
├────────────────────────────────────────────────────────────┤
│ POST /api/coach/start                                       │
│ Duration: 1.2s  ← END-TO-END LATENCY                       │
│                                                             │
│ Timeline:                                                   │
│ [════════════════════════════════════════] 1.2s            │
│  ├─[══] guard.check_message (15ms)                          │
│  ├─[═══] retrieval.retrieve (45ms)                        │
│  └─[═══════════════════════════] model (1100ms)            │
│                                                             │
│ Tags:                                                       │
│   http.method: POST                                         │
│   http.url: /api/coach/start                                │
│   http.status_code: 200                                     │
│   http.route: /api/coach/start                              │
└────────────────────────────────────────────────────────────┘
```

---

## Quick Tips

### Tip 1: Sort by Duration

1. Click the **"Duration"** column header to sort
2. Longest durations = slowest end-to-end requests
3. These are the ones you care about for p95!

### Tip 2: Filter by Tags

Add these tag filters to find specific spans:

**For HTTP endpoints:**
```
http.method=POST
http.url=/api/coach/start
```

**For successful requests:**
```
http.status_code=200
```

**For failed requests:**
```
http.status_code>=400
```

### Tip 3: Identify Root vs Child Spans

**Root Span (End-to-End):**
- ✅ Has `http.method` tag
- ✅ Has `http.url` or `http.route` tag
- ✅ Usually named like `POST /api/...`
- ✅ Appears at the **top** of trace hierarchy

**Child Spans:**
- ✅ Have `guard.*`, `retrieval.*`, or `model.*` attributes
- ✅ Are nested **under** the root span
- ✅ These are **not** end-to-end spans

---

## Example: Finding End-to-End Spans from k6 Test

When you run k6, it sends:
1. `POST /api/coach/start` ← This creates end-to-end spans
2. WebSocket connections

### To Find These:

**Step 1:** Open Jaeger → http://localhost:16686

**Step 2:** Select:
- Service: `child-growth-assistant`
- Operation: `POST /api/coach/start` (from dropdown)

**Step 3:** Click "Find Traces"

**Step 4:** You'll see a list like:
```
POST /api/coach/start    1.2s   [Trace ID: abc123]
POST /api/coach/start    0.9s   [Trace ID: def456]
POST /api/coach/start    1.5s   [Trace ID: ghi789]
...
```

**These durations (1.2s, 0.9s, 1.5s) are your END-TO-END latencies!**

### Step 5: Click Any Trace

You'll see the full breakdown:
```
POST /api/coach/start (1.2s total)  ← END-TO-END
├── guard.check_message (15ms)
├── retrieval.retrieve (45ms)
└── model.generate_advice (1100ms)
```

---

## Troubleshooting

**Can't find "Operation" dropdown?**
- Make sure you've selected a service first
- Operation dropdown appears after selecting service

**Don't see any traces?**
- Check time range (set to "Last 1 hour" or wider)
- Verify backend is sending traces (check logs for "OTLP exporter configured")
- Make sure Jaeger is running: `docker ps | grep jaeger`

**See WebSocket traces but no HTTP?**
- WebSocket traces might have different operation names
- Look for operation like: `/ws/coach/...` or `GET /ws/...`

**Want to see all operations?**
- Leave "Operation" dropdown as "All Operations"
- Look for spans with `http.method` tags (these are HTTP endpoints)

---

## Summary

**End-to-End Spans = Root/Top-Level Spans**

**How to Find:**
1. Filter by Operation: `POST /api/coach/start`
2. Or look for spans with `http.method` tags
3. Or look at the top-level span in trace hierarchy

**What They Show:**
- Total request duration (guard + retrieval + model + overhead)
- This is what you need for p95 latency calculations!

The **root span duration** = your **end-to-end latency** 🎯

