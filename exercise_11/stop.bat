@echo off
REM Exercise 11 - Stop All Servers Script (Windows)

echo ============================================
echo Stopping Exercise 11 servers...
echo ============================================
echo.

REM Kill processes on port 8011 (backend)
echo Checking backend (port 8011)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8011 ^| findstr LISTENING') do (
    echo Stopping backend process (PID: %%a)
    taskkill /PID %%a /F >nul 2>&1
)

REM Kill processes on port 3082 (frontend)
echo Checking frontend (port 3082)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3082 ^| findstr LISTENING') do (
    echo Stopping frontend process (PID: %%a)
    taskkill /PID %%a /F >nul 2>&1
)

REM Also kill any command windows with "Backend Server" or "Frontend Server" in title
tasklist /FI "WINDOWTITLE eq Backend Server*" /NH 2>nul | find /I "cmd.exe" >nul && (
    echo Closing backend window...
    taskkill /FI "WINDOWTITLE eq Backend Server*" /F >nul 2>&1
)

tasklist /FI "WINDOWTITLE eq Frontend Server*" /NH 2>nul | find /I "cmd.exe" >nul && (
    echo Closing frontend window...
    taskkill /FI "WINDOWTITLE eq Frontend Server*" /F >nul 2>&1
)

echo.
echo ============================================
echo All servers stopped!
echo ============================================
echo.
echo To start again, run: start.bat
echo.
pause

