# Prompt Changelog

This file tracks changes to prompt templates. All prompt changes must be versioned.

## Format

Each entry should include:
- **Version**: Version number (v1, v2, etc.)
- **Date**: Date of change
- **Author**: Who made the change
- **Description**: What changed and why

---

## Version History

### v1 (2025-01-01)
**Author**: system  
**Description**: Initial prompt template for parenting coach

Initial version of the child coach prompt template. Includes:
- Basic structure for parent questions
- RAG knowledge integration
- Citation support
- Empathetic tone guidelines

---

## How to Add a New Version

1. **Create new prompt file**: `child_coach_v2.json`
2. **Update version number** in the JSON file
3. **Add changelog entry** in this file
4. **Generate new snapshot**: 
   ```bash
   pytest backend/tests/test_prompt_snapshots.py::test_generate_snapshots -s -m generate_snapshots
   ```
5. **Run tests** to verify:
   ```bash
   pytest backend/tests/test_prompt_snapshots.py
   ```

## Version Bump Rules

- **Major changes** (template structure, new variables): Increment major version
- **Minor changes** (tone adjustments, wording): Increment minor version
- **Patch changes** (typos, formatting): Increment patch version

For this task, we use simple sequential versioning (v1, v2, v3, etc.).

