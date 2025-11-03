# How to Test CI Workflow for Prompt v2

## Understanding the CI Workflow

The CI workflow (`.github/workflows/prompt-version-check.yml`) checks that:
1. ✅ If you create a **new version file** (v2.json) → **PASS**
2. ❌ If you **modify existing version** (v1.json) → **FAIL**

## Testing Methods

### Method 1: Test Locally (Recommended)

You can test the CI logic locally before pushing:

#### Step 1: Simulate Creating v2 (Should Pass)

```bash
# 1. Create v2 file
cd exercise_11
python prompts/create_version.py child_coach "v2 - Testing CI"

# 2. Generate snapshot
cd backend
python -m pytest tests/test_prompt_snapshots.py::test_generate_snapshots -s -m generate_snapshots -p no:langsmith

# 3. Run snapshot tests (should pass)
python -m pytest tests/test_prompt_snapshots.py -v -p no:langsmith
```

**Expected:** ✅ All tests pass (new version is OK)

#### Step 2: Simulate Modifying v1 (Should Fail)

```bash
# 1. Edit v1 directly (WRONG - this should fail)
cd exercise_11/prompts
# Edit child_coach_v1.json, change the template

# 2. Run snapshot test (should fail)
cd ../backend
python -m pytest tests/test_prompt_snapshots.py::test_prompt_v1_snapshot -v -p no:langsmith
```

**Expected:** ❌ Test fails with: "Template has changed! Create a new version if intentional."

### Method 2: Test via GitHub Actions (Real CI)

#### Option A: Create a Test Branch and PR

```bash
# 1. Create a test branch
git checkout -b test-prompt-v2-ci

# 2. Create v2
cd exercise_11
python prompts/create_version.py child_coach "v2 - Testing CI workflow"
cd backend
python -m pytest tests/test_prompt_snapshots.py::test_generate_snapshots -s -m generate_snapshots -p no:langsmith

# 3. Commit and push
git add prompts/child_coach_v2.json backend/tests/snapshots/child_coach_v2.json prompts/CHANGELOG.md
git commit -m "Test: Add prompt v2 to test CI"
git push origin test-prompt-v2-ci

# 4. Create Pull Request
# GitHub will automatically run the CI workflow
```

**Expected:** ✅ CI should pass (new version file created)

#### Option B: Modify v1 in PR (Should Fail)

```bash
# 1. Create test branch
git checkout -b test-prompt-v1-modify

# 2. Edit v1 directly (WRONG)
# Modify prompts/child_coach_v1.json template

# 3. Commit
git add prompts/child_coach_v1.json
git commit -m "Test: Modify v1 (should fail CI)"

# 4. Push and create PR
git push origin test-prompt-v1-modify
```

**Expected:** ❌ CI should fail with error message

### Method 3: Manual CI Script (Local Simulation)

I can create a script that mimics the CI checks. Would you like me to create `test_ci_local.bat`?

## What the CI Actually Checks

The workflow does these checks:

### ✅ Valid: Creating New Version

**What happens:**
```
Changes:
  + prompts/child_coach_v2.json (new file)

CI Check:
  - Detects new file
  - Verifies naming: child_coach_v2.json
  - Verifies version in JSON matches: version: 2
  - Runs snapshot tests
  → ✅ PASS
```

### ❌ Invalid: Modifying Existing Version

**What happens:**
```
Changes:
  ~ prompts/child_coach_v1.json (modified)

CI Check:
  - Detects modified file
  - Compares template against base branch
  - Template changed!
  → ❌ FAIL with error:
     "Template changed in child_coach_v1.json without creating new version!"
```

## Quick Test Commands

### Test 1: Verify v2 Setup (Should Pass)

```bash
cd exercise_11/backend
python -m pytest tests/test_prompt_snapshots.py -v -p no:langsmith
```

### Test 2: Verify v2 Snapshot Exists

```bash
cd exercise_11/backend
python -c "from app.prompt_loader import list_prompt_versions; print('Versions:', list_prompt_versions('child_coach'))"
```

### Test 3: Test Snapshot Comparison

```bash
cd exercise_11/backend
python -m pytest tests/test_prompt_snapshots.py::test_prompt_v1_snapshot -v -p no:langsmith
python -m pytest tests/test_prompt_snapshots.py::test_all_prompt_versions_have_snapshots -v -p no:langsmith
```

## Testing Checklist

Before pushing to GitHub:

- [ ] Created `child_coach_v2.json` (not modified v1)
- [ ] v2 has correct `version: 2` in JSON
- [ ] Generated snapshot: `tests/snapshots/child_coach_v2.json`
- [ ] Updated `prompts/CHANGELOG.md`
- [ ] All local tests pass: `pytest tests/test_prompt_snapshots.py -v`
- [ ] Files follow naming: `child_coach_v2.json`

## Expected CI Behavior

### When You Push v2:

**GitHub Actions Log Will Show:**
```
✓ Changed prompt files:
  prompts/child_coach_v2.json

✓ Checking file: child_coach_v2.json
  ✓ New version file: child_coach_v2.json
  ✓ Version matches filename: v2

✓ Running prompt snapshot tests...
  ✓ test_prompt_v1_snapshot PASSED
  ✓ test_prompt_v2_snapshot PASSED
  ✓ test_all_prompt_versions_have_snapshots PASSED
  ...

✅ CI passed: New version created correctly
```

## Troubleshooting

**If CI fails:**

1. **Check error message** - It will tell you what's wrong
2. **Verify file naming** - Must be `child_coach_v2.json`
3. **Verify version field** - Must match filename version
4. **Check snapshot exists** - Run `create_snap.bat`
5. **Check changelog** - Update `prompts/CHANGELOG.md`

## Summary

**To test CI for prompt v2:**

1. **Create v2** (not modify v1)
2. **Generate snapshot** (`create_snap.bat`)
3. **Run local tests** (`RUN_TESTS.bat`)
4. **Commit and push** (CI runs automatically)
5. **Check GitHub Actions** tab for results

The CI will automatically run when you push a PR with prompt changes!

