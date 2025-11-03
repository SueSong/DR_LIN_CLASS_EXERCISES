@echo off
echo ============================================
echo Restarting Observability Services
echo ============================================
echo.

echo Step 1: Checking if containers are running...
docker ps --format "table {{.Names}}\t{{.Status}}" | findstr /i "jaeger grafana"
echo.

echo Step 2: Stopping any existing containers...
docker stop jaeger exercise11-jaeger grafana exercise11-grafana 2>nul
docker rm jaeger exercise11-jaeger grafana exercise11-grafana 2>nul
echo.

echo Step 3: Starting Jaeger and Grafana from exercise_11...
cd /d "%~dp0"
docker-compose -f docker-compose.yml up -d
echo.

echo Step 4: Waiting 10 seconds for services to start...
timeout /t 10 /nobreak >nul
echo.

echo Step 5: Checking service status...
docker-compose -f docker-compose.yml ps
echo.

echo Step 6: Testing connections...
echo Testing Jaeger (port 16686)...
curl -s http://localhost:16686 -m 3 >nul 2>&1
if %errorlevel% == 0 (
    echo   [OK] Jaeger is responding
) else (
    echo   [FAIL] Jaeger is not responding
)
echo.

echo Testing Grafana (port 3001)...
curl -s http://localhost:3001 -m 3 >nul 2>&1
if %errorlevel% == 0 (
    echo   [OK] Grafana is responding
) else (
    echo   [FAIL] Grafana is not responding
)
echo.

echo ============================================
echo Services should be available at:
echo   Jaeger UI: http://localhost:16686
echo   Grafana UI: http://localhost:3001
echo   - Username: admin
echo   - Password: 636492
echo ============================================
echo.

pause

