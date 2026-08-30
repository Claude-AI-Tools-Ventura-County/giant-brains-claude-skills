---
name: swe
description: MOVED to giant-brains-swe-skills (01-plan/swe) — invoke it from there. Original triggers follow. Apply an opinionated software-engineering governance lens to a build/spec/PRD document — especially a "build v1.x" doc — so the plan enforces minimal scope, designs for diagnosis, accounts for blast radius, and is verifiable before anyone writes code. Use this when authoring or reviewing a v1.x build plan, implementation spec, architecture doc, RFC, or AGENTS.md/CLAUDE.md, or when the user says "write a project plan," "write a plan," "review this build doc," "apply our SWE standards," "make this plan production-grade," "gate this spec," "is this plan ready to build," "bake in our engineering philosophy," or pastes a plan and asks whether it embodies good engineering discipline. Also self-trigger before drafting a v1.x build document or any project plan so the standards shape it from the first draft instead of being bolted on after. This is the standard (the rubric), not the pipeline — it supplies the engineering invariants a plan is checked against. Its Pillar 0 grades provenance — whether the plan was written against a trace of the real system (see the recon skill) rather than an invented blast radius — where an existing system is in play.
---

# swe — moved

This skill now lives in [giant-brains-swe-skills](https://github.com/Claude-AI-Tools-Ventura-County/giant-brains-swe-skills/tree/main/01-plan/swe). Install it from there and invoke that copy; this stub exists for one release so existing symlinks keep resolving, and will be removed in the release after v1.1.0.

```bash
git clone https://github.com/Claude-AI-Tools-Ventura-County/giant-brains-swe-skills.git && cd giant-brains-swe-skills && ln -s "$PWD/01-plan/swe" ~/.claude/skills/swe
```
