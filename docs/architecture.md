# Architecture

HackClaw is a Hermes Agent plugin pack. The codebase has three parts:

```
hackclaw/
├── skills/hackclaw/    # the squad as Hermes skills (markdown)
├── plugin/hackclaw/    # the platform tools (Python)
└── install.sh          # symlinks both into ~/.hermes/
```

That's the whole thing. No orchestration code, no CLI, no agent runtime. Hermes already has all of that.

## Why six skills

Three roles collapse: a Dev-who-writes-copy writes worse copy. Twelve roles thrash on coordination. Six is the sweet spot.

| Skill | Reads from | Writes to |
|-------|-----------|-----------|
| Strategist | brief, existing submissions | chosen angle |
| PM | chosen angle, time budget | build plan |
| Dev | build plan | repo URL, deploy URL |
| Designer | chosen angle | brand palette, hero image |
| Storyteller | chosen angle, plan, build artifacts | project page HTML, README, demo script |
| Submitter | everything above | submission state, project URL |

No skill-to-skill dialogue. State flows through Hermes session memory. Each skill reads what it needs, decides, writes its output, returns control to the orchestrator.

## The orchestrator

`skills/hackclaw/squad/SKILL.md` is the entry point. When the user runs `/hackathon run <url>` (or messages "win this hackathon for me" on Telegram), Hermes loads `squad` and the agent executes the flow it describes:

1. Call `hackclaw_select_platform(url)` to pick TAIKAI vs browser
2. Call `hackclaw_get_brief(url)` and `hackclaw_list_submissions(url)`
3. Spawn `strategist` as a subagent via Hermes ACP, passing the brief
4. Spawn `pm` with the strategist's output
5. Spawn `dev` with the plan (Dev itself delegates to Hermes's `claude-code` subagent for the actual coding)
6. Parallel-spawn `designer` and `storyteller` once Dev returns a deploy URL
7. Spawn `submitter` with everything assembled, which calls `hackclaw_create_draft` and `hackclaw_update_project`
8. Issue an approval prompt to the user via the active gateway
9. On approval, call `hackclaw_submit(project_id)` and report back

The orchestrator is markdown. Hermes does the rest.

## The plugin

`plugin/hackclaw/__init__.py` exposes `register(ctx)`. Hermes calls it once at startup; we wire each tool with `ctx.register_tool(name, schema, handler)`. Six tools register:

| Tool | Job |
|------|-----|
| `hackclaw_select_platform` | Pick the right adapter for a hackathon URL |
| `hackclaw_get_brief` | Normalize a hackathon brief into a structured shape |
| `hackclaw_list_submissions` | Scout existing submissions |
| `hackclaw_create_draft` | Create a draft project on the platform |
| `hackclaw_update_project` | Fill in description, repo, deploy URL |
| `hackclaw_submit` | Flip the project to ACTIVE (gated by approval) |

Each tool dispatches to a `HackathonPlatform` adapter under `plugin/hackclaw/platforms/`.

## Platform adapters

```
HackathonPlatform (protocol)
├── TaikaiPlatform       MVP, routes through TAIKAI MCP
└── BrowserPlatform      stub for v0.3+
```

The TAIKAI adapter has two routes:

- **MCP route** (default): the plugin tool dispatches the call to the TAIKAI MCP that Hermes has configured. Cleanest path. No API auth duplication.
- **GraphQL route** (fallback): the plugin tool calls TAIKAI's GraphQL endpoint directly with `TAIKAI_TOKEN`. Used when the MCP route isn't available.

Toggle with `HACKCLAW_TAIKAI_VIA=mcp|graphql` (default `mcp`).

The browser adapter is reserved for v0.3+. It will use Claude in Chrome MCP to drive Devpost, ETHGlobal, Encode, Dorahacks, and any platform with a web form.

## State

Hermes session memory holds everything that flows between roles. We do not maintain a parallel state model. When a subagent returns, its structured output (whatever it produced as its final response) becomes part of the parent agent's context for the next step.

This is one of the reasons Hermes was the right substrate. Sharing structured data across agents is exactly what session memory + ACP subagent return values do.

## Kill-switch

The Submitter never auto-publishes. After it has created/updated the draft and filled the description, it returns control to the orchestrator with a message: *"Submission ready as DRAFT. Reply 'ship it' to publish."* Hermes routes this to whichever gateway is active (CLI, Telegram, etc.). The user replies. Only then does the orchestrator call `hackclaw_submit`.

This pattern gets us a built-in safety rail without any custom kill-switch code. Hermes already does approval prompts.

## What we deliberately don't build

- An agent loop. Hermes has one.
- Memory. Hermes has it.
- Tool calling. Hermes has it.
- Messaging gateways (Telegram, Discord, Slack, voice). Hermes has them.
- Cron scheduling. Hermes has it.
- Multi-provider model routing. Hermes has it (`hermes model`).
- A web dashboard. Hermes has one.
- Skill self-improvement. Hermes has the curator.

What we build: the squad shape and the platform adapters. That's it.

## What carries upstream

If something HackClaw learns is worth pushing upstream to Hermes itself, we send a PR to NousResearch/hermes-agent. Specifically:

- The hackathon-platform pattern (a generic "platform protocol + plugin tools" template) might be useful beyond hackathons. PRs welcome from anyone who finds it useful.
- Bug fixes or improvements to ACP subagent semantics that we discover while building this.

## File map

```
skills/hackclaw/
├── squad/
│   ├── SKILL.md              # orchestrator
│   └── references/
│       └── flow.md           # the squad pipeline diagram
├── strategist/SKILL.md
├── pm/SKILL.md
├── dev/SKILL.md
├── designer/SKILL.md
├── storyteller/SKILL.md
└── submitter/SKILL.md

plugin/hackclaw/
├── plugin.yaml               # plugin manifest
├── __init__.py               # register(ctx) entry point
├── tools/
│   ├── __init__.py
│   ├── _runtime.py           # async-to-sync bridge + adapter selection
│   ├── hackclaw_select_platform.py
│   ├── hackclaw_get_brief.py
│   ├── hackclaw_list_submissions.py
│   ├── hackclaw_create_draft.py
│   ├── hackclaw_update_project.py
│   └── hackclaw_submit.py
└── platforms/
    ├── __init__.py
    ├── base.py               # HackathonPlatform protocol
    ├── taikai.py             # MCP + GraphQL routes
    └── browser.py            # stub
```
