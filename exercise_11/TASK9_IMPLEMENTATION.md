# Task 9: Prompt Versioning & Snapshots - Implementation Summary

## ✅ Deliverables Completed

### 1. Versioned Prompt Files
- ✅ `prompts/child_coach_v1.json` - Initial version with proper structure

### 2. Snapshot Tests
- ✅ `backend/tests/test_prompt_snapshots.py` - Comprehensive snapshot tests
- ✅ `backend/tests/snapshots/child_coach_v1.json` - Initial snapshot

### 3. Prompt Changelog
- ✅ `prompts/CHANGELOG.md` - Tracks all prompt version changes

### 4. CI Workflow
- ✅ `.github/workflows/prompt-version-check.yml` - Fails if prompts change without version bump

### 5. Helper Utilities
- ✅ `backend/app/prompt_loader.py` - Module to load and manage prompt versions
- ✅ `prompts/create_version.py` - Script to easily create new prompt versions
- ✅ `prompts/README.md` - Documentation for using the versioning system

## How It Works

### Versioning System

**File Naming:**
- Must follow: `{prompt_id}_v{version}.json`
- Example: `child_coach_v1.json`, `child_coach_v2.json`

**Structure:**
Each prompt file contains:
- `version`: Version number
- `prompt_id`: Identifier (e.g., "child_coach")
- `template`: The actual prompt template with `{{variables}}`
- `metadata`: Creation info, tags
- `changelog`: What changed in this version

### Snapshot Testing

**Purpose:**
- Ensure prompts don't accidentally change
- Catch unintended modifications
- Verify version integrity

**Tests:**
1. `test_prompt_v1_snapshot()` - Verifies v1 matches snapshot
2. `test_all_prompt_versions_have_snapshots()` - Ensures all versions have snapshots
3. `test_prompt_file_naming_convention()` - Validates naming
4. `test_prompt_structure()` - Validates JSON structure

**Generate Snapshots:**
```bash
pytest backend/tests/test_prompt_snapshots.py::test_generate_snapshots -s -m generate_snapshots
```

### CI Enforcement

**Workflow:** `.github/workflows/prompt-version-check.yml`

**Checks:**
1. Detects changed prompt files in PRs/pushes
2. Verifies if template changed in existing version → **FAILS**
3. Allows new version files → **PASSES**
4. Runs snapshot tests
5. Validates version numbers match filenames

**Result:**
- ✅ **Pass**: Created `child_coach_v2.json` with changes
- ❌ **Fail**: Modified `child_coach_v1.json` directly

## Usage Examples

### Creating a New Prompt Version

**Method 1: Using Script (Recommended)**
```bash
cd exercise_11
python prompts/create_version.py child_coach "v2 - Improved empathy"
```

**Method 2: Manual**
```bash
cp prompts/child_coach_v1.json prompts/child_coach_v2.json
# Edit the file, update version, template, changelog
```

### Using Prompts in Code

```python
from app.prompt_loader import get_prompt_version, render_prompt

# Load prompt
prompt = get_prompt_version("child_coach", version=1)

# Render with variables
rendered = render_prompt(
    prompt["template"],
    user_question="How to handle bedtime?",
    retrieved_knowledge="RAG content here..."
)
```

### Running Tests

```bash
# Run all prompt tests
pytest backend/tests/test_prompt_snapshots.py -v

# Generate snapshots (after creating new version)
pytest backend/tests/test_prompt_snapshots.py::test_generate_snapshots -s -m generate_snapshots
```

## Testing the CI Check

### Test Case 1: Valid (Should Pass)
1. Create `prompts/child_coach_v2.json` with new template
2. Update `prompts/CHANGELOG.md`
3. Generate snapshot
4. Push to PR
5. ✅ CI should pass

### Test Case 2: Invalid (Should Fail)
1. Modify `prompts/child_coach_v1.json` template directly
2. Push to PR
3. ❌ CI should fail with error:
   ```
   ERROR: Template changed in child_coach_v1.json without creating new version!
   You must create a new version file (e.g., child_coach_v2.json)
   ```

## Pass Criteria

✅ **Task 9 passes if:**
1. All prompt files follow naming convention
2. All versions have corresponding snapshots
3. CI workflow fails when prompts change without version bump
4. Snapshot tests pass
5. Changelog is maintained

## Files Created

```
exercise_11/
├── prompts/
│   ├── child_coach_v1.json          ✅ Versioned prompt
│   ├── CHANGELOG.md                  ✅ Changelog
│   ├── README.md                     ✅ Documentation
│   └── create_version.py             ✅ Helper script
├── backend/
│   ├── app/
│   │   └── prompt_loader.py           ✅ Prompt loading module
│   └── tests/
│       ├── test_prompt_snapshots.py   ✅ Snapshot tests
│       └── snapshots/
│           └── child_coach_v1.json   ✅ Initial snapshot
└── .github/
    └── workflows/
        └── prompt-version-check.yml   ✅ CI enforcement
```

## Next Steps (Optional)

1. **Integrate prompts into advice generation** - Use `prompt_loader` in `sse.py`/`websocket.py`
2. **Add more prompt types** - Create versions for different use cases
3. **Automated versioning** - Script to bump versions automatically
4. **Prompt A/B testing** - Use versioning for experimentation

---

**Status: ✅ Complete**
All deliverables met. CI will fail if prompts change without version bump.

