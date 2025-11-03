# How Snapshot Discovery Works

## The Process

When you run `create_snap.bat`, it calls:
```bash
pytest tests/test_prompt_snapshots.py::test_generate_snapshots -s -m generate_snapshots
```

This test automatically discovers ALL prompt files. Here's how:

## Step-by-Step Discovery

### 1. The Test Calls `list_prompt_versions()`

```python
def test_generate_snapshots():
    versions = list_prompt_versions("child_coach")  # ← Discovers all versions
```

### 2. `list_prompt_versions()` Searches for Files

Looking at `backend/app/prompt_loader.py`:

```python
def list_prompt_versions(prompt_id: str = "child_coach") -> list:
    project_root = Path(__file__).parent.parent.parent
    prompts_dir = project_root / "prompts"
    
    # Find all files matching pattern: {prompt_id}_v*.json
    pattern = f"{prompt_id}_v*.json"
    prompt_files = list(prompts_dir.glob(pattern))  # ← Searches prompts/ directory
    
    versions = []
    for file in prompt_files:
        # Extract version from filename: child_coach_v2.json → 2
        version_part = file.stem.split("_v")[-1]
        version = int(version_part)
        versions.append(version)
    
    return sorted(versions)  # Returns: [1, 2, 3, ...]
```

### 3. For Each Version, Create Snapshot

```python
for version in versions:  # [1, 2, ...]
    prompt = get_prompt_version("child_coach", version=version)  # Load the JSON
    snapshot_file = SNAPSHOTS_DIR / f"child_coach_v{version}.json"
    
    # Write snapshot
    with open(snapshot_file, 'w') as f:
        json.dump(prompt, f, indent=2)
```

## File Pattern Matching

The script uses **filename pattern matching**:

**Pattern:** `child_coach_v*.json`

**Matches:**
- ✅ `child_coach_v1.json` → version 1
- ✅ `child_coach_v2.json` → version 2
- ✅ `child_coach_v10.json` → version 10
- ❌ `other_prompt_v1.json` → skipped (wrong prompt_id)
- ❌ `child_coach_v1.1.json` → skipped (version must be integer)

## Example Discovery Flow

### Current Files:
```
prompts/
  ├── child_coach_v1.json  ← Found!
  └── child_coach_v2.json  ← Found!
```

### Discovery Process:
1. Search `prompts/` for `child_coach_v*.json`
2. Find: `child_coach_v1.json`, `child_coach_v2.json`
3. Extract versions: `[1, 2]`
4. Sort: `[1, 2]`
5. Create snapshots:
   - `tests/snapshots/child_coach_v1.json`
   - `tests/snapshots/child_coach_v2.json`

## How to Add More Versions

**Just create the file!** The script will automatically discover it:

```bash
# 1. Create new version
cp prompts/child_coach_v2.json prompts/child_coach_v3.json

# 2. Edit v3 with your changes

# 3. Run snapshot generation
tests\create_snap.bat

# 4. It automatically creates:
#    tests/snapshots/child_coach_v1.json ✅
#    tests/snapshots/child_coach_v2.json ✅
#    tests/snapshots/child_coach_v3.json ✅ (new!)
```

## Multiple Prompt Types

If you had multiple prompt types:
```
prompts/
  ├── child_coach_v1.json
  ├── child_coach_v2.json
  ├── safety_guard_v1.json      ← Different prompt_id
  └── safety_guard_v2.json
```

The current script only processes `child_coach` prompts because:
```python
versions = list_prompt_versions("child_coach")  # Hard-coded!
```

To process all prompt types, you'd need to:
1. Discover all prompt IDs first
2. Then generate snapshots for each

## Summary

**The script discovers files by:**
1. ✅ Scanning `prompts/` directory
2. ✅ Matching filename pattern: `{prompt_id}_v*.json`
3. ✅ Extracting version numbers from filenames
4. ✅ Creating snapshots for ALL discovered versions

**You don't need to tell it which files** - it finds them automatically by pattern matching!

