---
name: shakedown
description: MOVED to giant-brains-swe-skills (03-audit/shakedown) — invoke it from there. Original triggers follow. Audit a script-calling skill for CWD-sensitive path-resolution bugs — bundled `.sh` scripts that run in the session that wrote them but come back "not found" in another session, repo, or install — then write a graded report with a proposed fix. Runs a read-only static path audit plus a live scenario matrix (foreign CWD, nested dirs, spaces-in-path, project vs user install, stripped exec bit). Use when the user says "test this skill", "shake out the path bugs", "why can't Claude find my skill's scripts", "the bash script isn't being located", "harden this skill before I ship it", "audit the skill's script paths", or points at a script-calling skill that behaves unreliably across sessions or installs.
---

# shakedown — moved

This skill now lives in [giant-brains-swe-skills](https://github.com/Claude-AI-Tools-Ventura-County/giant-brains-swe-skills/tree/main/03-audit/shakedown). Install it from there and invoke that copy; this stub exists for one release so existing symlinks keep resolving, and will be removed in the release after v1.1.0.

```bash
git clone https://github.com/Claude-AI-Tools-Ventura-County/giant-brains-swe-skills.git && cd giant-brains-swe-skills && ln -s "$PWD/03-audit/shakedown" ~/.claude/skills/shakedown
```
