# How to View Dashboard Charts in Grafana

## Important Note
The current dashboard JSON files are in a simplified format. To see actual charts with data, you have two options:

### Option 1: View Traces in Jaeger (Works Immediately! ✅)

Since OpenTelemetry is currently exporting **traces** to Jaeger (not metrics), you can view latency information directly in Jaeger:

1. **Open Jaeger UI**: http://localhost:16686
2. **Select Service**: Choose `child-growth-assistant` from the dropdown
3. **Click "Find Traces"**
4. **View Trace Details**: Click on any trace to see:
   - Individual span latencies
   - Span attributes (e.g., `guard.latency_ms`, `retrieval.latency_ms`, `model.latency_ms`)
   - Trace timeline visualization

**To generate traces:**
- Send messages through the frontend (http://localhost:3082)
- Or run a load test to generate multiple traces

---

### Option 2: View Dashboard in Grafana (Needs Configuration)

If you've imported the dashboard, here's how to view it:

#### Step 1: Navigate to Your Dashboard

1. **Login to Grafana**: http://localhost:3001
   - Username: `admin`
   - Password: `636492`

2. **Go to Dashboards**:
   - Click the **☰ menu** (hamburger icon) in the top-left
   - Select **"Dashboards"** → **"Browse"**

3. **Find Your Dashboard**:
   - Look for "Child Growth Assistant - Latency Dashboard"
   - Click on it to open

#### Step 2: Check Data Source Configuration

The dashboard needs a data source to query metrics. Currently, we're only exporting **traces** (to Jaeger), not **metrics**.

**Option A: Use Jaeger Data Source (View Traces)**
1. Go to **Configuration** → **Data Sources** → **Add data source**
2. Select **"Jaeger"**
3. URL: `http://jaeger:16686` (or `http://localhost:16686`)
4. Click **"Save & Test"**

**Option B: Set Up Metrics Export (For Charts)**

To see latency charts, we need to export metrics. This requires additional setup:

1. **Add Prometheus** to docker-compose.yml
2. **Configure OpenTelemetry** to export metrics to Prometheus
3. **Configure Grafana** to use Prometheus as data source

---

## Quick Test: View Traces in Jaeger

1. **Generate some traffic**:
   ```bash
   # Option 1: Use frontend
   # Open http://localhost:3082 and send a few messages
   
   # Option 2: Run a load test
   cd exercise_11/load/k6
   k6 run coach_scenario.js
   ```

2. **Open Jaeger**: http://localhost:16686

3. **View traces**:
   - Service: `child-growth-assistant`
   - Click "Find Traces"
   - Click any trace to see detailed span information
   - Look at span attributes for `guard.latency_ms`, `retrieval.latency_ms`, `model.latency_ms`

---

## Current Status

✅ **Working Now:**
- Traces are being sent to Jaeger
- You can view detailed trace information in Jaeger UI
- Span attributes contain latency information

⚠️ **Needs Setup:**
- Metrics export (for Grafana charts)
- Proper Grafana dashboard JSON format
- Prometheus or metrics backend configuration

---

## Next Steps

If you want to see charts in Grafana:

1. **For now**: Use Jaeger UI (http://localhost:16686) to view traces and latency
2. **For charts**: We can set up metrics export to Prometheus, then create proper Grafana dashboards

Would you like me to:
- Set up Prometheus and metrics export?
- Create proper Grafana dashboard JSON files?
- Or stick with Jaeger for now (it works great for viewing traces!)?

