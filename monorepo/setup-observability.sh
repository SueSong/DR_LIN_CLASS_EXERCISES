#!/bin/bash

# AI Agent Training - Observability Setup Script
# Sets up Jaeger, Prometheus, and Grafana for OpenTelemetry demo

set -e

echo "🎯 AI Agent Training - Observability Setup"
echo "=========================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

echo "✅ Docker is running"

# Check if Docker Compose is available
if ! command -v docker-compose > /dev/null 2>&1; then
    echo "❌ docker-compose is not installed. Please install Docker Compose."
    exit 1
fi

echo "✅ Docker Compose is available"

# Pull required images
echo "📦 Pulling Docker images..."
docker-compose pull

# Start observability stack
echo "🚀 Starting observability stack..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check service health
echo "🔍 Checking service health..."

# Check Jaeger
if curl -s http://localhost:16686 > /dev/null; then
    echo "✅ Jaeger UI is ready at http://localhost:16686"
else
    echo "⚠️  Jaeger UI might still be starting..."
fi

# Check Prometheus
if curl -s http://localhost:9090 > /dev/null; then
    echo "✅ Prometheus is ready at http://localhost:9090"
else
    echo "⚠️  Prometheus might still be starting..."
fi

# Check Grafana
if curl -s http://localhost:3001 > /dev/null; then
    echo "✅ Grafana is ready at http://localhost:3001 (admin/admin)"
else
    echo "⚠️  Grafana might still be starting..."
fi

# Check OpenTelemetry Collector
if curl -s http://localhost:4318/v1/traces > /dev/null 2>&1; then
    echo "✅ OpenTelemetry Collector is ready"
else
    echo "⚠️  OpenTelemetry Collector might still be starting..."
fi

echo ""
echo "🎉 Observability stack is starting up!"
echo ""
echo "📊 Access URLs:"
echo "  • Jaeger UI (Traces):     http://localhost:16686"
echo "  • Grafana (Metrics):     http://localhost:3001 (admin/admin)"
echo "  • Prometheus:            http://localhost:9090"
echo "  • OTEL Collector:        http://localhost:4317 (gRPC), http://localhost:4318 (HTTP)"
echo ""
echo "🚀 Next steps:"
echo "  1. Start your API: cd apps/api && ./run.sh"
echo "  2. Run demo traces: python demo_traces.py"
echo "  3. View traces in Jaeger UI"
echo ""
echo "🛑 To stop: docker-compose down"
