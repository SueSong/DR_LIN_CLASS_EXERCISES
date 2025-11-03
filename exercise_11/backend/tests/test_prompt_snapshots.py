"""
Snapshot tests for prompt templates.
These tests ensure prompts don't change without version bumps.
"""

import json
import pytest
from pathlib import Path
from app.prompt_loader import get_prompt_version, list_prompt_versions

# Path to snapshots directory
SNAPSHOTS_DIR = Path(__file__).parent / "snapshots"


def test_prompt_v1_snapshot():
    """Test that prompt v1 matches its snapshot."""
    prompt = get_prompt_version("child_coach", version=1)
    
    # Load snapshot
    snapshot_file = SNAPSHOTS_DIR / "child_coach_v1.json"
    assert snapshot_file.exists(), f"Snapshot file not found: {snapshot_file}"
    
    with open(snapshot_file, 'r', encoding='utf-8') as f:
        expected = json.load(f)
    
    # Compare critical fields
    assert prompt["version"] == expected["version"], "Version mismatch"
    assert prompt["prompt_id"] == expected["prompt_id"], "Prompt ID mismatch"
    assert prompt["template"] == expected["template"], "Template has changed! Create a new version if intentional."
    
    # Compare metadata (may differ slightly, but structure should match)
    assert "metadata" in prompt, "Missing metadata"
    assert "metadata" in expected, "Missing metadata in snapshot"


def test_all_prompt_versions_have_snapshots():
    """Test that all prompt versions have corresponding snapshot files."""
    versions = list_prompt_versions("child_coach")
    
    for version in versions:
        snapshot_file = SNAPSHOTS_DIR / f"child_coach_v{version}.json"
        assert snapshot_file.exists(), (
            f"Missing snapshot for version {version}: {snapshot_file}\n"
            f"Run: python -m pytest backend/tests/test_prompt_snapshots.py::test_generate_snapshots -s"
        )


@pytest.mark.generate_snapshots
def test_generate_snapshots():
    """
    Generate snapshot files for all prompt versions.
    Run with: pytest backend/tests/test_prompt_snapshots.py::test_generate_snapshots -s -m generate_snapshots
    """
    # Ensure snapshots directory exists
    SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    
    versions = list_prompt_versions("child_coach")
    
    for version in versions:
        prompt = get_prompt_version("child_coach", version=version)
        snapshot_file = SNAPSHOTS_DIR / f"child_coach_v{version}.json"
        
        # Write snapshot
        with open(snapshot_file, 'w', encoding='utf-8') as f:
            json.dump(prompt, f, indent=2, ensure_ascii=False)
        
        print(f"Generated snapshot: {snapshot_file}")


def test_prompt_file_naming_convention():
    """Test that prompt files follow naming convention: {prompt_id}_v{version}.json"""
    project_root = Path(__file__).parent.parent.parent
    prompts_dir = project_root / "prompts"
    
    for prompt_file in prompts_dir.glob("*.json"):
        filename = prompt_file.name
        
        # Should match pattern: {prompt_id}_v{version}.json
        parts = filename.replace(".json", "").split("_v")
        
        assert len(parts) == 2, (
            f"Prompt file {filename} doesn't follow naming convention: "
            f"Expected format: {{prompt_id}}_v{{version}}.json"
        )
        
        version_str = parts[1]
        assert version_str.isdigit(), (
            f"Version in {filename} must be a number, got: {version_str}"
        )


def test_prompt_structure():
    """Test that prompt files have required structure."""
    versions = list_prompt_versions("child_coach")
    
    for version in versions:
        prompt = get_prompt_version("child_coach", version=version)
        
        # Required fields
        assert "version" in prompt, f"Missing 'version' in v{version}"
        assert "prompt_id" in prompt, f"Missing 'prompt_id' in v{version}"
        assert "template" in prompt, f"Missing 'template' in v{version}"
        
        # Version should match
        assert prompt["version"] == version, (
            f"Version mismatch in v{version}: expected {version}, got {prompt['version']}"
        )

