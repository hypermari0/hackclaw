"""hackclaw_select_platform tool.

Returns "taikai" or "browser" for a given hackathon URL. The squad calls this
first to know which adapter is in play.
"""

from hackclaw.tools._runtime import select_platform_kind

NAME = "hackclaw_select_platform"
DESCRIPTION = (
    "Pick the right adapter for a hackathon URL. Returns 'taikai' for "
    "TAIKAI hackathons or 'browser' for everything else (handled via "
    "Claude in Chrome MCP in v0.3+)."
)
INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "hackathon_url": {
            "type": "string",
            "description": "The full URL of the hackathon (e.g. https://taikai.network/<org>/hackathons/<slug>)",
        },
    },
    "required": ["hackathon_url"],
}


async def run(hackathon_url: str) -> dict:
    kind = select_platform_kind(hackathon_url)
    return {"platform": kind}


def register(registry):
    """Hermes plugin registration entry point.

    The exact registry API depends on the Hermes plugin API version. Common
    shapes are:
        registry.register(name, description, schema, callable)
        registry.add_tool({...})
    Adjust to match the Hermes version being targeted.
    """
    registry.register(
        name=NAME,
        description=DESCRIPTION,
        input_schema=INPUT_SCHEMA,
        handler=run,
    )
