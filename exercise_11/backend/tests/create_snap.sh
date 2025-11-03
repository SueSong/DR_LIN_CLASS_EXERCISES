#!/bin/bash
# Generate snapshot files for all prompt versions
# Run this after creating a new prompt version (e.g., child_coach_v2.json)

cd "$(dirname "$0")/.."

echo "========================================"
echo "Generating Prompt Snapshots"
echo "========================================"
echo ""

# Activate virtual environment if it exists
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "Using virtual environment..."
else
    echo "No virtual environment found, using system Python..."
fi

echo ""
echo "Running snapshot generation..."
echo ""

# Run the snapshot generation test
python -m pytest tests/test_prompt_snapshots.py::test_generate_snapshots -s -m generate_snapshots -p no:langsmith

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "✅ Snapshots generated successfully!"
    echo "========================================"
    echo ""
    echo "Snapshot files created in: tests/snapshots/"
else
    echo ""
    echo "========================================"
    echo "❌ Snapshot generation failed!"
    echo "========================================"
    exit 1
fi

