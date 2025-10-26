@echo off
REM Setup dependencies for Original API Server (Exercise 1-4)
REM Fixes missing OpenTelemetry dependencies

setlocal enabledelayedexpansion

echo 🔧 Setting up Original API Dependencies
echo =======================================

REM Change to API directory
cd /d "%~dp0apps\api"
if %errorlevel% neq 0 (
    echo ❌ Failed to navigate to apps\api directory
    pause
    exit /b 1
)

echo 📍 Current directory: %cd%

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

REM Install/upgrade dependencies
echo 📦 Installing dependencies...
pip install --upgrade pip

REM Install core dependencies
pip install fastapi uvicorn pydantic httpx

REM Install OpenTelemetry dependencies
echo 📊 Installing OpenTelemetry dependencies...
pip install opentelemetry-api
pip install opentelemetry-sdk
pip install opentelemetry-exporter-otlp
pip install opentelemetry-instrumentation-fastapi
pip install opentelemetry-instrumentation-httpx
pip install opentelemetry-instrumentation-requests

REM Install additional dependencies from requirements.txt if it exists
if exist "requirements.txt" (
    echo 📋 Installing from requirements.txt...
    pip install -r requirements.txt
)

echo ✅ Dependencies installed successfully!
echo.
echo 🚀 You can now start the Original API server with:
echo    python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
echo.
pause


