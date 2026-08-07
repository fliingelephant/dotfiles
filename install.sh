#!/bin/sh
# Wire this dotfiles repo into Claude Code and Codex. Idempotent.
set -e
root=$(cd "$(dirname "$0")" && pwd)

mkdir -p ~/.claude/skills ~/.agents/skills ~/.codex

# 1. One instruction file for both runtimes.
ln -sfn "$root/AGENTS.md" ~/.claude/CLAUDE.md
ln -sfn "$root/AGENTS.md" ~/.codex/AGENTS.md

# 2. Shared skills: both runtimes.
for s in "$root"/skills/*/; do
  ln -sfn "${s%/}" ~/.claude/skills/"$(basename "$s")"
  ln -sfn "${s%/}" ~/.agents/skills/"$(basename "$s")"
done

# 3. Claude-only skills.
for s in "$root"/claude/skills/*/; do
  ln -sfn "${s%/}" ~/.claude/skills/"$(basename "$s")"
done

# 4. Codex-only skills.
for s in "$root"/codex/skills/*/; do
  ln -sfn "${s%/}" ~/.agents/skills/"$(basename "$s")"
done
