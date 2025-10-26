@echo off
REM AI Trading Agent Startup Script (Windows)
REM Starts the Exercise 5 Trading Agent with proper environment setup

setlocal enabledelayedexpansion

echo 🚀 Starting AI Trading Agent...

REM Change to trading agent directory
cd /d "%~dp0apps\trading-agent"
if %errorlevel% neq 0 (
    echo ❌ Failed to navigate to trading-agent directory
    pause
    exit /b 1
)

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo ✅ Virtual environment found
) else (
    echo 📦 Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ❌ Failed to activate virtual environment
    pause
    exit /b 1
)

REM Install dependencies if needed
echo 📚 Checking dependencies...
pip show fastapi >nul 2>&1
if %errorlevel% neq 0 (
    echo 📦 Installing dependencies...
    pip install --upgrade pip
    pip install -r requirements_simple.txt
    pip install jinja2
    if %errorlevel% neq 0 (
        echo ❌ Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Set environment variables
set DATABASE_URL=postgresql://trader:trading123@localhost:5432/trading_db
set OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
set OTEL_SERVICE_NAME=trading-agent

echo 🌐 Starting server on http://localhost:8001
echo 💬 Chat UI will be available at: http://localhost:8001/
echo 📚 API docs available at: http://localhost:8001/docs
echo Press Ctrl+C to stop the server

REM Start the server
python -m uvicorn app:app --host 0.0.0.0 --port 8001 --reload

REM Cleanup on exit
echo.
echo 🛑 Server stopped
pause


