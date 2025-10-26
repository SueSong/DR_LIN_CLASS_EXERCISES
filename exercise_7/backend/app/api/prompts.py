from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional

from app.services.prompt_store import list_versions, create_version, set_deploy, resolve_prompt


router = APIRouter(prefix="/api/prompts", tags=["Prompts"])


@router.get("/{prompt_id:path}/versions")
async def get_versions(prompt_id: str):
    return {"prompt_id": prompt_id, "versions": await list_versions(prompt_id)}


@router.post("/{prompt_id:path}")
async def create_prompt_version(prompt_id: str, body: Dict[str, Any]):
    template = body.get("template")
    metadata = body.get("metadata", {})
    changelog = body.get("changelog", "")
    created_by = body.get("created_by", "user")
    if not template:
        raise HTTPException(status_code=400, detail="template is required")
    return await create_version(prompt_id, template, metadata, changelog, created_by)


@router.post("/{prompt_id:path}/deploy")
async def deploy_prompt(prompt_id: str, body: Dict[str, Any]):
    env = body.get("env", "development")
    strategy = body.get("strategy", "fixed")
    active_version = body.get("active_version")
    ab_alt_version = body.get("ab_alt_version")
    traffic_split = body.get("traffic_split", 0)
    if not active_version and strategy == "fixed":
        raise HTTPException(status_code=400, detail="active_version is required for fixed strategy")
    return await set_deploy(env, prompt_id, strategy, int(active_version or 1), ab_alt_version, int(traffic_split or 0))


@router.get("/resolve")
async def resolve(prompt: str, env: str = "development", user_key: Optional[str] = None):
    return await resolve_prompt(prompt, env, user_key)


