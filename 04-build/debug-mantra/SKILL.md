---
name: debug-mantra
description: MOVED to giant-brains-swe-skills (02-build/debug-mantra) — invoke it from there. Original triggers follow. Four-mantra debugging discipline — reproduce, trace the fail path, falsify the hypothesis, cross-reference every breadcrumb. Recite the mantra block verbatim at the start of any debugging session, then apply the four steps in order before proposing any fix. Trigger on /debug-mantra and proactively whenever debugging starts — user reports a bug, says something is broken/throwing/failing, asks to debug/diagnose/investigate an issue, pastes a stack trace or error log, or asks an attribution question ('where is this coming from?', 'what posts/triggers/generates this?', 'why is X appearing?') where the answer is an unknown source to find, not just a crash to fix. Adapted from: https://github.com/thananon/9arm-skills
---

# debug-mantra — moved

This skill now lives in [giant-brains-swe-skills](https://github.com/Claude-AI-Tools-Ventura-County/giant-brains-swe-skills/tree/main/02-build/debug-mantra). Install it from there and invoke that copy; this stub exists for one release so existing symlinks keep resolving, and will be removed in the release after v1.1.0.

```bash
git clone https://github.com/Claude-AI-Tools-Ventura-County/giant-brains-swe-skills.git && cd giant-brains-swe-skills && ln -s "$PWD/02-build/debug-mantra" ~/.claude/skills/debug-mantra
```
