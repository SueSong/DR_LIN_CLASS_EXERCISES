@echo off
REM Generate snapshot files for all prompt versions
REM Run this after creating a new prompt version (e.g., child_coach_v2.json)

cd /d %~dp0\..

echo ========================================
echo Generating Prompt Snapshots
echo ========================================
echo.

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo Using virtual environment...
) else (
    echo No virtual environment found, using system Python...
)

echo.
echo Running snapshot generation...
echo.

REM Run the snapshot generation test
python -m pytest tests/test_prompt_snapshots.py::test_generate_snapshots -s -m generate_snapshots -p no:langsmith

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo ✅ Snapshots generated successfully!
    echo ========================================
    echo.
    echo Snapshot files created in: tests\snapshots\
) else (
    echo.
    echo ========================================
    echo ❌ Snapshot generation failed!
    echo ========================================
    exit /b %ERRORLEVEL%
)

echo.
pause

