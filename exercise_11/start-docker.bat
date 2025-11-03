@echo off
echo ============================================
echo Starting Docker Desktop
echo ============================================
echo.

echo Checking if Docker Desktop is already running...
tasklist | findstr /i "Docker Desktop" >nul
if %errorlevel% == 0 (
    echo Docker Desktop appears to be running.
    echo If you can't see it, check the system tray (bottom-right).
    pause
    exit /b
)

echo.
echo Attempting to start Docker Desktop...
echo.

REM Try common Docker Desktop installation paths
set DOCKER_PATHS[0]="C:\Program Files\Docker\Docker\Docker Desktop.exe"
set DOCKER_PATHS[1]="%LOCALAPPDATA%\Programs\Docker\Docker\Docker Desktop.exe"
set DOCKER_PATHS[2]="C:\Program Files (x86)\Docker\Docker\Docker Desktop.exe"

for /l %%i in (0,1,2) do (
    call set "path=%%DOCKER_PATHS[%%i]%%"
    if exist !path! (
        echo Found Docker Desktop at: !path!
        echo Starting...
        start "" !path!
        echo.
        echo Docker Desktop is starting. Please wait 30-60 seconds.
        echo Check the system tray (bottom-right) for the Docker icon.
        echo.
        timeout /t 5 /nobreak >nul
        pause
        exit /b
    )
)

echo.
echo Docker Desktop executable not found in common locations.
echo.
echo Please start Docker Desktop manually:
echo 1. Press Windows key
echo 2. Type "Docker Desktop"
echo 3. Click on the Docker Desktop app
echo.
echo Or find it in:
echo   - Start Menu -> Docker Desktop
echo   - Desktop shortcut
echo.
pause

