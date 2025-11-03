# Prompt Versioning System

This directory contains versioned prompt templates for the Child Growth Assistant.

## File Structure

```
prompts/
├── child_coach_v1.json    # Version 1 of the child coach prompt
├── child_coach_v2.json    # Version 2 (when created)
├── CHANGELOG.md           # Changelog of all prompt changes
└── create_version.py      # Helper script to create new versions
```

## Naming Convention

Prompt files must follow this naming pattern:
```
{prompt_id}_v{version}.json
```

Examples:
- `child_coach_v1.json` ✅
- `child_coach_v2.json` ✅
- `child_coach_v1.1.json` ❌ (invalid)

## Prompt File Structure

Each prompt file must contain:

```json
{
  "version": 1,
  "prompt_id": "child_coach",
  "name": "Description",
  "description": "Long description",
  "template": "Prompt template with {{variables}}",
  "variables": ["user_question", "retrieved_knowledge"],
  "metadata": {
    "created_at": "2025-01-01T00:00:00Z",
    "created_by": "author",
    "tags": ["tag1", "tag2"]
  },
  "changelog": "What changed in this version"
}
```

## Creating a New Version

### Method 1: Using the Helper Script (Recommended)

```bash
cd exercise_11
python prompts/create_version.py [prompt_id] ["changelog message"]
```

Example:
```bash
python prompts/create_version.py child_coach "v2 - Improved empathy and structure"
```

### Method 2: Manual

1. Copy the latest version file:
   ```bash
   cp prompts/child_coach_v1.json prompts/child_coach_v2.json
   ```

2. Edit the new file:
   - Update `version` to 2
   - Update `template` with your changes
   - Update `metadata.created_at`
   - Update `changelog`

3. Update `prompts/CHANGELOG.md`

4. Generate snapshot:
   ```bash
   # From project root
   cd exercise_11
   pytest backend/tests/test_prompt_snapshots.py::test_generate_snapshots -s -m generate_snapshots
   
   # OR from backend directory
   cd exercise_11/backend
   pytest tests/test_prompt_snapshots.py::test_generate_snapshots -s -m generate_snapshots
   ```

## Testing

Run snapshot tests:
```bash
pytest backend/tests/test_prompt_snapshots.py -v
```

Generate snapshots (after creating new version):
```bash
# From project root (exercise_11/)
cd exercise_11
pytest backend/tests/test_prompt_snapshots.py::test_generate_snapshots -s -m generate_snapshots

# OR from backend directory
cd exercise_11/backend
pytest tests/test_prompt_snapshots.py::test_generate_snapshots -s -m generate_snapshots

# OR using Python module (if pytest not in PATH)
python -m pytest backend/tests/test_prompt_snapshots.py::test_generate_snapshots -s -m generate_snapshots
```

## CI Enforcement

The CI workflow (`.github/workflows/prompt-version-check.yml`) will:
- ✅ **Pass** if you create a new version file (e.g., `child_coach_v2.json`)
- ❌ **Fail** if you modify an existing version file without creating a new one

## Using Prompts in Code

```python
from app.prompt_loader import get_prompt_version, render_prompt

# Load a specific version
prompt = get_prompt_version("child_coach", version=1)

# Render with variables
rendered = render_prompt(
    prompt["template"],
    user_question="How to handle bedtime?",
    retrieved_knowledge="..."
)
```

## Best Practices

1. **Always version**: Never modify existing prompt files
2. **Document changes**: Update CHANGELOG.md with what and why
3. **Test changes**: Run snapshot tests before committing
4. **Review carefully**: Prompt changes affect production behavior

## Current Versions

- **v1**: Initial prompt template for parenting coach

See `CHANGELOG.md` for detailed history.

