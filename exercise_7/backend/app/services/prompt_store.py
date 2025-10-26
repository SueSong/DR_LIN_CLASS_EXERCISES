import asyncio
from typing import Any, Dict, List, Optional, Tuple
import random

from app.database import execute_raw_command, execute_raw_query, check_table_exists


PROMPT_SEED = {
    "agent/planner": [
        {
            "version": 1,
            "template": "System: You are a pragmatic planner. Inputs: {goal} {constraints}",
            "metadata": {"tags": ["plan-exec", "baseline"], "locale": "en"},
            "changelog": "initial version",
            "created_by": "seed",
        },
        {
            "version": 2,
            "template": "System: Plan tasks concisely with numbered steps. Inputs: {goal} {constraints}",
            "metadata": {"tags": ["plan-exec", "short"], "locale": "en"},
            "changelog": "shortened instructions",
            "created_by": "seed",
        },
    ]
}


async def ensure_schema() -> None:
    if not await check_table_exists("prompts"):
        await execute_raw_command(
            """
            CREATE TABLE IF NOT EXISTS prompts (
              id TEXT PRIMARY KEY,
              created_at TIMESTAMP DEFAULT now()
            );
            """
        )
    if not await check_table_exists("prompt_versions"):
        await execute_raw_command(
            """
            CREATE TABLE IF NOT EXISTS prompt_versions (
              id BIGSERIAL PRIMARY KEY,
              prompt_id TEXT REFERENCES prompts(id),
              version INT,
              template TEXT,
              metadata JSONB,
              changelog TEXT,
              created_by TEXT,
              created_at TIMESTAMP DEFAULT now(),
              UNIQUE(prompt_id, version)
            );
            """
        )
    if not await check_table_exists("prompt_deploys"):
        await execute_raw_command(
            """
            CREATE TABLE IF NOT EXISTS prompt_deploys (
              env TEXT,
              prompt_id TEXT,
              strategy TEXT,
              active_version INT,
              ab_alt_version INT,
              traffic_split INT,
              updated_at TIMESTAMP DEFAULT now(),
              PRIMARY KEY (env, prompt_id)
            );
            """
        )

    # seed minimal planner prompts if not present
    existing = await execute_raw_query(
        "SELECT COUNT(*) AS c FROM prompt_versions WHERE prompt_id = $1", "agent/planner"
    )
    count = (existing[0]["c"] if existing else 0) or 0
    if count == 0:
        await execute_raw_command("INSERT INTO prompts(id) VALUES($1) ON CONFLICT DO NOTHING", "agent/planner")
        for row in PROMPT_SEED["agent/planner"]:
            await execute_raw_command(
                """
                INSERT INTO prompt_versions(prompt_id, version, template, metadata, changelog, created_by)
                VALUES($1,$2,$3,$4::jsonb,$5,$6)
                ON CONFLICT (prompt_id, version) DO NOTHING
                """,
                "agent/planner",
                row["version"],
                row["template"],
                row["metadata"],
                row["changelog"],
                row["created_by"],
            )
        # default deploy fixed v1 for development
        await execute_raw_command(
            """
            INSERT INTO prompt_deploys(env, prompt_id, strategy, active_version, ab_alt_version, traffic_split)
            VALUES($1,$2,$3,$4,$5,$6)
            ON CONFLICT (env, prompt_id) DO NOTHING
            """,
            "development",
            "agent/planner",
            "fixed",
            1,
            None,
            0,
        )


async def list_versions(prompt_id: str) -> List[Dict[str, Any]]:
    await ensure_schema()
    rows = await execute_raw_query(
        """
        SELECT version, template, metadata, changelog, created_by, created_at
        FROM prompt_versions WHERE prompt_id=$1 ORDER BY version DESC
        """,
        prompt_id,
    )
    return rows


async def create_version(prompt_id: str, template: str, metadata: Dict[str, Any], changelog: str, created_by: str) -> Dict[str, Any]:
    await ensure_schema()
    await execute_raw_command("INSERT INTO prompts(id) VALUES($1) ON CONFLICT DO NOTHING", prompt_id)
    current = await execute_raw_query(
        "SELECT COALESCE(MAX(version),0) AS v FROM prompt_versions WHERE prompt_id=$1",
        prompt_id,
    )
    next_version = int((current[0]["v"] if current else 0) or 0) + 1
    await execute_raw_command(
        """
        INSERT INTO prompt_versions(prompt_id, version, template, metadata, changelog, created_by)
        VALUES($1,$2,$3,$4::jsonb,$5,$6)
        """,
        prompt_id,
        next_version,
        template,
        metadata,
        changelog,
        created_by,
    )
    return {"prompt_id": prompt_id, "version": next_version}


async def set_deploy(env: str, prompt_id: str, strategy: str, active_version: int, ab_alt_version: Optional[int], traffic_split: Optional[int]) -> Dict[str, Any]:
    await ensure_schema()
    await execute_raw_command(
        """
        INSERT INTO prompt_deploys(env, prompt_id, strategy, active_version, ab_alt_version, traffic_split)
        VALUES($1,$2,$3,$4,$5,$6)
        ON CONFLICT (env, prompt_id)
        DO UPDATE SET strategy=EXCLUDED.strategy,
                      active_version=EXCLUDED.active_version,
                      ab_alt_version=EXCLUDED.ab_alt_version,
                      traffic_split=EXCLUDED.traffic_split,
                      updated_at=now()
        """,
        env,
        prompt_id,
        strategy,
        active_version,
        ab_alt_version,
        traffic_split or 0,
    )
    return {"env": env, "prompt_id": prompt_id, "strategy": strategy}


async def resolve_prompt(prompt_uri: str, env: str, user_key: Optional[str] = None) -> Dict[str, Any]:
    await ensure_schema()
    prompt_id = prompt_uri.replace("prompt://", "")
    deploy = await execute_raw_query(
        "SELECT strategy, active_version, ab_alt_version, traffic_split FROM prompt_deploys WHERE env=$1 AND prompt_id=$2",
        env,
        prompt_id,
    )
    if not deploy:
        # fallback to latest version
        versions = await list_versions(prompt_id)
        if not versions:
            return {"prompt_id": prompt_id, "version": 1, "template": "", "metadata": {}}
        version = int(versions[0]["version"])
    else:
        d = deploy[0]
        if d["strategy"] == "ab" and d.get("ab_alt_version") and int(d.get("traffic_split") or 0) > 0:
            # deterministic split
            key = user_key or "default"
            h = abs(hash(f"{prompt_id}:{env}:{key}")) % 100
            version = d["ab_alt_version"] if h < int(d["traffic_split"]) else d["active_version"]
        else:
            version = d["active_version"]

    row = await execute_raw_query(
        "SELECT version, template, metadata FROM prompt_versions WHERE prompt_id=$1 AND version=$2",
        prompt_id,
        version,
    )
    if not row:
        return {"prompt_id": prompt_id, "version": version, "template": "", "metadata": {}}
    r = row[0]
    return {"prompt_id": prompt_id, "version": r["version"], "template": r["template"], "metadata": r["metadata"]}


