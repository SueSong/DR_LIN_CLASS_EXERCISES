"""
Prompt Loader Module
Loads versioned prompt templates from prompts/ directory.
"""

import json
import os
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

# Cache for loaded prompts
_PROMPT_CACHE: Dict[str, Dict] = {}


def get_prompt_version(prompt_id: str = "child_coach", version: int = 1) -> Dict:
    """
    Load a specific version of a prompt.
    
    Args:
        prompt_id: Prompt identifier (default: "child_coach")
        version: Version number (default: 1)
        
    Returns:
        Dictionary containing prompt data
        
    Raises:
        FileNotFoundError: If prompt file doesn't exist
        ValueError: If prompt file is invalid
    """
    cache_key = f"{prompt_id}_v{version}"
    
    # Check cache first
    if cache_key in _PROMPT_CACHE:
        return _PROMPT_CACHE[cache_key]
    
    # Find prompt file
    project_root = Path(__file__).parent.parent.parent
    prompt_file = project_root / "prompts" / f"{prompt_id}_v{version}.json"
    
    if not prompt_file.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_file}")
    
    # Load and validate
    try:
        with open(prompt_file, 'r', encoding='utf-8') as f:
            prompt_data = json.load(f)
        
        # Validate structure
        required_fields = ["version", "prompt_id", "template"]
        for field in required_fields:
            if field not in prompt_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Verify version matches
        if prompt_data.get("version") != version:
            raise ValueError(
                f"Version mismatch: file contains v{prompt_data.get('version')}, "
                f"requested v{version}"
            )
        
        # Cache it
        _PROMPT_CACHE[cache_key] = prompt_data
        
        return prompt_data
    
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in prompt file: {e}")


def get_latest_prompt(prompt_id: str = "child_coach") -> Dict:
    """
    Get the latest version of a prompt.
    
    Args:
        prompt_id: Prompt identifier
        
    Returns:
        Latest prompt version
    """
    project_root = Path(__file__).parent.parent.parent
    prompts_dir = project_root / "prompts"
    
    # Find all versions
    pattern = f"{prompt_id}_v*.json"
    prompt_files = list(prompts_dir.glob(pattern))
    
    if not prompt_files:
        raise FileNotFoundError(f"No prompt files found for {prompt_id}")
    
    # Extract versions and get latest
    versions = []
    for file in prompt_files:
        # Extract version from filename: child_coach_v2.json -> 2
        try:
            version_part = file.stem.split("_v")[-1]
            version = int(version_part)
            versions.append((version, file))
        except (ValueError, IndexError):
            continue
    
    if not versions:
        raise ValueError(f"Could not parse versions from prompt files")
    
    # Get latest version
    latest_version, latest_file = max(versions, key=lambda x: x[0])
    
    return get_prompt_version(prompt_id, latest_version)


def render_prompt(template: str, **kwargs) -> str:
    """
    Render a prompt template with variables.
    
    Args:
        template: Prompt template with {{variable}} placeholders
        **kwargs: Variables to substitute
        
    Returns:
        Rendered prompt string
    """
    result = template
    
    for key, value in kwargs.items():
        placeholder = f"{{{{ {key} }}}}"
        if placeholder in result:
            result = result.replace(placeholder, str(value))
    
    # Warn about unused variables in template
    import re
    unused = re.findall(r'\{\{\s*(\w+)\s*\}\}', result)
    if unused:
        print(f"Warning: Unused template variables: {unused}")
    
    return result


def list_prompt_versions(prompt_id: str = "child_coach") -> list:
    """
    List all available versions of a prompt.
    
    Args:
        prompt_id: Prompt identifier
        
    Returns:
        List of version numbers
    """
    project_root = Path(__file__).parent.parent.parent
    prompts_dir = project_root / "prompts"
    
    pattern = f"{prompt_id}_v*.json"
    prompt_files = list(prompts_dir.glob(pattern))
    
    versions = []
    for file in prompt_files:
        try:
            version_part = file.stem.split("_v")[-1]
            version = int(version_part)
            versions.append(version)
        except (ValueError, IndexError):
            continue
    
    return sorted(versions)

