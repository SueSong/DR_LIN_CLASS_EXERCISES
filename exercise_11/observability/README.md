# Observability

This directory contains OpenTelemetry observability setup and dashboard configurations for the Child Growth Assistant.

## Structure

- `observability.py` - OpenTelemetry setup module (in `backend/app/observability.py`)
- `dashboards/` - JSON dashboard configurations for monitoring tools

## OpenTelemetry Spans

The system tracks three main operation types:

### 1. Guard Spans (`guard.check_message`)
- **Purpose**: Track safety guard checks
- **Attributes**:
  - `guard.message_length`: Length of user message
  - `guard.classification`: SAFE, BLOCKED, or ESCALATE
  - `guard.latency_ms`: Processing time in milliseconds
  - `guard.primary_category`: Category that triggered classification
  - `guard.matched_categories_count`: Number of categories matched
  - `guard.template_used`: Template used for refusal messages

### 2. Retrieval Spans (`retrieval.retrieve`)
- **Purpose**: Track RAG knowledge base retrieval
- **Attributes**:
  - `retrieval.query_length`: Length of user query
  - `retrieval.max_results`: Maximum results requested
  - `retrieval.latency_ms`: Retrieval time in milliseconds
  - `retrieval.results_count`: Number of results returned
  - `retrieval.top_relevance_score`: Relevance score of top result
  - `retrieval.is_fallback`: Whether fallback entry was used

### 3. Model Spans (`model.generate_advice` / `model.generate_advice_stream`)
- **Purpose**: Track advice generation and streaming
- **Attributes**:
  - `model.user_text_length`: Length of user input
  - `model.session_id`: Session identifier
  - `model.streaming`: Whether streaming mode (SSE)
  - `model.latency_ms`: Total generation time
  - `model.advice_length`: Length of generated advice
  - `model.citations_count`: Number of citations included
  - `model.has_citations`: Whether citations are present
  - `model.relevance_score`: Top relevance score from RAG
  - `model.classification`: Response classification (SAFE, BLOCKED, ESCALATE, SAFE_FALLBACK)

## Setup

Observability is automatically initialized when the FastAPI app starts. To configure:

1. **Console Export** (default: enabled)
   - Spans are logged to console for development

2. **Jaeger Export** (optional)
   - Set `OTEL_EXPORTER_OTLP_ENDPOINT` environment variable
   - Default: `http://localhost:4317`
   - Requires Jaeger collector running

## Dashboards

Three dashboard configurations are provided:

1. **latency_dashboard.json** - Monitor latency for all operations
2. **classification_dashboard.json** - Monitor safety classifications and model responses
3. **performance_dashboard.json** - Monitor SLO compliance (p95 < 2.5s, error rate < 1%)

These can be imported into monitoring tools like:
- Grafana
- Jaeger UI
- Datadog
- New Relic
- Any OpenTelemetry-compatible tool

## SLO Targets

- **P95 Latency**: ≤ 2.5 seconds
- **Error Rate**: ≤ 1%

## Usage

The observability system runs automatically. To view spans:

1. **Console**: Check backend logs for span output
2. **Jaeger**: Navigate to http://localhost:16686 (if Jaeger is running)
3. **Custom Tool**: Import dashboard JSON files into your monitoring tool

## Testing

Run load tests to generate spans:
```bash
# k6 load test
cd load/k6
k6 run coach_scenario.js

# Locust load test
cd load/locust
locust -f locustfile.py
```

Span data will be collected during the load test, showing latency and classification distributions.

