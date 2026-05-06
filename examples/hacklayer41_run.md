# Hacklayer 4_1 MCP Edition — the recursive demo

This is the demo we're driving toward for the hackathon submission. It runs from any Hermes interface (CLI, Telegram, Discord). The CLI version is the safe path; the Telegram version is the showpiece.

## CLI version (safe path)

```
$ hermes
Hermes v2026.4.x ready.

> /hackathon run https://taikai.network/layerx/hackathons/hacklayer4-1-mcp-edition

[Squad] Brief loaded. 4 existing submissions.

[Squad] Strategist suggests: A pluggable hackathon-platform protocol with
        TAIKAI as the first adapter, demonstrated by the squad submitting
        itself to this hackathon. Approve, refine, or override?

> approve

[Squad] PM scoped 3 features. Dev starting build.
[Squad] (5 min) Dev: scaffold + landing page committed.
[Squad] (12 min) Dev: TAIKAI adapter + submission flow committed.
[Squad] (18 min) Dev: deployed. https://hackclaw-run-xxx.vercel.app
[Squad] Brand set. Project page drafted.
[Squad] Submission ready as DRAFT.
        Project: https://taikai.network/layerx/hackathons/hacklayer4-1-mcp-edition/projects/cmosopzb3007xgbu2fl9d7t9t
        Reply 'ship it' to publish, or describe changes.

> ship it

[Squad] Submitted. ACTIVE on TAIKAI as of 14:32 WEST.

[Run summary]
  Angle:           A pluggable hackathon-platform protocol...
  Features:        scaffold, TAIKAI adapter, submission flow
  Repo:            https://github.com/hypermario/hackclaw-run-xxx
  Deploy:          https://hackclaw-run-xxx.vercel.app
  Project:         (the existing Hacklayer 4_1 project, now ACTIVE)
  Wall-clock:      24 minutes
```

## Telegram version (showpiece)

```
You (Telegram, at lunch):  Win Hacklayer 4_1 for me.

Hermes:  On it. Loading the brief.

Hermes:  Brief loaded. 4 existing submissions. Strategist suggests
         "A pluggable hackathon-platform protocol with TAIKAI as the
         first adapter, demonstrated by the squad submitting itself to
         this hackathon." Approve, refine, or override?

You:  Approve.

Hermes:  PM scoped 3 features. Dev starting build.

[5 min later]

Hermes:  Dev: scaffold + landing page committed.

[7 min later]

Hermes:  Dev: TAIKAI adapter + submission flow committed.

[6 min later]

Hermes:  Dev: deployed. https://hackclaw-run-xxx.vercel.app
         Brand set. Project page drafted.

         Submission ready as DRAFT.
         Project: <link>  Repo: <link>  Deploy: <link>
         Reply 'ship it' to publish.

You:  ship it

Hermes:  Submitted. ACTIVE on TAIKAI as of 14:32 WEST.
```

That's the full demo. No CLI, no dashboard, no terminal. Just a thread.

## Setup before the demo

Pre-flight checklist:

- [ ] Hermes is running (`hermes` for CLI, `hermes gateway` for Telegram)
- [ ] HackClaw is installed (`./install.sh` ran cleanly)
- [ ] HackClaw shows up in `/skills` and `/tools` inside Hermes
- [ ] TAIKAI MCP is configured (`hermes mcp add taikai`) OR `HACKCLAW_TAIKAI_VIA=graphql` with `TAIKAI_TOKEN` set
- [ ] `HACKCLAW_TARGET_PROJECT_ID=cmosopzb3007xgbu2fl9d7t9t` is set in the Hermes process environment
- [ ] `GITHUB_TOKEN` and `VERCEL_TOKEN` are set (Dev role needs them)
- [ ] If demoing on Telegram: bot token configured, you've messaged the bot at least once to verify routing
- [ ] Approval shortcut tested: pause the run, type "ship it", confirm publish path

## What can go wrong (and the recovery plan for each)

| Failure | Mitigation |
|---------|------------|
| Hermes ACP subagent spawn errors | Inspect upstream Hermes built-in skills for working ACP examples; copy their pattern |
| TAIKAI MCP route fails | Set `HACKCLAW_TAIKAI_VIA=graphql` and re-run |
| Dev's devstral subagent hangs | Cancel, reduce the build plan to a single static landing page, retry |
| Vercel deploy errors | Have a pre-deployed fallback URL ready as a "what would have shipped" reference |
| Telegram routing flakes during demo | Drop to CLI; same skills, same plugin, same recursive flex |
