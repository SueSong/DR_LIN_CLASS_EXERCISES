# What Are Snapshots?

## Purpose

**Snapshots are "golden copies" of your prompts** - they serve as a reference point to detect unexpected changes.

## Why Do We Need Them?

### Problem: Accidental Changes

Without snapshots, someone could accidentally:
- Modify a prompt template without creating a new version
- Make typos or formatting changes
- Break prompt structure without realizing it

### Solution: Snapshot Testing

Snapshots prevent this by:
1. **Storing a known-good copy** of each prompt version
2. **Comparing** the current prompt against the snapshot
3. **Failing tests** if they don't match

## How It Works

### 1. Initial Snapshot

When you create `child_coach_v1.json`, you also create:
- `tests/snapshots/child_coach_v1.json` (the snapshot)

The snapshot is a **copy** of the prompt file for reference.

### 2. Test Comparison

When tests run:
```python
# Test loads current prompt
prompt = get_prompt_version("child_coach", version=1)

# Test loads snapshot
with open("tests/snapshots/child_coach_v1.json") as f:
    expected = json.load(f)

# Test compares them
assert prompt["template"] == expected["template"]  # ✅ or ❌
```

### 3. What Happens

**If prompt matches snapshot:**
- ✅ Test passes
- Prompt hasn't changed (good!)

**If prompt doesn't match snapshot:**
- ❌ Test fails
- Error: "Template has changed! Create a new version if intentional."

## Real-World Example

### Scenario: Someone accidentally edits v1

**What happens:**
1. Developer opens `prompts/child_coach_v1.json`
2. Makes a "small" change to the template
3. Commits the change
4. CI runs tests → **SNAPSHOT TEST FAILS** ❌
5. CI blocks the commit with error:
   ```
   Template has changed in child_coach_v1.json without creating new version!
   You must create child_coach_v2.json instead.
   ```

**What should happen:**
1. Developer wants to change the prompt
2. Creates `child_coach_v2.json` with the new template
3. Updates snapshot: `tests/snapshots/child_coach_v2.json`
4. Tests pass ✅
5. CI approves ✅

## Snapshot Files

**Location:** `backend/tests/snapshots/`

**Naming:** Same as prompt files
- `child_coach_v1.json` → `snapshots/child_coach_v1.json`
- `child_coach_v2.json` → `snapshots/child_coach_v2.json`

**Content:** Exact copy of the prompt JSON

## When to Update Snapshots

### ✅ Update when:
- Creating a **new version** (v2, v3, etc.)
- Intentionally changing a prompt (create new version first!)

### ❌ Don't update when:
- Accidentally editing an existing version
- Making typos
- The snapshot test fails unexpectedly

## Commands

### Generate Snapshots

After creating a new prompt version:
```bash
pytest tests/test_prompt_snapshots.py::test_generate_snapshots -s -m generate_snapshots
```

This creates snapshot files for all prompt versions.

### Run Snapshot Tests

Check if prompts match snapshots:
```bash
pytest tests/test_prompt_snapshots.py -v
```

## Summary

**Snapshots = Safety Net**

They ensure:
- ✅ Prompt versions are **immutable** (can't change without new version)
- ✅ Accidental edits are **caught immediately**
- ✅ Version history is **preserved**
- ✅ CI enforces **proper versioning workflow**

Think of snapshots like a **lock** on your prompt files - they prevent unauthorized changes and force proper version management.

