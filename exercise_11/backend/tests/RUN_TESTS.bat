@echo off
REM Quick script to run prompt snapshot tests without langsmith plugin

cd /d %~dp0\..

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Run tests with langsmith plugin disabled
python -m pytest tests/test_prompt_snapshots.py -v -p no:langsmith

pause

