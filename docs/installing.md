# Installing HackClaw

HackClaw runs on top of Hermes Agent. If you don't have Hermes installed yet, do that first.

## Step 1: Install Hermes Agent

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

Or follow the manual install at [github.com/NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent).

After install:

```bash
hermes setup
```

The setup wizard walks you through:

- Provider selection (Anthropic for Sonnet 4.6 is the default for HackClaw)
- API key configuration
- Optional: Telegram bot token, Discord, Slack, etc. for the messaging gateway

Verify Hermes works:

```bash
hermes
> hello
```

You should get a response. If you don't, fix Hermes first; HackClaw won't work without it.

## Step 2: Clone HackClaw and run the installer

```bash
git clone https://github.com/hypermario/hackclaw.git
cd hackclaw
./install.sh
```

This symlinks two things into your `~/.hermes/` directory:

- `skills/hackclaw/` -> `~/.hermes/skills/hackclaw/`
- `plugin/hackclaw/` -> `~/.hermes/plugins/hackclaw/`

Symlinks (not copies) so updating HackClaw is just `git pull`.

## Step 3: Install the plugin's Python dependencies

```bash
pip install -e .
```

The plugin needs `httpx` and `pydantic`. Hermes itself has its own dependency tree, separate from this.

## Step 4: Configure the TAIKAI MCP source

If you'll target TAIKAI hackathons (most likely), add the TAIKAI MCP to Hermes:

```bash
hermes mcp add taikai
```

Follow the prompts to authenticate (TAIKAI session token).

If your version of Hermes uses a different MCP-add flow (e.g., editing `~/.hermes/config.yaml` manually), see the Hermes docs for the current pattern.

## Step 5: Verify HackClaw loads

```bash
hermes
```

Once Hermes starts:

```
> /skills
```

You should see `hackclaw/squad`, `hackclaw/strategist`, `hackclaw/pm`, `hackclaw/dev`, `hackclaw/designer`, `hackclaw/storyteller`, `hackclaw/submitter` in the list.

```
> /tools
```

You should see `hackclaw_select_platform`, `hackclaw_get_brief`, `hackclaw_list_submissions`, `hackclaw_create_draft`, `hackclaw_update_project`, `hackclaw_submit`.

If anything is missing, run `hermes doctor` and check the logs at `~/.hermes/logs/`.

## Step 6 (optional): Configure Telegram

If you want the Telegram demo experience, set up the Hermes messaging gateway:

```bash
hermes config set messaging.telegram.bot_token <your-bot-token>
hermes gateway
```

Now you can message your bot:

```
You:  /hackathon run https://taikai.network/<org>/hackathons/<slug>
```

Or just describe the task naturally:

```
You:  Win Hacklayer 4_1 for me.
```

Hermes routes it through the `squad` skill, the same as the CLI path.

## Troubleshooting

**Skills don't load.**
Check `~/.hermes/skills/hackclaw` exists and the symlink points to the repo. `ls -la ~/.hermes/skills/hackclaw` should show a symlink.

**Plugin tools don't register.**
Confirm `pip install -e .` ran cleanly. Check `~/.hermes/logs/` for plugin load errors.

**TAIKAI calls fail.**
Try the GraphQL fallback: `export HACKCLAW_TAIKAI_VIA=graphql` and `export TAIKAI_TOKEN=<your-token>` before starting Hermes.

**Squad runs but Dev never deploys.**
The Dev skill delegates to Hermes's `claude-code` subagent. Confirm `claude` CLI is installed and available on your PATH (`npm i -g @anthropic-ai/claude-code`). Also confirm `GITHUB_TOKEN` and `VERCEL_TOKEN` are set.

**Telegram bot doesn't respond.**
Make sure `hermes gateway` is running (not just `hermes`). The CLI is one mode; the gateway is another.
