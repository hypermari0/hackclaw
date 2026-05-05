"""hackclaw_create_draft tool.

Creates a DRAFT project on the platform. Returns the project ID.
"""

from hackclaw.platforms.base import ProjectDraft
from hackclaw.tools._runtime import select_platform

NAME = "hackclaw_create_draft"
DESCRIPTION = (
    "Create a DRAFT project on the hackathon platform. Returns the platform "
    "project ID. Used by the Submitter."
)
INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "hackathon_url": {"type": "string"},
        "name": {"type": "string", "description": "Project name (3-80 chars)"},
        "teaser": {"type": "string", "description": "Short tagline (3-200 chars)"},
    },
    "required": ["hackathon_url", "name", "teaser"],
}


async def run(hackathon_url: str, name: str, teaser: str) -> dict:
    adapter, _kind = select_platform(hackathon_url)
    draft = ProjectDraft(name=name[:80], teaser=teaser[:200])
    project_id = await adapter.create_draft_project(hackathon_url, draft)
    return {"project_id": project_id, "state": "DRAFT"}


def register(registry):
    registry.register(
        name=NAME,
        description=DESCRIPTION,
        input_schema=INPUT_SCHEMA,
        handler=run,
    )
