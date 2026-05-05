"""Sanity tests for the platform protocol and TAIKAI URL parsing."""

import sys
from pathlib import Path

# Resolve the plugin package on sys.path for tests to find it
sys.path.insert(0, str(Path(__file__).parent.parent / "plugin"))

import pytest


def test_taikai_url_parser():
    from hackclaw.platforms.taikai import parse_taikai_url

    org, slug = parse_taikai_url(
        "https://taikai.network/layerx/hackathons/hacklayer4-1-mcp-edition"
    )
    assert org == "layerx"
    assert slug == "hacklayer4-1-mcp-edition"


def test_taikai_url_parser_with_lang_prefix():
    from hackclaw.platforms.taikai import parse_taikai_url

    org, slug = parse_taikai_url(
        "https://taikai.network/en/layerx/hackathons/hacklayer4-1-mcp-edition"
    )
    assert org == "layerx"
    assert slug == "hacklayer4-1-mcp-edition"


def test_taikai_url_parser_rejects_non_taikai():
    from hackclaw.platforms.taikai import parse_taikai_url

    with pytest.raises(ValueError):
        parse_taikai_url("https://devpost.com/hackathons/foo")


def test_select_platform_kind_taikai():
    from hackclaw.tools._runtime import select_platform_kind

    assert select_platform_kind(
        "https://taikai.network/layerx/hackathons/test"
    ) == "taikai"


def test_select_platform_kind_other():
    from hackclaw.tools._runtime import select_platform_kind

    assert select_platform_kind("https://devpost.com/hackathons/foo") == "browser"


def test_brief_roundtrip():
    from hackclaw.platforms.base import Brief

    b = Brief(
        title="Hacklayer 4_1 MCP Edition",
        short_description="Build Where the Agents Live",
        raw_url="https://taikai.network/layerx/hackathons/hacklayer4-1-mcp-edition",
    )
    blob = b.model_dump_json()
    restored = Brief.model_validate_json(blob)
    assert restored.title == "Hacklayer 4_1 MCP Edition"


def test_project_draft_validation():
    from hackclaw.platforms.base import ProjectDraft

    d = ProjectDraft(name="HackClaw", teaser="AI squads that claw their way to wins.")
    assert d.name == "HackClaw"
