# How to Find Operation Names in Jaeger

If you don't see `POST /api/coach/start`, here's how to find what operations actually exist:

## Method 1: Check Operation Dropdown (Easiest!)

1. Open Jaeger: **http://localhost:16686**
2. Select service: **`child-growth-assistant`**
3. Look at the **"Operation"** dropdown
4. Click on it to see **ALL available operations**

**Common operation names you might see:**
- `/api/coach/start` (without POST prefix)
- `POST /api/coach/start`
- `GET /api/coach/start` (less likely)
- `/api/coach/stream`
- `POST /api/coach/stream`
- `/ws/coach/{session_id}`
- `GET /ws/coach/{session_id}`
- `/healthz`
- `GET /healthz`

**Try selecting "All Operations" first to see everything!**

---

## Method 2: Check Without Filtering

1. In Jaeger UI:
   - Service: `child-growth-assistant`
   - Operation: **"All Operations"** (or leave blank)
2. Click **"Find Traces"**
3. Look at the traces - the operation name appears in each trace entry

---

## Method 3: Check Trace Tags

1. Find ANY trace (even if operation name is unclear)
2. Click on it
3. Click on the **root span** (top-level span)
4. Look in **Tags** section for:
   - `http.route` - Shows the route path
   - `http.method` - Shows HTTP method (POST, GET, etc.)
   - `http.url` - Shows full URL

**Example Tags:**
```
http.method: POST
http.route: /api/coach/start
http.url: /api/coach/start
```

---

## Method 4: Check What k6 Actually Sends

Looking at `coach_scenario.js`, k6 sends:
1. `GET /healthz` - Health check
2. `POST /api/coach/start` - Start session  
3. WebSocket connection to `/ws/coach/{session_id}`

**So you should see these operations:**
- `GET /healthz` (or just `/healthz`)
- `POST /api/coach/start` (or just `/api/coach/start`)
- WebSocket operation (name may vary)

---

## Common Operation Name Variations

FastAPI OpenTelemetry instrumentation might name operations as:

**Option 1: Full path only**
```
/api/coach/start
/api/coach/stream
/ws/coach/{session_id}
```

**Option 2: Method + Path**
```
POST /api/coach/start
POST /api/coach/stream
GET /ws/coach/{session_id}
```

**Option 3: Just the function name**
```
start_session
stream_advice
coach_ws
```

**Try all of these in the Operation dropdown!**

---

## Quick Checklist

- [ ] Opened Jaeger UI
- [ ] Selected service: `child-growth-assistant`
- [ ] Operation dropdown shows options
- [ ] Tried "All Operations" to see everything
- [ ] Looked at actual trace list for operation names
- [ ] Checked a trace's Tags section for `http.route`

---

## If You Still Don't See Anything

**Possible reasons:**
1. **No traces generated yet**
   - Run k6 test: `cd exercise_11\load\k6 && k6 run coach_scenario.js`
   - Or use frontend to send some messages
   - Wait 10-30 seconds for traces to appear

2. **Time range too narrow**
   - Set time range to "Last 1 hour" or "Last 24 hours"
   - Or manually set to include when you ran the test

3. **Traces going to different service**
   - Check if service name is exactly `child-growth-assistant`
   - Try searching with empty service filter

4. **Jaeger not receiving traces**
   - Check backend logs for "OTLP exporter configured"
   - Verify Jaeger is running: `docker ps | grep jaeger`
   - Check backend is actually making requests

---

## Alternative: Look for ANY HTTP Spans

Instead of specific operation, look for:
- Spans with `http.method` tag → These are HTTP requests
- Spans with `http.route` tag → These show the route
- Top-level spans (no parent) → These are end-to-end

**Steps:**
1. Open any trace
2. Find spans with `http.method=POST` or `http.method=GET` in Tags
3. Check `http.route` tag to see the endpoint
4. That span's duration = end-to-end latency

---

## Next Steps

1. **Try "All Operations" first** - See what's actually there
2. **Check any trace** - Look at Tags to find operation info
3. **Generate new traces** - Run k6 or use frontend
4. **Wait and refresh** - Traces may take a few seconds to appear

Tell me what you see in the Operation dropdown or in trace Tags, and I'll help you identify the right operation! 🔍

