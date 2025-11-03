@echo off
REM Exercise 11 - Test Script
REM Verifies that all components are working correctly

setlocal enabledelayedexpansion

echo.
echo 🧪 Testing Exercise 11 - Child Growth Assistant
echo ================================================
echo.

set FAILED=0
goto :main

REM Test function
:test_endpoint
setlocal enabledelayedexpansion
set "name=%~1"
set "url=%~2"
set "expected=%~3"

echo|set /p="Testing !name!... "

set response=
for /f "delims=" %%i in ('curl -s "!url!" 2^>^&1') do (
    if not defined response (set response=%%i) else (set response=!response! %%i)
)
if "!response!"=="" set response=FAILED

echo !response! | findstr /C:"!expected!" >nul
if !errorlevel! equ 0 (
    echo ✅ PASSED
    endlocal
    exit /b 0
) else (
    echo ❌ FAILED
    echo   Expected: !expected!
    echo   Got: !response!
    endlocal
    exit /b 1
)

:main
echo 🔍 Backend Tests
echo ----------------

REM Test 1: Backend Health
call :test_endpoint "Backend Health" "http://localhost:8011/healthz" "healthy"
if errorlevel 1 set /a FAILED+=1

REM Test 2: Backend Ready
call :test_endpoint "Backend Ready" "http://localhost:8011/readyz" "ready"
if errorlevel 1 set /a FAILED+=1

REM Test 3: Backend CORS
echo|set /p="Testing Backend CORS... "
set cors_response=
for /f "delims=" %%i in ('curl -s -H "Origin: http://localhost:3082" -H "Access-Control-Request-Method: POST" -X OPTIONS http://localhost:8011/api/coach/start -i 2^>^&1') do (
    if not defined cors_response (set cors_response=%%i) else (set cors_response=!cors_response! %%i)
)
echo !cors_response! | findstr /C:"access-control-allow-origin" >nul
if !errorlevel! equ 0 (
    echo ✅ PASSED
) else (
    echo ❌ FAILED
    set /a FAILED+=1
)

REM Test 4: Coach API Endpoint
echo|set /p="Testing Coach Start API... "
set coach_response=
for /f "delims=" %%i in ('curl -s -X POST http://localhost:8011/api/coach/start -H "Content-Type: application/json" -d "{\"parent_name\":\"Test Parent\"}" 2^>^&1') do (
    if not defined coach_response (set coach_response=%%i) else (set coach_response=!coach_response! %%i)
)
echo !coach_response! | findstr /C:"session_id" >nul
if !errorlevel! equ 0 (
    echo ✅ PASSED
) else (
    echo ❌ FAILED
    set /a FAILED+=1
)

echo.
echo 🖥️  Frontend Tests
echo ----------------

REM Test 5: Frontend Home Page
call :test_endpoint "Frontend Home" "http://localhost:3082" "Child Growth Assistant"
if errorlevel 1 set /a FAILED+=1

REM Test 6: Frontend Coach Page
call :test_endpoint "Frontend Coach" "http://localhost:3082/coach" "parent"
if errorlevel 1 set /a FAILED+=1

REM Test 7: Frontend Static Assets
echo|set /p="Testing Frontend Assets... "
set assets_response=
for /f "delims=" %%i in ('curl -s -I http://localhost:3082/_next/static/ 2^>^&1') do (
    if not defined assets_response (set assets_response=%%i) else (set assets_response=!assets_response! %%i)
)
echo !assets_response! | findstr /C:"200" >nul
if !errorlevel! equ 0 (
    echo ✅ PASSED
) else (
    echo ⚠️  WARNING (may be normal during development)
)

echo.
echo 🔌 WebSocket Tests
echo ----------------

REM Test 8: WebSocket Endpoint (basic connectivity)
echo|set /p="Testing WebSocket Connection... "
REM Use PowerShell to test TCP connection
powershell -Command "$tcpClient = New-Object System.Net.Sockets.TcpClient; try { $tcpClient.Connect('localhost', 8011); $tcpClient.Close(); exit 0 } catch { exit 1 }" >nul 2>&1
if !errorlevel! equ 0 (
    echo ✅ PASSED
) else (
    echo ⚠️  WARNING (WebSocket may not be accessible via TCP test)
)

echo.
echo ================================================

if !FAILED! equ 0 (
    echo 🎉 All tests passed!
    echo.
    echo ✨ Ready for development!
    echo.
    echo Open http://localhost:3082 in your browser to use the app
    endlocal
    exit /b 0
) else (
    echo ❌ !FAILED! test^(s^) failed
    echo.
    echo Troubleshooting:
    echo 1. Make sure both servers are running (start.bat)
    echo 2. Check logs: type backend.log frontend.log
    echo 3. Try restarting: stop.bat ^&^& start.bat
    endlocal
    exit /b 1
)

