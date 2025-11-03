# How to Find and Run test_generate_snapshots

## Where Is It?

**File:** `backend/tests/test_prompt_snapshots.py`  
**Line:** Around line 49  
**Function name:** `test_generate_snapshots`

## It's a Test Function

`test_generate_snapshots` is **not a separate file** - it's a **function** inside the test file.

```python
# In backend/tests/test_prompt_snapshots.py

@pytest.mark.generate_snapshots
def test_generate_snapshots():  # ← This is the function!
    """
    Generate snapshot files for all prompt versions.
    """
    # ... code to generate snapshots ...
```

## How to Run It

### Method 1: Use create_snap.bat (Easiest) ✅

```bash
cd exercise_11/backend/tests
create_snap.bat
```

This script calls `test_generate_snapshots` for you!

### Method 2: Run the Test Function Directly

```bash
cd exercise_11/backend
python -m pytest tests/test_prompt_snapshots.py::test_generate_snapshots -s -m generate_snapshots -p no:langsmith
```

### Method 3: Run from Project Root

```bash
cd exercise_11
python -m pytest backend/tests/test_prompt_snapshots.py::test_generate_snapshots -s -m generate_snapshots -p no:langsmith
```

## Visual Guide

```
exercise_11/
  └── backend/
      └── tests/
          ├── test_prompt_snapshots.py  ← The file
          │   ├── def test_prompt_v1_snapshot(): ...
          │   ├── def test_all_prompt_versions_have_snapshots(): ...
          │   ├── def test_generate_snapshots(): ... ← IT'S HERE!
          │   ├── def test_prompt_file_naming_convention(): ...
          │   └── def test_prompt_structure(): ...
          └── create_snap.bat  ← Calls test_generate_snapshots
```

## Quick Test

**See all test functions in the file:**

```bash
cd exercise_11/backend
python -m pytest tests/test_prompt_snapshots.py --collect-only
```

This will list all test functions including `test_generate_snapshots`.

## Summary

**You don't "find" it as a file** - it's a **function** in:
- **File:** `backend/tests/test_prompt_snapshots.py`
- **Function:** `test_generate_snapshots()`
- **Easiest way to run:** Use `create_snap.bat` script!

