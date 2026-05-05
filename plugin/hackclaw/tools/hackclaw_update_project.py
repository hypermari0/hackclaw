"""hackclaw_update_project tool.

Fills in description, repo URL, deploy URL on a DRAFT project. Used by the
Submitter after the Storyteller has produced the project page HTML.
"""

import os

from hackclaw.platforms.base import ProjectUpdates
from hackclaw.platforms.taikai import TaikaiPlatform
from hackclaw.tools._runtime import select_platform

NAME = "hackclaw_update_project"
DESCRIPTION = (
    "Update a DRAFT project on the hackathon platform with description HTML, "
    "repo URL, and deploy URL. Used by the Submitter."
)
INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "project_id": {"type": "string"},
        "description_html": {"type": "string"},
        "repo_url": {"type": "string"},
        "deploy_url": {"type": "string"},
    },
    "required": ["project_id", "description_html"],
}


async def run(
    project_id: str,
    description_html: str,
    repo_url: str | None = None,
    deploy_url: str | None = None,
) -> dict:
    # We don't have the hackathon URL here; we infer the platform from the
    # project_id's shape. TAIKAI project IDs are cuids (lowercase alphanumeric,
    # ~25 chars). Browser-platform IDs will look different in v0.3+.
    # For v0.2, default to TAIKAI when in doubt.
    if _looks_like_taikai_id(project_id):
        adapter = TaikaiPlatform()
    else:
        # No way to dispatch without the URL; surface the error so the squad
        # can pass the URL explicitly.
        raise ValueError(
            f"Cannot infer platform from project_id={project_id!r}. "
            "v0.2 only supports TAIKAI; v0.3 will require passing hackathon_url."
        )

    updates = ProjectUpdates(
        description_html=description_html,
        repo_url=repo_url,
        deploy_url=deploy_url,
    )
    await adapter.update_project(project_id, updates)
    return {"project_id": project_id, "state": "DRAFT", "updated": True}


def _looks_like_taikai_id(pid: str) -> bool:
    return bool(pid) and pid.islower() and pid.isalnum() and 20 <= len(pid) <= 30


def register(registry):
    registry.register(
        name=NAME,
        description=DESCRIPTION,
        input_schema=INPUT_SCHEMA,
        handler=run,
    )
