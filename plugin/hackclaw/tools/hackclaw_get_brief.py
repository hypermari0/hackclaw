"""hackclaw_get_brief tool.

Loads and normalizes a hackathon brief from the platform.
"""

from hackclaw.tools._runtime import select_platform

NAME = "hackclaw_get_brief"
DESCRIPTION = (
    "Load and normalize a hackathon brief from the platform. Returns title, "
    "short_description, full_description, theme_tags, timeline, prizes, "
    "rules. Used by the Strategist to understand what to build."
)
INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "hackathon_url": {"type": "string"},
    },
    "required": ["hackathon_url"],
}


async def run(hackathon_url: str) -> dict:
    adapter, _kind = select_platform(hackathon_url)
    brief = await adapter.get_brief(hackathon_url)
    return brief.model_dump(mode="json")


def register(registry):
    registry.register(
        name=NAME,
        description=DESCRIPTION,
        input_schema=INPUT_SCHEMA,
        handler=run,
    )
