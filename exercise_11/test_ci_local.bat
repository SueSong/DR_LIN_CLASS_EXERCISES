@echo off
REM Local CI test script - Simulates GitHub Actions checks
REM Tests that prompts follow versioning rules

cd /d %~dp0

echo ========================================
echo Testing CI Workflow Logic (Local)
echo ========================================
echo.

REM Check if git is available
where git >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Git not found. CI test requires git.
    echo    For manual testing, run: backend\tests\RUN_TESTS.bat
    pause
    exit /b 1
)

echo Checking for prompt changes...
echo.

REM Get changed files (compare with HEAD)
echo Changed prompt files in working directory:
git diff --name-only HEAD | findstr /R "prompts.*\.json$"

if %ERRORLEVEL% NEQ 0 (
    echo No prompt files changed (or no changes staged)
    echo.
)

echo.
echo Running snapshot tests...
echo.

cd backend

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo Using virtual environment...
)

REM Disable langsmith plugin to avoid compatibility issues
REM pytest.ini should handle this, but explicitly disable just in case
python -m pytest tests/test_prompt_snapshots.py -v -p no:langsmith

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Tests failed! CI would reject this.
    pause
    exit /b 1
)

echo.
echo ========================================
echo ✅ Local CI Checks Passed
echo ========================================
echo.
echo Next steps:
echo 1. Commit your changes
echo 2. Push to GitHub
echo 3. Create a Pull Request
echo 4. GitHub Actions will run the real CI
echo.
pause

