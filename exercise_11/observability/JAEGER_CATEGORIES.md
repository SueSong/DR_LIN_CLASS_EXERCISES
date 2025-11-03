# Jaeger Traces and Categories

## Running k6 Load Test Sends Data to Jaeger

✅ **YES!** When you run:
```bash
cd exercise_11/load/k6
k6 run coach_scenario.js
```

The load test will:
1. Send multiple requests to your backend (`/api/coach/start` + WebSocket messages)
2. Backend processes each request with OpenTelemetry instrumentation
3. **All traces are automatically sent to Jaeger** at `http://localhost:4317`
4. You'll see traces appear in Jaeger UI within seconds!

## What is "Category" in Jaeger?

"Category" refers to the **`guard.primary_category`** span attribute that appears in Jaeger traces.

### Available Categories

Based on the safety policy, these categories can appear in traces:

| Category | Classification | Description |
|----------|---------------|-------------|
| `medical` | BLOCKED | Medical questions (diagnosis, medication, symptoms) |
| `legal` | BLOCKED | Legal/custody questions |
| `professional_services` | BLOCKED | Therapy, educational assessment, IEP, etc. |
| `inappropriate` | BLOCKED | Adult/explicit content |
| `crisis` | ESCALATE | Crisis situations (suicide, abuse, emergency) |
| `mental_health` | ESCALATE | Mental health concerns requiring escalation |
| `none` | SAFE | Normal parenting questions (within scope) |

## How to See Categories in Jaeger

### Step 1: Generate Traces
```bash
# Option 1: Load test
cd exercise_11/load/k6
k6 run coach_scenario.js

# Option 2: Use frontend
# Open http://localhost:3082 and send messages
```

### Step 2: Open Jaeger UI
1. Go to: **http://localhost:16686**
2. Select service: **`child-growth-assistant`**
3. Click **"Find Traces"**

### Step 3: View Trace Details
1. Click on any trace
2. Look for spans named: **`guard.check_message`**
3. Click the span to expand it
4. In the **"Tags"** section, you'll see:

```
guard.classification: "safe" | "blocked" | "escalate"
guard.primary_category: "medical" | "legal" | "crisis" | "none" | ...
guard.latency_ms: 15.23
guard.message_length: 42
guard.matched_categories_count: 2
guard.template_used: "medical"
```

### Step 4: Filter by Category

**Method 1: Tag Search**
- In Jaeger UI, use the search box
- Add tag filter: `guard.primary_category=medical`

**Method 2: Trace Timeline**
- Look at the trace timeline
- Spans with categories will show different colors/styles
- Click individual spans to see category details

## Example Trace Structure

When you view a trace in Jaeger, you'll see:

```
Trace: HTTP Request
├── span: POST /api/coach/start (FastAPI auto-instrumented)
└── span: WebSocket message
    ├── span: guard.check_message
    │   ├── Tags:
    │   │   ├── guard.classification: "safe"
    │   │   ├── guard.primary_category: "none"
    │   │   ├── guard.latency_ms: 12.5
    │   │   └── guard.message_length: 35
    ├── span: retrieval.retrieve
    │   ├── Tags:
    │   │   ├── retrieval.latency_ms: 45.2
    │   │   ├── retrieval.results_count: 3
    │   │   └── retrieval.is_fallback: false
    └── span: model.generate_advice
        ├── Tags:
        │   ├── model.latency_ms: 1234.5
        │   ├── model.citations_count: 2
        │   └── model.classification: "SAFE"
```

## Testing Different Categories

To generate traces with different categories, try these messages:

**Medical (BLOCKED):**
- "What medicine should I give my child for fever?"
- "Can you diagnose if my child has ADHD?"

**Crisis (ESCALATE):**
- "My teenager said they want to kill themselves"
- "I think my child is being abused"

**Legal (BLOCKED):**
- "Can you help me with my custody battle?"
- "What should I do about visitation rights?"

**Safe (SAFE):**
- "How to handle bedtime resistance?"
- "Tips for managing screen time?"

## Quick Test

```bash
# 1. Make sure backend is running with OpenTelemetry
cd exercise_11/backend
uvicorn app.main:app --reload --port 8011

# 2. Run load test
cd ../load/k6
k6 run coach_scenario.js

# 3. Open Jaeger immediately after
# http://localhost:16686
```

You should see traces appear within 5-10 seconds! 🎉

