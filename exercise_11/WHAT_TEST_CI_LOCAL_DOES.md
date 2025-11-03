# What Does test_ci_local.bat Do?

## Yes, It Runs Snapshot Tests!

`test_ci_local.bat` is a **wrapper script** that runs snapshot tests (and more).

## What It Does

### 1. Checks Git Changes (Optional Info)
```bash
git diff --name-only HEAD | findstr /R "prompts.*\.json$"
```
- Shows which prompt files changed
- **Just for information** - doesn't block tests

### 2. Runs Snapshot Tests (Main Check) ✅
```bash
python -m pytest tests/test_prompt_snapshots.py -v -p no:langsmith
```
- **This IS the snapshot test suite!**
- Runs all 5 snapshot tests:
  - `test_prompt_v1_snapshot` - Compares v1 against snapshot
  - `test_all_prompt_versions_have_snapshots` - Checks snapshots exist
  - `test_generate_snapshots` - Can generate snapshots
  - `test_prompt_file_naming_convention` - Validates naming
  - `test_prompt_structure` - Validates structure

### 3. Reports Results
- ✅ Pass → "Local CI Checks Passed"
- ❌ Fail → "Tests failed! CI would reject this."

## Relationship: test_ci_local.bat vs Snapshot Tests

```
test_ci_local.bat
    │
    ├─> Shows git changes (optional)
    │
    └─> Runs snapshot tests
            │
            ├─> test_prompt_v1_snapshot
            ├─> test_all_prompt_versions_have_snapshots  
            ├─> test_generate_snapshots
            ├─> test_prompt_file_naming_convention
            └─> test_prompt_structure
```

## Direct Comparison

### Option 1: Run test_ci_local.bat (Wrapper)
```bash
cd exercise_11
test_ci_local.bat
```
- Shows git info
- Runs snapshot tests
- Gives CI-style feedback

### Option 2: Run Snapshot Tests Directly (Same Tests)
```bash
cd exercise_11/backend
python -m pytest tests/test_prompt_snapshots.py -v -p no:langsmith
```
- Runs snapshot tests only
- No git checking
- Same tests, less wrapper

### Option 3: Use RUN_TESTS.bat (Same Tests)
```bash
cd exercise_11/backend/tests
RUN_TESTS.bat
```
- Runs snapshot tests
- Cleaner output

## What's the Difference?

| Script | Runs Snapshot Tests? | Shows Git Info? | CI-Style Output? |
|--------|---------------------|-----------------|------------------|
| `test_ci_local.bat` | ✅ YES | ✅ YES | ✅ YES |
| Direct pytest | ✅ YES | ❌ NO | ❌ NO |
| `RUN_TESTS.bat` | ✅ YES | ❌ NO | ❌ NO |

## Summary

**YES, `test_ci_local.bat` runs snapshot tests!**

It's essentially:
1. Check git (optional info)
2. **Run snapshot tests** ← Main part
3. Report results

The snapshot tests are the **core** of what it does. The git checking is just extra information.

**Bottom line:** Running `test_ci_local.bat` = Running snapshot tests + git info + CI-style messages.

