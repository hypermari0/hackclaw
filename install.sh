#!/usr/bin/env bash
# HackClaw install: symlink skills and plugin into ~/.hermes
#
# Re-run safe. Idempotent. Will replace existing symlinks but refuse to clobber
# real directories (you'll see a clear error).

set -euo pipefail

REPO_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
HERMES_DIR="${HERMES_DIR:-$HOME/.hermes}"

SKILLS_TARGET="$HERMES_DIR/skills/hackclaw"
PLUGIN_TARGET="$HERMES_DIR/plugins/hackclaw"

SKILLS_SOURCE="$REPO_DIR/skills/hackclaw"
PLUGIN_SOURCE="$REPO_DIR/plugin/hackclaw"

bold() { printf "\033[1m%s\033[0m\n" "$1"; }
warn() { printf "\033[33m%s\033[0m\n" "$1"; }
fail() { printf "\033[31m%s\033[0m\n" "$1" >&2; exit 1; }

bold "HackClaw install"
echo "Repo: $REPO_DIR"
echo "Hermes: $HERMES_DIR"
echo

# Sanity check Hermes
if [ ! -d "$HERMES_DIR" ]; then
  fail "$HERMES_DIR not found. Install Hermes first (https://github.com/NousResearch/hermes-agent)."
fi

mkdir -p "$HERMES_DIR/skills" "$HERMES_DIR/plugins"

# Skills
if [ -L "$SKILLS_TARGET" ] || [ ! -e "$SKILLS_TARGET" ]; then
  rm -f "$SKILLS_TARGET"
  ln -s "$SKILLS_SOURCE" "$SKILLS_TARGET"
  echo "✔ skills linked: $SKILLS_TARGET → $SKILLS_SOURCE"
elif [ -d "$SKILLS_TARGET" ]; then
  fail "$SKILLS_TARGET exists as a real directory. Move or remove it, then re-run."
fi

# Plugin
if [ -L "$PLUGIN_TARGET" ] || [ ! -e "$PLUGIN_TARGET" ]; then
  rm -f "$PLUGIN_TARGET"
  ln -s "$PLUGIN_SOURCE" "$PLUGIN_TARGET"
  echo "✔ plugin linked: $PLUGIN_TARGET → $PLUGIN_SOURCE"
elif [ -d "$PLUGIN_TARGET" ]; then
  fail "$PLUGIN_TARGET exists as a real directory. Move or remove it, then re-run."
fi

echo
bold "Next steps"
cat <<EOF
  1. Install plugin deps:        pip install -e .
  2. Configure TAIKAI MCP:       hermes mcp add taikai
  3. Start Hermes:               hermes
  4. Run the squad:              /hackathon run https://taikai.network/<org>/hackathons/<slug>

For Telegram delivery: \`hermes gateway\` after configuring the Telegram bot in your Hermes config.
EOF
