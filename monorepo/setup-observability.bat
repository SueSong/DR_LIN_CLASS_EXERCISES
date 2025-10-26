@echo off
REM AI Agent Training - Observability Setup Script (Windows)
REM Sets up Jaeger, Prometheus, and Grafana for OpenTelemetry demo

setlocal enabledelayedexpansion

echo 🎯 AI Agent Training - Observability Setup
echo ==========================================

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)

echo ✅ Docker is running

REM Check if Docker Compose is available
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ docker-compose is not installed. Please install Docker Compose.
    pause
    exit /b 1
)

echo ✅ Docker Compose is available

REM Pull required images
echo 📦 Pulling Docker images...
docker-compose pull
if %errorlevel% neq 0 (
    echo ❌ Failed to pull Docker images
    pause
    exit /b 1
)

REM Start observability stack
echo 🚀 Starting observability stack...
docker-compose up -d
if %errorlevel% neq 0 (
    echo ❌ Failed to start observability stack
    pause
    exit /b 1
)

REM Wait for services to be ready
echo ⏳ Waiting for services to start...
timeout /t 10 /nobreak >nul

REM Check service health
echo 🔍 Checking service health...

REM Check Jaeger
curl -s http://localhost:16686 >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Jaeger UI is ready at http://localhost:16686
) else (
    echo ⚠️  Jaeger UI might still be starting...
)

REM Check Prometheus
curl -s http://localhost:9090 >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Prometheus is ready at http://localhost:9090
) else (
    echo ⚠️  Prometheus might still be starting...
)

REM Check Grafana
curl -s http://localhost:3001 >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Grafana is ready at http://localhost:3001 ^(admin/admin^)
) else (
    echo ⚠️  Grafana might still be starting...
)

REM Check OpenTelemetry Collector
curl -s http://localhost:4318/v1/traces >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ OpenTelemetry Collector is ready
) else (
    echo ⚠️  OpenTelemetry Collector might still be starting...
)

echo.
echo 🎉 Observability stack is starting up!
echo.
echo 📊 Access URLs:
echo   • Jaeger UI ^(Traces^):     http://localhost:16686
echo   • Grafana ^(Metrics^):     http://localhost:3001 ^(admin/admin^)
echo   • Prometheus:            http://localhost:9090
echo   • OTEL Collector:        http://localhost:4317 ^(gRPC^), http://localhost:4318 ^(HTTP^)
echo.
echo 🚀 Next steps:
echo   1. Start Trading Agent: npm run start:trading
echo   2. Start Original API: npm run start:api
echo   3. Run demo traces: python demo_traces.py
echo   4. View traces in Jaeger UI
echo.
echo 🛑 To stop: docker-compose down
echo.
echo Press any key to continue...
pause >nul


