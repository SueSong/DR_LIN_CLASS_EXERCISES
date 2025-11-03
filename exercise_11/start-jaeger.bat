@echo off
REM Start Jaeger and Grafana for Exercise 11

echo Starting Jaeger and Grafana...
docker-compose -f docker-compose.yml up -d

echo.
echo Waiting for services to start...
timeout /t 5 /nobreak >nul

echo.
echo Checking service status...
docker-compose -f docker-compose.yml ps

echo.
echo ========================================
echo Jaeger UI: http://localhost:16686
echo Grafana UI: http://localhost:3001
echo   - Username: admin
echo   - Password: 636492
echo ========================================
echo.
echo To stop services: docker-compose -f docker-compose.yml down
echo.

