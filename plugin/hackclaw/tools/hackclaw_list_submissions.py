"""hackclaw_list_submissions tool.

Returns the existing submissions for a hackathon. Used by the Strategist to
spot crowded angles and find a differentiation lane.
"""

from hackclaw.tools._runtime import select_platform

NAME = "hackclaw_list_submissions"
DESCRIPTION = (
    "List existing submissions for a hackathon. Returns name, teaser, and "
    "author for each. Used by the Strategist to find an under-served angle."
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
    submissions = await adapter.list_existing_submissions(hackathon_url)
    return {"submissions": [s.model_dump(mode="json") for s in submissions]}


def register(registry):
    registry.register(
        name=NAME,
        description=DESCRIPTION,
        input_schema=INPUT_SCHEMA,
        handler=run,
    )
