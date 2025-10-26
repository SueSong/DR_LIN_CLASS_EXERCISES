@echo off
REM Complete Server Startup Script for Exercise 5 (Windows)
REM Starts all servers in the correct order with proper error handling

setlocal enabledelayedexpansion

title AI Agent Training - Exercise 5 Server Startup

echo 🚀 Complete Server Startup Commands for Exercise 5
echo =====================================================
echo.

REM Check prerequisites
echo 📋 Prerequisites Check
echo =====================

REM Check if we're in the monorepo directory
if not exist "package.json" (
    echo ❌ Not in monorepo directory. Please run this from the monorepo root.
    echo Current directory: %cd%
    echo Expected files: package.json, docker-compose.yml
    pause
    exit /b 1
)

echo ✅ In monorepo directory: %cd%

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running. Starting Docker Desktop...
    start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    echo ⏳ Waiting for Docker to start (30 seconds)...
    timeout /t 30 /nobreak >nul
    
    REM Check again
    docker info >nul 2>&1
    if %errorlevel% neq 0 (
        echo ❌ Docker failed to start. Please start Docker Desktop manually.
        pause
        exit /b 1
    )
)

echo ✅ Docker is running

REM Check if Node.js is available
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js is not installed. Please install Node.js first.
    pause
    exit /b 1
)

echo ✅ Node.js is available

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed. Please install Python first.
    pause
    exit /b 1
)

echo ✅ Python is available
echo.

REM Step 1: Stop any existing servers
echo 🛑 Stopping any existing servers...
echo ===================================

REM Kill processes on our target ports
for %%p in (8000 8001 3000 16686 9090 5432 6379) do (
    for /f "tokens=5" %%a in ('netstat -aon ^| findstr :%%p') do (
        taskkill /f /pid %%a >nul 2>&1
    )
)

REM Stop docker-compose services
docker-compose down >nul 2>&1

echo ✅ Existing servers stopped
echo.

REM Step 2: Start Observability Stack
echo 🔭 1. Starting Observability Stack (Jaeger, Prometheus, Grafana)
echo ================================================================

call setup-observability.bat
if %errorlevel% neq 0 (
    echo ❌ Failed to start observability stack
    echo ⚠️  Continuing without observability...
    set OBSERVABILITY_FAILED=1
) else (
    echo ✅ Observability stack started successfully
    set OBSERVABILITY_FAILED=0
)

echo.
echo ⏳ Waiting 10 seconds for observability services to stabilize...
timeout /t 10 /nobreak >nul
echo.

REM Step 3: Start Trading Agent Server
echo 🎯 2. Starting Trading Agent Server (Exercise 5)
echo ===============================================

echo Starting Trading Agent in new window...
start "Trading Agent Server" /d "%cd%" start-trading.bat

REM Wait and check if trading agent started
echo ⏳ Waiting for Trading Agent to start...
timeout /t 15 /nobreak >nul

curl -s http://localhost:8001/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Trading Agent is running at http://localhost:8001
) else (
    echo ⚠️  Trading Agent might still be starting...
)

echo.

REM Step 4: Start Original API Server (Optional)
echo 🔧 3. Starting Original API Server (Exercise 1-4) - Optional
echo ===========================================================

set /p START_API="Start Original API Server? (y/n): "
if /i "!START_API!"=="y" (
    echo Starting Original API in new window...
    start "Original API Server" /d "%cd%\apps\api" cmd /k "python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload"
    
    echo ⏳ Waiting for Original API to start...
    timeout /t 10 /nobreak >nul
    
    curl -s http://localhost:8000/health >nul 2>&1
    if %errorlevel% equ 0 (
        echo ✅ Original API is running at http://localhost:8000
    ) else (
        echo ⚠️  Original API might still be starting...
    )
) else (
    echo ⏭️  Skipping Original API Server
)

echo.

REM Step 5: Display Access Information
echo 🎮 Server Access Information
echo ============================

echo.
echo 🎯 Main Services:
echo   • Trading Agent Chat UI:    http://localhost:8001
echo   • Trading Agent API Docs:   http://localhost:8001/docs
echo   • Trading Agent Health:     http://localhost:8001/health

if "!START_API!"=="y" (
    echo   • Original API Docs:        http://localhost:8000/docs
    echo   • Original API Health:      http://localhost:8000/health
)

if !OBSERVABILITY_FAILED! equ 0 (
    echo.
    echo 📊 Observability Services:
    echo   • Jaeger Tracing UI:        http://localhost:16686
    echo   • Prometheus Metrics:       http://localhost:9090
    echo   • Grafana Dashboards:       http://localhost:3001 ^(admin/admin^)
)

echo.
echo 🧪 Quick Test Commands:
echo   • Test Trading Agent:       curl http://localhost:8001/health
echo   • Get Stock Quote:          curl -X POST http://localhost:8001/quotes -H "Content-Type: application/json" -d "{\"symbols\":[\"AAPL\"],\"user_id\":\"test\"}"
echo   • Execute Trade:            curl -X POST http://localhost:8001/trades -H "Content-Type: application/json" -d "{\"symbol\":\"AAPL\",\"action\":\"BUY\",\"amount\":1000,\"user_id\":\"test\"}"

echo.
echo 🎉 Exercise 5 Setup Complete!
echo ==============================
echo.
echo 🚀 Ready to demo:
echo   1. Open http://localhost:8001 for the Trading Agent Chat UI
echo   2. Try stock quotes, trading, and AI recommendations
if !OBSERVABILITY_FAILED! equ 0 (
    echo   3. View traces at http://localhost:16686 ^(search for "trading-agent" service^)
)
echo   4. All 6 exercises are implemented and ready for demonstration

echo.
echo 🛑 To stop all servers:
echo   • Close this window and the server windows
echo   • Or run: docker-compose down

echo.
echo Press any key to open the Trading Agent Chat UI...
pause >nul

REM Open the main interface
start http://localhost:8001

echo.
echo 🎯 Trading Agent Chat UI opened in your browser!
echo Keep this window open to monitor server status.
echo.
pause


