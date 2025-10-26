@echo off
setlocal ENABLEEXTENSIONS ENABLEDELAYEDEXPANSION

REM Change to this script's directory
cd /d "%~dp0"

REM Activate venv if present
if exist .venv\Scripts\activate.bat (
  call .venv\Scripts\activate.bat
)

REM Pick a Python launcher
set "USE_PY=python"
where %USE_PY% >nul 2>&1
if errorlevel 1 (
  where py >nul 2>&1
  if errorlevel 1 (
    echo Python not found. Install Python 3.9+ or ensure it's on PATH.
    exit /b 1
  ) else (
    set "USE_PY=py -3"
  )
)

REM Run the app, forwarding all args
%USE_PY% hello_agent.py %*

endlocal


