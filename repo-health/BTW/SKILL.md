---
name: btw
description: MOVED within this repo to 06-session/BTW — invoke it from there. Original triggers follow. Starts and maintains a manual session attention firewall for Claude Code. Invoke only with /btw when the user explicitly wants focus mode, no side quests, or a maximum of three active tasks. Create one append-only Markdown log per BTW focus session, capture the opening user prompt plus repository and branch context, and park assistant-initiated off-task findings as Action, Review Later, or Interesting instead of surfacing them in assistant prose. After activation, treat plain-language "btw check" as an in-session re-anchor rather than a new invocation.
argument-hint: "[up to 3 focus items or the opening session request]"
disable-model-invocation: true
allowed-tools:
  - 'Bash(python3 "${CLAUDE_SKILL_DIR}/scripts/btw.py" *)'
  - 'Bash(python "${CLAUDE_SKILL_DIR}/scripts/btw.py" *)'
---

# BTW — moved

This skill now lives at [06-session/BTW/SKILL.md](../../06-session/BTW/SKILL.md) in this repo. Re-point your symlink (`ln -sfn "$PWD/06-session/BTW" ~/.claude/skills/BTW`) or re-run the README install loop. This stub exists for one release (v1.1.0) so existing symlinks keep resolving, and is removed in the release after.
