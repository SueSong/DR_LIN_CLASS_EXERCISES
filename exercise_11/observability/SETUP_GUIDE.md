# Observability Setup Guide

## Prerequisites
✅ Your Docker Jaeger and Grafana are running

## Verify Jaeger Connection

1. **Check Jaeger OTLP Endpoint**
   - Jaeger typically listens on port `4317` for OTLP gRPC
   - Default endpoint: `http://localhost:4317`

2. **Set Environment Variable (Optional)**
   ```bash
   # If your Jaeger is on a different endpoint, set this:
   export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
   ```

3. **Start Backend Server**
   ```bash
   cd exercise_11/backend
   pip install -r requirements.txt
   uvicorn app.main:app --reload --port 8011
   ```

4. **Check Logs**
   When the backend starts, you should see:
   ```
   INFO: OTLP exporter configured: http://localhost:4317
   INFO: FastAPI instrumentation enabled
   INFO: OpenTelemetry observability initialized successfully
   ```

5. **Generate Some Traffic**
   - Use the frontend to send a few messages
   - Or run a load test:
     ```bash
     cd exercise_11/load/k6
     k6 run coach_scenario.js
     ```

6. **View Traces in Jaeger**
   - Open browser: http://localhost:16686
   - Select service: `child-growth-assistant`
   - Click "Find Traces"
   - You should see spans for:
     - `guard.check_message` - Safety guard checks
     - `retrieval.retrieve` - RAG retrieval operations  
     - `model.generate_advice` or `model.generate_advice_stream` - Advice generation

## Import Dashboards to Grafana

The dashboard JSON files are in `exercise_11/observability/dashboards/`:

1. **Login to Grafana**
   - Available at: http://localhost:3001
   - Username: `admin`
   - Password: `636492`

2. **Configure Jaeger Data Source**
   - Go to: Configuration → Data Sources → Add data source
   - Select "Jaeger"
   - URL: `http://localhost:16686`
   - Click "Save & Test"
   
   **Note:** Grafana is available at http://localhost:3001 (not 3000)

3. **Import Dashboards**
   - Go to: Dashboards → Import
   - Upload JSON files:
     - `latency_dashboard.json`
     - `classification_dashboard.json`
     - `performance_dashboard.json`
   - Or copy-paste the JSON content

4. **Manual Dashboard Creation**
   If import doesn't work, create panels manually using these queries:

   **Latency Queries:**
   - `guard.latency_ms` - Guard operation latency
   - `retrieval.latency_ms` - RAG retrieval latency
   - `model.latency_ms` - Model generation latency

   **Classification Metrics:**
   - `guard.classification` - Safety classifications (SAFE, BLOCKED, ESCALATE)
   - `model.classification` - Model response types
   - `retrieval.is_fallback` - Whether fallback entries were used

   **Performance Metrics:**
   - `http.server.duration` - End-to-end request latency (p95 should be < 2.5s)
   - Error rate should be < 1%

## Span Attributes to Query

When viewing traces in Jaeger, you'll see these attributes:

**Guard Spans:**
- `guard.message_length` - Length of user message
- `guard.classification` - SAFE, BLOCKED, or ESCALATE
- `guard.latency_ms` - Processing time
- `guard.primary_category` - Category that triggered classification
- `guard.matched_categories_count` - Number of categories matched

**Retrieval Spans:**
- `retrieval.query_length` - Query length
- `retrieval.latency_ms` - Retrieval time
- `retrieval.results_count` - Number of results
- `retrieval.top_relevance_score` - Relevance score of top result
- `retrieval.is_fallback` - Whether fallback was used

**Model Spans:**
- `model.user_text_length` - User input length
- `model.session_id` - Session identifier
- `model.latency_ms` - Total generation time
- `model.advice_length` - Length of generated advice
- `model.citations_count` - Number of citations
- `model.has_citations` - Whether citations are present
- `model.relevance_score` - Top relevance score
- `model.classification` - Response classification

## Troubleshooting

**No traces in Jaeger?**
1. Check backend logs for OTLP connection errors
2. Verify Jaeger is running: `docker ps | grep jaeger`
3. Check port 4317 is accessible: `telnet localhost 4317`
4. Try setting explicit endpoint in `main.py`:
   ```python
   setup_observability(
       jaeger_endpoint="http://localhost:4317"
   )
   ```

**Spans not showing attributes?**
- Ensure spans are created within the `with tracer.start_as_current_span()` context
- Check span.set_attribute() calls are executed before span ends

**Dashboard not showing data?**
- Verify Grafana can connect to Jaeger data source
- Check time range in Grafana (use "Last 5 minutes")
- Ensure traffic is being generated (send messages or run load tests)

