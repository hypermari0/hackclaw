"""hackclaw_submit tool.

Flips a DRAFT project to ACTIVE on the hackathon platform. Called by the
orchestrator AFTER the user has approved the submission via a Hermes approval
prompt.

Never call this from a subagent. The Submitter prepares the DRAFT; the
orchestrator handles the approval gate; this tool publishes.
"""

from hackclaw.platforms.taikai import TaikaiPlatform

NAME = "hackclaw_submit"
DESCRIPTION = (
    "Flip a DRAFT project to ACTIVE on the hackathon platform. Should only "
    "be called by the orchestrator AFTER explicit user approval. Returns "
    "the new state and the public URL if the platform exposes one."
)
INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "project_id": {"type": "string"},
    },
    "required": ["project_id"],
}


async def run(project_id: str) -> dict:
    if _looks_like_taikai_id(project_id):
        adapter = TaikaiPlatform()
    else:
        raise ValueError(
            f"Cannot infer platform from project_id={project_id!r}. "
            "v0.2 only supports TAIKAI."
        )

    result = await adapter.submit(project_id)
    return result.model_dump(mode="json")


def _looks_like_taikai_id(pid: str) -> bool:
    return bool(pid) and pid.islower() and pid.isalnum() and 20 <= len(pid) <= 30


def register(registry):
    registry.register(
        name=NAME,
        description=DESCRIPTION,
        input_schema=INPUT_SCHEMA,
        handler=run,
    )
