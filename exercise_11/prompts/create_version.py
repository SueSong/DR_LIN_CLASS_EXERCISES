#!/usr/bin/env python3
"""
Helper script to create a new prompt version.
Usage: python prompts/create_version.py
"""

import json
import sys
from pathlib import Path
from datetime import datetime

PROMPTS_DIR = Path(__file__).parent


def get_latest_version(prompt_id: str = "child_coach") -> int:
    """Get the latest version number for a prompt."""
    versions = []
    for file in PROMPTS_DIR.glob(f"{prompt_id}_v*.json"):
        try:
            version_part = file.stem.split("_v")[-1]
            version = int(version_part)
            versions.append(version)
        except (ValueError, IndexError):
            continue
    
    return max(versions) if versions else 0


def create_new_version(prompt_id: str = "child_coach", changelog: str = None) -> Path:
    """Create a new version of a prompt."""
    latest = get_latest_version(prompt_id)
    new_version = latest + 1
    
    # Load latest version as template
    latest_file = PROMPTS_DIR / f"{prompt_id}_v{latest}.json"
    if latest_file.exists():
        with open(latest_file, 'r', encoding='utf-8') as f:
            template = json.load(f)
    else:
        # Create from scratch
        template = {
            "version": new_version,
            "prompt_id": prompt_id,
            "name": "Child Growth Assistant - Parent Coach",
            "description": "Prompt template for generating parenting advice based on RAG retrieval",
            "template": "",
            "variables": ["user_question", "retrieved_knowledge"],
            "metadata": {
                "created_at": datetime.utcnow().isoformat() + "Z",
                "created_by": "user",
                "tags": ["parenting", "coach", "advice"]
            },
            "changelog": ""
        }
    
    # Create new version
    new_file = PROMPTS_DIR / f"{prompt_id}_v{new_version}.json"
    template["version"] = new_version
    template["metadata"]["created_at"] = datetime.utcnow().isoformat() + "Z"
    template["changelog"] = changelog or f"v{new_version} - Updated prompt template"
    
    with open(new_file, 'w', encoding='utf-8') as f:
        json.dump(template, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Created new prompt version: {new_file}")
    print(f"   Version: v{new_version}")
    print(f"   Based on: v{latest}" if latest > 0 else "   (new prompt)")
    
    return new_file


if __name__ == "__main__":
    prompt_id = sys.argv[1] if len(sys.argv) > 1 else "child_coach"
    changelog = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        new_file = create_new_version(prompt_id, changelog)
        print(f"\n📝 Next steps:")
        print(f"1. Edit {new_file} with your changes")
        print(f"2. Update prompts/CHANGELOG.md")
        print(f"3. Generate snapshot: pytest backend/tests/test_prompt_snapshots.py::test_generate_snapshots -s -m generate_snapshots")
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)

