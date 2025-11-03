# Test Breakdown - What Each Test Does

## The 5 Tests Explained

Even though you only have **one snapshot file** (`child_coach_v1.json`), there are **5 tests** because they check different things:

### 1. `test_prompt_v1_snapshot` ✅
**Purpose:** The **actual snapshot comparison test**

**What it does:**
- Loads the current `child_coach_v1.json` prompt
- Loads the snapshot `tests/snapshots/child_coach_v1.json`
- Compares them to ensure they match
- **This is the main protection against accidental changes**

**Uses snapshot:** ✅ YES - directly compares against snapshot file

---

### 2. `test_all_prompt_versions_have_snapshots` ✅
**Purpose:** Ensures every prompt version has a snapshot

**What it does:**
- Lists all prompt versions (currently just v1)
- Checks that each version has a corresponding snapshot file
- **Prevents you from forgetting to create snapshots**

**Uses snapshot:** ⚠️ PARTIALLY - checks if snapshot file exists, doesn't compare content

**Why it passes:** You have `child_coach_v1.json` in both places, so it passes.

---

### 3. `test_generate_snapshots` ✅
**Purpose:** Utility test to generate snapshot files

**What it does:**
- Creates snapshot files for all prompt versions
- **Helper test** - run this when you create a new version
- Useful for initial setup

**Uses snapshot:** ⚠️ CREATES - generates snapshot files, doesn't compare

**Why it passes:** Successfully created/generated the snapshot (or verified it exists)

---

### 4. `test_prompt_file_naming_convention` ✅
**Purpose:** Validates file naming rules

**What it does:**
- Checks all `.json` files in `prompts/` directory
- Verifies they follow pattern: `{prompt_id}_v{version}.json`
- **Ensures naming consistency**

**Uses snapshot:** ❌ NO - checks file naming, not snapshot content

**Why it passes:** Your file `child_coach_v1.json` follows the correct naming pattern

---

### 5. `test_prompt_structure` ✅
**Purpose:** Validates JSON structure and required fields

**What it does:**
- Loads each prompt version
- Checks for required fields: `version`, `prompt_id`, `template`
- Verifies `version` number matches filename
- **Ensures prompts are valid and well-formed**

**Uses snapshot:** ❌ NO - checks JSON structure, not snapshot content

**Why it passes:** Your `child_coach_v1.json` has all required fields and valid structure

---

## Summary

| Test | Purpose | Uses Snapshot? |
|------|---------|----------------|
| 1. `test_prompt_v1_snapshot` | Compare v1 against snapshot | ✅ **YES** |
| 2. `test_all_prompt_versions_have_snapshots` | Check snapshots exist | ⚠️ Checks existence |
| 3. `test_generate_snapshots` | Generate snapshots | ⚠️ Creates them |
| 4. `test_prompt_file_naming_convention` | Validate naming | ❌ NO |
| 5. `test_prompt_structure` | Validate structure | ❌ NO |

## Why 5 Tests?

Only **Test #1** directly compares prompt against snapshot. The other 4 tests ensure:
- ✅ Snapshots are created (tests 2, 3)
- ✅ Files follow rules (test 4)
- ✅ Data is valid (test 5)

**All together = Complete protection!**

When you create v2, you'll need `child_coach_v2.json` and `snapshots/child_coach_v2.json`, and test #1 will check v2 against its snapshot too.

