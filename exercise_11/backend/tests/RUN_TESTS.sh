#!/bin/bash
# Quick script to run prompt snapshot tests without langsmith plugin

cd "$(dirname "$0")/.."

# Activate virtual environment if it exists
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# Run tests with langsmith plugin disabled
python -m pytest tests/test_prompt_snapshots.py -v -p no:langsmith

