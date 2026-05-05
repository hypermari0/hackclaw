# Instructions for Claude Code

You are picking up the HackClaw build. **HackClaw is a Hermes Agent plugin pack** that deploys a squad of AI agents to win hackathons end-to-end. There is no v0.1, no LangGraph, no standalone Python runner. We're going direct to the Hermes-native shape.

## Read these first

1. `README.md` — the project pitch
2. `docs/architecture.md` — the squad-as-skills design and how the orchestrator works
3. `docs/installing.md` — Hermes prerequisites
4. `skills/hackclaw/squad/SKILL.md` — the orchestrator skill (the entry point)

## Substrate

We are building against a Hermes Agent install at [hypermari0/hermes-agent](https://github.com/hypermari0/hermes-agent), a fork of [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) with minor customizations. Skill frontmatter and plugin manifest schema match upstream.

If anything in our scaffold doesn't load, **the upstream repo is the ground truth**, not these files. Inspect:
- Upstream skill examples in `~/.hermes/skills/` (built-in skills) for SKILL.md format
- Upstream plugin examples in `~/.hermes/plugins/` for plugin.yaml + tool registration
- `agent/` and `gateway/` source for ACP subagent spawn semantics

When our spec disagrees with the upstream Hermes source, fix the spec to match Hermes. Do not fork-modify Hermes itself.

## Target hackathon (the recursive demo)

**Hacklayer 4_1 MCP Edition** — internal LayerX hackathon. Build phase ends in ~24h.

- Challenge ID: `cmorgdlgm001hcz4xs9a50yxt`
- Project ID (already created as DRAFT): `cmosopzb3007xgbu2fl9d7t9t`
- Org slug: `layerx`
- Challenge slug: `hacklayer4-1-mcp-edition`
- Hackathon URL: `https://taikai.network/layerx/hackathons/hacklayer4-1-mcp-edition`

The recursive flex: HackClaw runs against Hacklayer 4_1 and submits its own project. The Submitter must update the **existing** project (`cmosopzb3007xgbu2fl9d7t9t`), not create a new one. Add an env var `HACKCLAW_TARGET_PROJECT_ID` and a check in the Submitter tool that, if set, updates instead of creates.

## Goal

By the time you're done:

1. `./install.sh` symlinks `skills/hackclaw/` into `~/.hermes/skills/` and `plugin/hackclaw/` into `~/.hermes/plugins/`
2. `hermes` boots cleanly, loads the HackClaw skills and tools without errors
3. `hermes mcp add taikai` works (or the equivalent, depending on Hermes's current MCP-add UX)
4. `/hackathon run https://taikai.network/layerx/hackathons/hacklayer4-1-mcp-edition` from inside Hermes drives the full pipeline
5. The Submitter pauses on a Hermes approval prompt before flipping to ACTIVE
6. After approval, the existing TAIKAI project flips to ACTIVE
7. The demo also works from Telegram (`hermes gateway` running, Telegram bot configured)

## Component status

### Skills (`skills/hackclaw/*/SKILL.md`)

Each role has a SKILL.md with frontmatter (`name`, `description`, allowed toolsets) and a body that's the system prompt. The orchestrator (`squad/SKILL.md`) drives the flow. **Verify frontmatter against your local Hermes — the keys may differ slightly from what we wrote.**

### Plugin (`plugin/hackclaw/`)

`plugin.yaml` declares the plugin. Six tool wrappers in `tools/` register HackClaw-specific tools with Hermes:

- `hackclaw_get_brief(hackathon_url)` 
- `hackclaw_list_submissions(hackathon_url)`
- `hackclaw_create_draft(hackathon_url, name, teaser)`
- `hackclaw_update_project(project_id, description_html, repo_url, deploy_url)`
- `hackclaw_submit(project_id)`
- `hackclaw_select_platform(hackathon_url)` returns "taikai" or "browser"

Each tool dispatches to a `HackathonPlatform` adapter in `platforms/`. The adapters are where actual API/MCP calls happen.

### Platforms (`plugin/hackclaw/platforms/`)

- `base.py`: the `HackathonPlatform` protocol
- `taikai.py`: routes through the TAIKAI MCP that Hermes has configured. **The user has the TAIKAI MCP available in his own Claude session and Hermes plugin authoring docs explain MCP-to-tool dispatch — verify against Hermes's actual MCP integration shape, not our spec, if they disagree.**
- `browser.py`: stub for v0.3+

## Priority order

### P0 — must work for the recursive demo

1. **Skills load cleanly.** `hermes` starts without complaining about HackClaw skill frontmatter.
2. **Plugin tools register.** `/tools` inside Hermes lists the six `hackclaw_*` tools.
3. **TAIKAI adapter via MCP.** `hackclaw_get_brief("https://taikai.network/layerx/hackathons/hacklayer4-1-mcp-edition")` returns the brief by routing through the TAIKAI MCP. If MCP routing has friction, fall back to direct GraphQL — both paths documented in the platform adapter.
4. **Squad orchestrator end-to-end.** `/hackathon run <url>` walks all six roles and produces a DRAFT update on the existing project.
5. **Approval prompt before publish.** Submitter does not call `hackclaw_submit` until the human confirms via the active gateway (CLI or Telegram).
6. **Recursive submit succeeds.** The DRAFT project at `cmosopzb3007xgbu2fl9d7t9t` flips to ACTIVE with HackClaw-generated content.

### P1 — makes the demo great

7. **Telegram gateway tested.** `hermes gateway` boots with Telegram configured. The full conversation in the README's "Telegram demo" section works end to end.
8. **Storyteller injects the recursive-flex narrative.** When it detects the Hacklayer 4_1 URL or project ID, it writes the "HackClaw submitted HackClaw" paragraph into the project page HTML.
9. **Live progress updates.** The squad skill posts progress messages back to the user via the active gateway every few minutes ("Strategist done, PM scoping..."). Don't make the user stare at silence.

### P2 — explicitly do NOT start until P0 is green

10. Browser platform implementation (Devpost, etc.)
11. Cost-aware model routing
12. Auto-recorded demo videos
13. Anything in the README roadmap

## Style rules (project owner's preferences, hard rules)

- **No em dashes anywhere.** Periods, commas, parentheses, or colons. Skill prompts already follow this; do not regress.
- Punchy, direct copy. Builder-to-builder voice.
- No filler.
- No AI-flavored phrases ("in today's fast-paced world").
- No emojis unless explicitly asked.

## Stack

- Hermes Agent (substrate)
- Python 3.11 for the plugin tool wrappers
- Markdown for skills
- TAIKAI MCP for the TAIKAI adapter
- Claude in Chrome MCP for the browser adapter (v0.3+)

## Time discipline

You have hours, not days. Build the spine end to end first. Polish second. **Do not start P2 work until the recursive submit succeeds.**

## What the project owner has

- Active TAIKAI session as `hypermario` with admin rights on the LayerX org
- Anthropic API key
- Working `hypermari0/hermes-agent` install
- Telegram bot token
- A TAIKAI MCP source already configured in his Claude session (the same one this scaffold should target)

If you need any of these to test, ask through the chat session he uses to drive you.

## Failure modes to expect

1. **Hermes ACP spawn semantics differ from spec.** The squad skill's "spawn this subagent" syntax in our spec is inferred from upstream docs. If it doesn't work, inspect a working built-in skill that uses ACP and copy its pattern.
2. **MCP-to-tool routing in plugins.** The TAIKAI adapter spec assumes Hermes can dispatch from a plugin tool to a configured MCP. Verify that pattern in upstream before going deep on the adapter; if it requires a different approach (e.g., direct MCP client in the plugin), adjust.
3. **TAIKAI GraphQL fallback may be needed.** Have it ready as a backup. Keep both paths in `platforms/taikai.py`, gated by an env var (`HACKCLAW_TAIKAI_VIA=mcp|graphql`, default `mcp`).
4. **Skill frontmatter keys.** Upstream Hermes uses `name`, `description`, possibly `metadata.toolsets`, `metadata.subagent_allowed`, etc. Our specs use these names but they may have shifted. Always check actual upstream skills first.

When in doubt, ground truth is upstream Hermes source, not this scaffold.
