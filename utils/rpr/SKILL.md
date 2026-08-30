---
name: rpr
description: MOVED to giant-brains-swe-skills (04-toolbox/rpr) — invoke it from there. Original triggers follow. Review the most recent permission requests in the current session, generalize them into safe allowlist rules, and append them to .claude/settings.local.json to reduce future prompts. Triggers when the user runs "/rpr", "/rpr <N>", "/rpr session", or says things like "stop asking me", "I keep getting permission prompts", or "reduce these requests". Differentiates from read-only (which pre-approves safe reads) and fewer-permission-prompts (which mines all history) by reacting only to the recent, specific commands that just prompted in this session.
---

# rpr — moved

This skill now lives in [giant-brains-swe-skills](https://github.com/Claude-AI-Tools-Ventura-County/giant-brains-swe-skills/tree/main/04-toolbox/rpr). Install it from there and invoke that copy; this stub exists for one release so existing symlinks keep resolving, and will be removed in the release after v1.1.0.

```bash
git clone https://github.com/Claude-AI-Tools-Ventura-County/giant-brains-swe-skills.git && cd giant-brains-swe-skills && ln -s "$PWD/04-toolbox/rpr" ~/.claude/skills/rpr
```
