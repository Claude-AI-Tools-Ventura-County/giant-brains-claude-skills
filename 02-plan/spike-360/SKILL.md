---
name: spike-360
description: >
  MOVED to giant-brains-swe-skills (01-plan/spike-360) — invoke it from there. Original triggers follow.
  Interrogate authority before planning a feature, refactor, migration, rewrite,
  backfill, event-sourcing design, dual-write setup, new authoritative store, or
  system-of-record change. Fire whenever a proposal might introduce, move,
  duplicate, or replace authoritative state — or involves event sourcing or
  "event sourced," a "source of truth," "authoritative" data, dual-writes,
  replay, projections, replacing persistence, a new data store, or "design the
  architecture for / rewrite X" — and classify authority before writing any plan
  or reaching for a seam or architecture spike. The five levels: audit-only, read
  projection, dual-written peer, source of truth, replacement runtime; for
  audit-only or read-projection cases, fire just long enough to classify and
  stop, and for dual-written peer and above, require the surface and
  failure-scenario checks first. Triggering is deliberately broad — the skill
  classifies first and stops fast when the level is light. Skip only for a
  localized bugfix with no authority change, or when the authority level is
  already classified, agreed, and its required surface and failure-scenario pass
  is already complete.
---

# spike-360 — moved

This skill now lives in [giant-brains-swe-skills](https://github.com/Claude-AI-Tools-Ventura-County/giant-brains-swe-skills/tree/main/01-plan/spike-360). Install it from there and invoke that copy; this stub exists for one release so existing symlinks keep resolving, and will be removed in the release after v1.1.0.

```bash
git clone https://github.com/Claude-AI-Tools-Ventura-County/giant-brains-swe-skills.git && cd giant-brains-swe-skills && ln -s "$PWD/01-plan/spike-360" ~/.claude/skills/spike-360
```
