# HackClaw

> AI squads that claw their way to hackathon wins.

**HackClaw** is a [Hermes Agent](https://github.com/hypermari0/hermes-agent) plugin pack that deploys a squad of AI agents to participate in hackathons end-to-end. From reading the brief to submitting the final project, the squad handles the full pipeline.

You message your Hermes agent on Telegram with "win this hackathon for me." Twenty minutes later you get a reply with the deploy URL, the repo, the project page, and a "ship it?" prompt. That's the whole interface.

## Why a Hermes plugin

Most agent frameworks reinvent the agent loop, the tool calling layer, the memory system, and the messaging gateway. We did not. Hermes already does all of that, and does it well.

What HackClaw adds:

- A **squad of six hackathon-shaped skills** (Strategist, PM, Dev, Designer, Storyteller, Submitter)
- **Pluggable hackathon-platform adapters** as Hermes tools (TAIKAI native via MCP, browser fallback for everything else)
- **An orchestrator skill** that drives the full pipeline, brief to submission, with a built-in approval prompt before publishing

Everything else (Telegram, Discord, Slack, voice, memory across runs, multi-provider model routing, scheduling, session persistence) you get from Hermes for free.

Credit and license to upstream:

- Upstream agent core: [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent), MIT
- Personal fork it's developed against: [hypermari0/hermes-agent](https://github.com/hypermari0/hermes-agent), MIT
- HackClaw: this repo, MIT

## The squad

| Agent | Job |
|-------|-----|
| **Strategist** | Reads the brief, scouts existing submissions, picks the angle most likely to win |
| **PM** | Scopes the MVP, enforces the time budget, kills scope creep |
| **Dev** | Writes the code and deploys it (delegates to Hermes's bundled `claude-code` subagent) |
| **Designer** | Brand, landing page, project page hero |
| **Storyteller** | Demo script, README, project page copy |
| **Submitter** | Records the demo, fills forms, hits submit |

Each role is a Hermes skill. The orchestrator (`squad`) skill spawns them as subagents via Hermes ACP. No god-agents. No multi-agent dialogue. State flows through Hermes session memory.

## Works on any hackathon platform

A pluggable platform adapter handles the integration:

- **TAIKAI** native via the TAIKAI MCP. Fast, structured, reliable.
- **Everywhere else** browser automation via Claude in Chrome MCP. Works on Devpost, ETHGlobal, Encode, Dorahacks, and any platform with a web form.

Structured MCP first, browser as fallback. Adding a new platform means implementing a five-method protocol.

## Install

Prerequisites: a working Hermes Agent install. If you don't have one, see [docs/installing.md](docs/installing.md) for the 5-minute path.

```bash
# Clone HackClaw and run the installer
git clone https://github.com/hypermario/hackclaw.git
cd hackclaw
./install.sh

# Configure the TAIKAI MCP source (if you'll target TAIKAI)
hermes mcp add taikai

# Start Hermes (CLI, or hermes gateway for Telegram + others)
hermes
```

Inside Hermes:

```
> /hackathon run https://taikai.network/<org>/hackathons/<slug>
```

## The Telegram demo

```
You (Telegram, at lunch):  Win Hacklayer 4_1 for me.

Hermes:  On it. Loading the brief.

Hermes:  Brief loaded. 4 existing submissions. Strategist suggests
         <angle>. Approve, refine, or override?

You:  Approve.

Hermes:  PM scoped 3 features. Dev starting build.
         I'll send updates every 5 minutes.

[20 minutes later]

Hermes:  Submission ready as DRAFT.
         Project: <url>  Repo: <url>  Deploy: <url>
         Reply "ship it" to publish.

You:  ship it

Hermes:  Submitted. ACTIVE on TAIKAI as of 14:32 WEST.
```

Every word of that conversation, every tool call, and every subagent spawn is logged in Hermes session memory. Resumable, inspectable, replayable.

## How it works

```
                ┌─────────────┐
   hackathon    │  Strategist │  reads brief, scouts angle
   URL ───────► └──────┬──────┘
                       ▼
                ┌─────────────┐
                │     PM      │  scopes MVP, sets time budget
                └──────┬──────┘
                       ▼
                ┌─────────────┐
                │     Dev     │  delegates to claude-code subagent
                └──────┬──────┘
                       ▼
              ┌────────┴────────┐
              ▼                 ▼
        ┌──────────┐      ┌─────────────┐
        │ Designer │      │ Storyteller │
        └────┬─────┘      └──────┬──────┘
             └────────┬──────────┘
                      ▼
                ┌─────────────┐
                │  Submitter  │  fills form, awaits approval
                └──────┬──────┘
                       ▼
                  approval prompt
                       ▼
                  submission
```

The orchestrator is a Hermes skill, not orchestration code. The flow above is what the `squad` skill instructs the running agent to do.

## Origin story

HackClaw was built during [Hacklayer 4_1 MCP Edition](https://taikai.network/layerx/hackathons/hacklayer4-1-mcp-edition), an internal LayerX hackathon. The recursive flex: HackClaw submitted itself.

The TAIKAI project page, the deploy URL, the README you're reading. All produced by HackClaw running through Hermes. The commit history, the Vercel logs, and the TAIKAI submission timestamp all corroborate the claim.

## Roadmap

- v0.3: Native adapters for Devpost, ETHGlobal, Encode, Dorahacks (replace browser fallback for those)
- v0.4: Auto-recorded demo videos via Browserbase
- v0.5: Sponsor-track optimization, multi-objective scoring across prize tracks
- v0.6: Hybrid mode, humans and agents collaborating inside the same submission
- v0.7: Cost-aware model routing per agent role (Haiku for Designer + Submitter, Sonnet for Strategist + PM)

## Contributing

Issues and PRs welcome. Read [docs/architecture.md](docs/architecture.md) before sending a PR.

The codebase is intentionally small: prompts as markdown skills, platform adapters as Python tools, no orchestration code.

## License

MIT. Use it, fork it, ship with it.

## Built by

[Mario Alves](https://github.com/hypermario) at [LayerX](https://layerx.xyz). Part of the LayerX studio family alongside [TAIKAI](https://taikai.network), Ardaven, and RayTrade Studio.

## Acknowledgments

- **Nous Research** for [Hermes Agent](https://github.com/NousResearch/hermes-agent), the substrate this is built on
- **Anthropic** for Claude and the MCP standard that makes platform-agnostic agent integrations possible
- **TAIKAI** for being the reference hackathon platform and for shipping an MCP that made the recursive flex possible
