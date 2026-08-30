---
name: relay
description: MOVED to giant-brains-swe-skills (02-build/relay) — invoke it from there. Original triggers follow. Generate and run a relay thread file in `relay-system/<date>/<slug>.md` — a turn-based, file-based review loop between two Claude Code agents (a Producer who builds, a Reviewer who critiques and proposes fixes the author applies) so a human stops copy-pasting output between two windows. Use this whenever the user wants to "set up a relay", run a "producer/reviewer" or "worker/reviewer" loop, have "two agents" review each other's work in a shared file, "hand off" between agents without pasting, or cut copy-paste and stray artifacts across AI sessions. Also use it to START a relay (scaffold the dated file) or to TAKE A TURN in an existing one (read the file, act only on your turn, append your block, flip the pointer). Trigger even if the user only describes two Claude windows shuttling text back and forth.
---

# relay — moved

This skill now lives in [giant-brains-swe-skills](https://github.com/Claude-AI-Tools-Ventura-County/giant-brains-swe-skills/tree/main/02-build/relay). Install it from there and invoke that copy; this stub exists for one release so existing symlinks keep resolving, and will be removed in the release after v1.1.0.

```bash
git clone https://github.com/Claude-AI-Tools-Ventura-County/giant-brains-swe-skills.git && cd giant-brains-swe-skills && ln -s "$PWD/02-build/relay" ~/.claude/skills/relay
```
