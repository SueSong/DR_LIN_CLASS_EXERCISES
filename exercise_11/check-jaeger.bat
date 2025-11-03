@echo off
echo Checking Jaeger status...
echo.

echo Checking if port 16686 is listening...
netstat -ano | findstr "16686"
echo.

echo Trying to check Docker containers...
docker ps --filter "name=jaeger" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>nul
echo.

echo If Jaeger container is not running, try:
echo   cd monorepo
echo   docker-compose up -d jaeger
echo.
echo Or if using exercise_11 docker-compose:
echo   cd exercise_11
echo   docker-compose up -d jaeger
echo.

pause

