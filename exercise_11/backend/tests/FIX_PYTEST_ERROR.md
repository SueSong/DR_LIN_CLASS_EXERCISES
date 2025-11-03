# Fix: pytest langsmith Plugin Error

## Problem

You're getting this error:
```
TypeError: ForwardRef._evaluate() missing 1 required keyword-only argument: 'recursive_guard'
```

This is caused by the `langsmith` pytest plugin being incompatible with your Python 3.12 environment.

## Solutions

### Solution 1: Disable langsmith Plugin (Quick Fix)

Run pytest with the plugin disabled:
```bash
cd exercise_11/backend
python -m pytest tests/test_prompt_snapshots.py -v -p no:langsmith
```

Or from project root:
```bash
cd exercise_11
python -m pytest backend/tests/test_prompt_snapshots.py -v -p no:langsmith
```

### Solution 2: Use pytest.ini (Automatic)

I've created `backend/pytest.ini` that automatically disables the problematic plugin.

Now you can just run:
```bash
cd exercise_11/backend
python -m pytest tests/test_prompt_snapshots.py -v
```

### Solution 3: Use Virtual Environment (Best Practice)

If you have a virtual environment without langsmith:
```bash
cd exercise_11/backend
venv\Scripts\activate  # Windows
pip install pytest pytest-asyncio
python -m pytest tests/test_prompt_snapshots.py -v
```

### Solution 4: Uninstall langsmith Globally

If you don't need langsmith:
```bash
pip uninstall langsmith
```

Then pytest should work normally.

## Quick Test Commands

```bash
# From backend directory (with pytest.ini)
cd exercise_11/backend
python -m pytest tests/test_prompt_snapshots.py -v

# From project root (with plugin disabled)
cd exercise_11
python -m pytest backend/tests/test_prompt_snapshots.py -v -p no:langsmith

# Generate snapshots
python -m pytest backend/tests/test_prompt_snapshots.py::test_generate_snapshots -s -m generate_snapshots -p no:langsmith
```

## Why This Happens

The `langsmith` package installs a pytest plugin automatically. This plugin tries to use pydantic v1 which has a compatibility issue with Python 3.12's `ForwardRef._evaluate()` method signature change.

The `-p no:langsmith` flag tells pytest to skip loading that plugin.

