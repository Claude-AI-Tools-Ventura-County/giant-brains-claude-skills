---
name: phase-qa
description: >
  MOVED to giant-brains-swe-skills (01-plan/phase-qa) — invoke it from there. Original triggers follow.
  Project plan enhancement tool. Reads a phased planning doc and appends a QA checklist
  (DRY, SOLID, observability, and phase-appropriate litmus tests) under each phase, and
  optionally adds an anti-goals section to give each checklist a scope boundary, and surfaces
  per phase whether the work needs deploying to a remote environment. Invoke before work
  begins to bake checks into the plan; invoke mid-project or post-project to also run
  code-diff reviews on completed phases. Always confirms with the user where they are in
  the process before writing anything. Gate enforcement is at the operator's discretion.
  Trigger: user invokes the skill directly, optionally naming phases to skip.
---

# phase-qa — moved

This skill now lives in [giant-brains-swe-skills](https://github.com/Claude-AI-Tools-Ventura-County/giant-brains-swe-skills/tree/main/01-plan/phase-qa). Install it from there and invoke that copy; this stub exists for one release so existing symlinks keep resolving, and will be removed in the release after v1.1.0.

```bash
git clone https://github.com/Claude-AI-Tools-Ventura-County/giant-brains-swe-skills.git && cd giant-brains-swe-skills && ln -s "$PWD/01-plan/phase-qa" ~/.claude/skills/phase-qa
```
