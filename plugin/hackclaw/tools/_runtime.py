"""Shared runtime helpers for HackClaw tools.

Every tool dispatches to a HackathonPlatform adapter. The selection is
URL-based: TAIKAI URLs go to TaikaiPlatform; everything else (eventually) to
BrowserPlatform.
"""

from hackclaw.platforms.base import HackathonPlatform
from hackclaw.platforms.browser import BrowserPlatform
from hackclaw.platforms.taikai import TaikaiPlatform


def select_platform(hackathon_url: str) -> tuple[HackathonPlatform, str]:
    """Return (adapter, kind) for a hackathon URL."""
    if "taikai.network" in hackathon_url:
        return TaikaiPlatform(), "taikai"
    return BrowserPlatform(), "browser"


def select_platform_kind(hackathon_url: str) -> str:
    """Return just the kind without instantiating the adapter (lighter)."""
    if "taikai.network" in hackathon_url:
        return "taikai"
    return "browser"
