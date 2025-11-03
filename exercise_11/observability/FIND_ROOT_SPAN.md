# How to Find the Root/End-to-End Span in Jaeger

## You're Seeing Child Spans

If you see these spans:
- `guard.check_message`
- `retrieval.retrieve`
- `model.generate_advice`

**These are CHILD spans!** You need to find the **PARENT/ROOT span** that contains them.

---

## How to Find the Root Span

### Method 1: Look at Trace Hierarchy (Timeline View)

1. In Jaeger, click on a trace
2. Look at the **timeline/tree view** on the left side
3. Find the **topmost span** (no indentation, furthest left)

**What you're looking for:**

```
Trace Timeline (left side):
│
├─ [ROOT SPAN] ← This is your end-to-end span!
│  ├─ guard.check_message
│  ├─ retrieval.retrieve
│  └─ model.generate_advice
```

### Method 2: Check for HTTP Tags

1. Click on each span
2. Check the **Tags** section
3. Look for `http.method` or `http.route` tags

**The span with HTTP tags = Root span!**

Example tags to look for:
```
http.method: POST
http.route: /api/coach/start
http.url: /api/coach/start
http.status_code: 200
```

### Method 3: Look for Parent-Child Relationship

1. Click on `guard.check_message` span
2. Look for **"References"** or **"Parent"** section
3. It will show the parent span name
4. Click on that parent span
5. That's your root/end-to-end span!

### Method 4: Check Span Order (Sort by Start Time)

1. In trace detail view, spans are usually listed in order
2. The **first span** (earliest start time) is usually the root
3. Child spans start later and are indented/nested

---

## Visual Guide: What to Look For

### In Jaeger Trace View:

```
┌─────────────────────────────────────────────────────────────┐
│ Trace Detail View                                            │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│ [ROOT SPAN - CLICK HERE!]                                    │
│ Duration: 1.2s  ← This is END-TO-END latency!               │
│ Operation: POST /api/coach/start                            │
│                                                               │
│ Tags:                                                         │
│   http.method: POST                                          │
│   http.route: /api/coach/start                               │
│   http.status_code: 200                                       │
│                                                               │
│ └─ guard.check_message (15ms)                                │
│ └─ retrieval.retrieve (45ms)                                │
│ └─ model.generate_advice (1100ms)                            │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Timeline View:

```
Timeline (horizontal):
│
│ [════════════════════════════════] 1.2s ← ROOT SPAN
│   ├─[══] guard (15ms)
│   ├─[═══] retrieval (45ms)
│   └─[════════════════════] model (1100ms)
│
```

---

## Quick Checklist

When looking at a trace:

- [ ] Found the **topmost/leftmost span** (no parent)
- [ ] Span has `http.method` tag (POST/GET)
- [ ] Span has `http.route` tag
- [ ] Span contains child spans (guard, retrieval, model)
- [ ] Span duration = total request time

**That's your end-to-end span!**

---

## Example: Finding Root Span

**What you see:**
```
guard.check_message          [15ms]
retrieval.retrieve           [45ms]
model.generate_advice         [1100ms]
```

**What to do:**
1. Look **above** or **around** these spans
2. Find a span that contains all three
3. It might be collapsed/hidden - **expand it!**
4. Check for a span with **longer duration** (like 1.2s)
5. That span duration = 15ms + 45ms + 1100ms = **total end-to-end time**

---

## Common Root Span Names

Depending on how FastAPI instrumentation names them:

**For HTTP:**
- `POST /api/coach/start`
- `/api/coach/start`
- `POST /api/coach/stream`
- `/api/coach/stream`

**For WebSocket:**
- `/ws/coach/{session_id}`
- `GET /ws/coach/{session_id}`
- `WebSocket /ws/coach/{session_id}`

---

## If You Still Can't Find It

**Try this:**

1. **Expand all spans** - Click the "+" or expand icons
2. **Look for the widest bar** in timeline view (longest duration)
3. **Check span start times** - Root span starts earliest
4. **Look at the trace list** - The operation name in the list view is the root span

**The root span duration = your end-to-end latency!** 🎯

---

## Summary

**Child spans:**
- `guard.check_message` ✅ (you see this)
- `retrieval.retrieve` ✅ (you see this)
- `model.generate_advice` ✅ (you see this)

**Root span (what you need):**
- Contains all child spans
- Has `http.method` and `http.route` tags
- Duration = sum of child spans + overhead
- This is your **END-TO-END latency** for SLO checking!

Look for the span that contains these three child spans - that's your root! 🔍

