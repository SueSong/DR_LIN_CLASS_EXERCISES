# Testing CI Locally (Without Pushing to GitHub)

## Quick Answer

**You DON'T need to push to GitHub to test!** You can test everything locally first.

## What Runs Locally vs GitHub

### ✅ Can Test Locally (Same as CI)

1. **Snapshot tests** - Run locally:
   ```bash
   cd exercise_11/backend
   python -m pytest tests/test_prompt_snapshots.py -v -p no:langsmith
   ```

2. **Snapshot generation** - Run locally:
   ```bash
   backend\tests\create_snap.bat
   ```

3. **All validation checks** - Same tests CI runs

### ❌ Only Runs on GitHub

1. **Git diff checking** - Compares against base branch
2. **GitHub Actions workflow** - Runs automatically on push/PR

## How to Test Locally (Before Pushing)

### Step 1: Create/Update Your Prompt Version

```bash
# Create v2 if you haven't
cd exercise_11
python prompts/create_version.py child_coach "v2 - Your changes"
```

### Step 2: Generate Snapshot

```bash
cd exercise_11/backend/tests
create_snap.bat
```

### Step 3: Run Tests (Same Tests CI Runs)

```bash
cd exercise_11/backend
python -m pytest tests/test_prompt_snapshots.py -v -p no:langsmith
```

**If all tests pass locally → CI will pass too!** ✅

### Step 4: When Ready, Push to GitHub

Only push after local tests pass:

```bash
git add prompts/child_coach_v2.json backend/tests/snapshots/child_coach_v2.json prompts/CHANGELOG.md
git commit -m "Add prompt v2"
git push origin your-branch
```

Then GitHub Actions will run (but should pass since you tested locally).

## What CI Actually Does

The CI workflow runs these steps:
1. ✅ Check git diff for changed files
2. ✅ Verify versioning rules (can test locally by running tests)
3. ✅ Run snapshot tests (YOU CAN RUN THIS LOCALLY)
4. ✅ Report pass/fail

**Steps 1-2 are git-specific, but step 3 is the important test and you CAN run it locally!**

## Local Test Checklist

Before pushing, verify locally:

- [ ] Created new version file (not modified existing)
- [ ] Snapshot generated (`create_snap.bat`)
- [ ] All tests pass (`RUN_TESTS.bat`)
- [ ] Changelog updated
- [ ] Version number matches filename

**If all ✅ → Push with confidence! CI will pass.**

## Quick Local Test Script

I created `test_ci_local.bat` - run it to simulate CI:

```bash
cd exercise_11
test_ci_local.bat
```

This runs the same snapshot tests that CI runs.

## Summary

**You can test everything locally first!**

- ✅ Run snapshot tests locally = Same as CI
- ✅ If local tests pass → CI will pass
- ❌ Only git diff checking requires GitHub
- ✅ But snapshot tests are the main check, and those work locally!

**Test locally → Fix issues → Push → CI confirms (should pass)**

