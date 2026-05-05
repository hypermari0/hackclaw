"""Plugin registration and tool-handler wiring tests.

Mirrors the shape Hermes uses to load plugins: it imports the package and
calls `register(ctx)`, where `ctx.register_tool(name, schema, handler)` is the
recording sink. We verify all six tool names show up with valid schemas.
"""

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "plugin"))


class _FakeCtx:
    def __init__(self) -> None:
        self.tools: list[tuple[str, dict, object]] = []

    def register_tool(self, name, schema, handler):
        self.tools.append((name, schema, handler))


def test_register_wires_all_six_tools():
    import hackclaw

    ctx = _FakeCtx()
    hackclaw.register(ctx)

    names = [t[0] for t in ctx.tools]
    assert names == [
        "hackclaw_select_platform",
        "hackclaw_get_brief",
        "hackclaw_list_submissions",
        "hackclaw_create_draft",
        "hackclaw_update_project",
        "hackclaw_submit",
    ]

    for name, schema, handler in ctx.tools:
        assert schema["name"] == name
        assert "description" in schema
        assert "parameters" in schema
        assert callable(handler)


def test_select_platform_handler_returns_json_string():
    from hackclaw.tools.hackclaw_select_platform import handle

    out = handle({"hackathon_url": "https://taikai.network/layerx/hackathons/foo"})
    assert isinstance(out, str)
    assert json.loads(out) == {"platform": "taikai"}


def test_create_draft_short_circuits_on_target_project_id(monkeypatch):
    from hackclaw.tools.hackclaw_create_draft import handle

    monkeypatch.setenv("HACKCLAW_TARGET_PROJECT_ID", "cmosopzb3007xgbu2fl9d7t9t")

    out = handle({
        "hackathon_url": "https://taikai.network/layerx/hackathons/hacklayer4-1-mcp-edition",
        "name": "HackClaw",
        "teaser": "AI squads that claw their way to wins.",
    })
    parsed = json.loads(out)
    assert parsed["project_id"] == "cmosopzb3007xgbu2fl9d7t9t"
    assert parsed["state"] == "DRAFT"
    assert parsed["reused_existing"] is True
    assert parsed["source"] == "HACKCLAW_TARGET_PROJECT_ID"


def test_create_draft_does_not_short_circuit_without_env(monkeypatch):
    """Without the env var, it must call into the platform adapter (not return a stub).

    We don't actually want to hit TAIKAI in tests, so we just confirm the
    short-circuit branch is gated correctly by checking it tries to dispatch.
    """
    from hackclaw.tools.hackclaw_create_draft import handle

    monkeypatch.delenv("HACKCLAW_TARGET_PROJECT_ID", raising=False)
    # MCP route by default. Without a real Hermes runtime, dispatch raises.
    monkeypatch.setenv("HACKCLAW_TAIKAI_VIA", "mcp")

    try:
        handle({
            "hackathon_url": "https://taikai.network/layerx/hackathons/hacklayer4-1-mcp-edition",
            "name": "HackClaw",
            "teaser": "AI squads that claw their way to wins.",
        })
    except Exception as e:
        # We expect a RuntimeError from the MCP-dispatch probe in this
        # non-Hermes environment. Anything else is a regression.
        assert "TAIKAI MCP route is unreachable" in str(e) or "Hermes" in str(e)
    else:
        raise AssertionError("Expected MCP dispatch to fail outside Hermes")
