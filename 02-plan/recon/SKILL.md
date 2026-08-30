---
name: recon
description: >-
  MOVED to giant-brains-swe-skills (01-plan/recon) — invoke it from there. Original triggers follow.
  Trace an existing system end to end — entry points, call paths, every read and
  write of the state involved, the contracts crossed, the failure and rollback
  paths — and write it down as a Recon Map before a plan for changing it is
  drafted. Fires when the user asks to plan, spec, design, refactor, migrate, or
  size a change to code that already exists: "write a plan", "plan this out",
  "how should we build X into this", "refactor X", "migrate X", "what would it
  take to change X", "will this break anything". Also self-trigger before you
  write any plan step whose blast radius names code you have not read. Uses the
  codebase-memory knowledge graph when installed, falls back to grep, and fans
  wide traces out across parallel read-only subagents. Produces a Recon Map file
  and hands off; it does not grade the plan. Do NOT fire on greenfield work with
  no existing system to trace, on a change confined to a file already read in
  full, on a typo or copy edit, on a non-code plan, or when a current Recon Map
  for the same subsystem already exists.
---

# recon — moved

This skill now lives in [giant-brains-swe-skills](https://github.com/Claude-AI-Tools-Ventura-County/giant-brains-swe-skills/tree/main/01-plan/recon). Install it from there and invoke that copy; this stub exists for one release so existing symlinks keep resolving, and will be removed in the release after v1.1.0.

```bash
git clone https://github.com/Claude-AI-Tools-Ventura-County/giant-brains-swe-skills.git && cd giant-brains-swe-skills && ln -s "$PWD/01-plan/recon" ~/.claude/skills/recon
```
