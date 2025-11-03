# How to Run Pytest Tests

## Installation

pytest is already in `requirements.txt`. Install it:

```bash
cd exercise_11/backend
pip install -r requirements.txt
```

Or install just pytest:
```bash
pip install pytest pytest-asyncio
```

## Running Tests

### From Project Root

```bash
# Run all tests
pytest exercise_11/backend/tests/

# Run prompt snapshot tests only
pytest exercise_11/backend/tests/test_prompt_snapshots.py -v

# Run safety guard tests only
pytest exercise_11/backend/tests/test_safety_guards.py -v
```

### From Backend Directory

```bash
cd exercise_11/backend

# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_prompt_snapshots.py -v

# Run specific test function
pytest tests/test_prompt_snapshots.py::test_prompt_v1_snapshot -v
```

### Generate Snapshots (After Creating New Prompt Version)

```bash
cd exercise_11/backend
pytest tests/test_prompt_snapshots.py::test_generate_snapshots -s -m generate_snapshots
```

## Using Virtual Environment (Recommended)

If you have a virtual environment:

```bash
cd exercise_11/backend

# Activate virtual environment
# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v
```

## Troubleshooting

### "pytest: command not found"

**Solution 1:** Install pytest globally:
```bash
pip install pytest pytest-asyncio
```

**Solution 2:** Use Python module:
```bash
python -m pytest tests/ -v
```

### Import Errors

Make sure you're running from the project root or backend directory:
```bash
# From project root
cd exercise_11/backend
pytest tests/
```

### Virtual Environment Issues

If virtual environment pytest doesn't work:
```bash
# Recreate virtual environment
cd exercise_11/backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

## Quick Test Commands

```bash
# Test prompt versioning
cd exercise_11/backend
pytest tests/test_prompt_snapshots.py::test_prompt_v1_snapshot -v

# Test all prompt tests
pytest tests/test_prompt_snapshots.py -v

# Test everything
pytest tests/ -v
```

