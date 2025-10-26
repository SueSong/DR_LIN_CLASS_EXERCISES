# 🔍 OpenTelemetry Observability Demo

This guide shows you how to set up and run a comprehensive OpenTelemetry demo with visual tracing for your AI Agent Training project.

## 🎯 What You'll Get

- **Jaeger UI** - Beautiful trace visualization showing AI agent execution flows
- **Grafana** - Metrics dashboards for performance monitoring  
- **Prometheus** - Metrics collection and storage
- **OpenTelemetry Collector** - Centralized telemetry data processing

## 🚀 Quick Start

### 1. Prerequisites

Make sure you have installed:
- **Docker** and **Docker Compose**
- **Python 3.9+** with `httpx` library

```bash
# Install httpx for the demo script
pip install httpx
```

### 2. Start Observability Stack

```bash
# Start Jaeger, Prometheus, Grafana, and OTEL Collector
npm run observability:start

# Or manually:
./setup-observability.sh
```

This will start:
- **Jaeger UI**: http://localhost:16686
- **Grafana**: http://localhost:3001 (admin/admin)
- **Prometheus**: http://localhost:9090
- **OTEL Collector**: localhost:4317 (gRPC), localhost:4318 (HTTP)

### 3. Start Your API

```bash
cd apps/api
./run.sh
```

### 4. Generate Demo Traces

```bash
# Run basic demo scenarios
npm run demo

# Run with concurrent operations
npm run demo:concurrent

# Run multiple times for more data
npm run demo:repeat
```

## 📊 Demo Scenarios

The demo script includes several realistic AI agent scenarios:

### 1. Data Processing Pipeline
- Fetches data from external API
- Queries database for user information  
- Writes processed data to file
- Reads back the processed data

### 2. Web Scraping Agent
- Scrapes JSON data from web service
- Creates directory structure
- Stores scraped data
- Queries database for statistics

### 3. Error Handling Demo
- Demonstrates retry behavior on HTTP 500 errors
- Shows database query failures
- File operation errors
- Recovery with successful operations

### 4. Concurrent Operations
- Multiple HTTP requests with different delays
- Parallel database queries
- Concurrent file operations

## 🎨 What to Look For in Jaeger

### Trace Features
- **Service Map**: Visual representation of service dependencies
- **Trace Timeline**: Detailed timing of each operation
- **Span Details**: Tool-specific attributes like:
  - `tool.name` - Which tool was executed
  - `retries` - Number of retry attempts
  - `latency_ms` - Operation duration
  - `status` - Success/error status
  - `http.url`, `db.statement`, `file.operation` - Tool-specific data

### Interesting Traces to Find
1. **Successful Pipeline**: Complete data processing flow
2. **Retry Behavior**: HTTP requests with multiple attempts
3. **Error Propagation**: How errors flow through the system
4. **Concurrent Operations**: Parallel execution patterns

## 🔧 Advanced Usage

### Custom Demo Scenarios

```bash
# Run specific scenarios only
python demo_traces.py --scenarios "Data Processing Pipeline" "Error Handling Demo"

# Run with custom API URL
python demo_traces.py --api-url http://your-api:8000

# Repeat demo multiple times
python demo_traces.py --repeat 5
```

### Monitoring Commands

```bash
# View logs from all observability services
npm run observability:logs

# Stop observability stack
npm run observability:stop

# Restart everything
npm run observability:stop && npm run observability:start
```

## 📈 Grafana Dashboards

Access Grafana at http://localhost:3001 (admin/admin)

### Pre-configured Data Sources
- **Prometheus** - For metrics visualization
- **Jaeger** - For trace correlation

### Metrics to Explore
- Tool execution rates
- Success/error ratios
- Response time distributions
- Retry attempt frequencies

## 🎯 Demo Presentation Tips

### For Exercise 4 Presentation

1. **Start with Service Map**
   - Show how AI agents interact with different tools
   - Highlight service dependencies

2. **Drill into Specific Traces**
   - Pick a complex data processing pipeline
   - Show the complete request flow
   - Highlight timing and dependencies

3. **Demonstrate Error Handling**
   - Show retry behavior in action
   - Explain how errors are tracked and recovered

4. **Show Real-time Monitoring**
   - Generate traces while presenting
   - Show live updates in Jaeger UI

5. **Metrics Correlation**
   - Switch to Grafana to show metrics
   - Correlate high-level metrics with detailed traces

## 🔍 Troubleshooting

### API Not Connecting to Jaeger
```bash
# Check if collector is running
curl http://localhost:4318/v1/traces

# Check API logs for OTLP export errors
cd apps/api && tail -f *.log
```

### No Traces Appearing
1. Ensure API is running with observability enabled
2. Check that demo script can reach the API
3. Verify OTEL Collector is receiving data
4. Check Jaeger UI service dropdown

### Performance Issues
```bash
# Reduce trace sampling for high-volume demos
export OTEL_TRACES_SAMPLER=traceidratio
export OTEL_TRACES_SAMPLER_ARG=0.1  # 10% sampling
```

## 🎉 Demo Script Examples

### Generate Realistic Load
```bash
# Simulate realistic AI agent workload
for i in {1..10}; do
  python demo_traces.py --concurrent &
  sleep 2
done
wait
```

### Error Rate Testing
```bash
# Focus on error scenarios
python demo_traces.py --scenarios "Error Handling Demo" --repeat 5
```

### Performance Testing
```bash
# High-frequency operations
python demo_traces.py --concurrent --repeat 10
```

## 📚 Learning Objectives

This demo demonstrates:

1. **Distributed Tracing** - How requests flow through multiple services
2. **Observability Best Practices** - Proper instrumentation and data collection
3. **Error Tracking** - How failures are captured and analyzed
4. **Performance Monitoring** - Identifying bottlenecks and optimization opportunities
5. **Tool Integration** - How different tools contribute to overall system behavior

## 🔮 Next Steps

- Add custom metrics to your tools
- Create Grafana dashboards for your specific use cases
- Implement alerting based on trace data
- Explore advanced Jaeger features like trace comparison
- Set up log correlation with traces

---

**Happy Tracing!** 🚀✨
