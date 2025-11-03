@echo off
REM Exercise 11 - Child Growth Assistant Startup Script (Windows)

echo ============================================
echo Starting Exercise 11 - Child Growth Assistant
echo ============================================
echo.

REM Get script directory
set SCRIPT_DIR=%~dp0
cd /d %SCRIPT_DIR%

echo [1/4] Starting Backend Server...
cd backend

REM Check if venv exists
if not exist "venv\" (
    echo Creating Python virtual environment...
    python -m venv venv
)

REM Activate venv and install dependencies
call venv\Scripts\activate.bat
pip install -q -r requirements.txt

echo Backend dependencies installed
echo.

REM Start backend in new window
start "Backend Server" cmd /k "cd /d %SCRIPT_DIR%backend && venv\Scripts\activate.bat && uvicorn app.main:app --host 0.0.0.0 --port 8011 --reload"

echo [2/4] Backend started on http://localhost:8011
timeout /t 3 /nobreak >nul
echo.

echo [3/4] Starting Frontend Server...
cd %SCRIPT_DIR%frontend

REM Check if node_modules exists
if not exist "node_modules\" (
    echo Installing Node.js dependencies...
    call npm install
)

echo Frontend dependencies installed
echo.

REM Start frontend in new window
start "Frontend Server" cmd /k "cd /d %SCRIPT_DIR%frontend && set PORT=3082 && npm run dev"

echo [4/4] Frontend started on http://localhost:3082
echo.

echo ============================================
echo All servers are running!
echo ============================================
echo.
echo Open your browser: http://localhost:3082
echo Backend API: http://localhost:8011/docs
echo.
echo Press any key to close this window...
echo (Servers will keep running in separate windows)
pause >nul

