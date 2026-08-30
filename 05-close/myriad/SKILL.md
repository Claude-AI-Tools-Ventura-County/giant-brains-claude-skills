---
name: myriad
description: >-
  MOVED within this repo to 06-session/myriad — invoke it from there. Original triggers follow.
  End-of-day triage funnel for messy agent output. Takes a wall-of-text agent
  completion message that blends finished work, blockers, gated next steps, and
  stray follow-ups, and sorts it into four buckets: Completed (shipped), Critical
  Blockers (what stops you now), Awaiting Your Call (gated next steps and decision
  prompts that need your go/no-go), and the "myriad" (nice-to-haves, ideas, dupes,
  someday-maybes). Shows a clean Done / Broken / Awaiting summary, nudges you with
  current git status so uncommitted work never gets abandoned, and parks the long
  tail in a durable weekly backlog file using an idempotent, verify-after-write
  append so nothing is ever lost or double-logged. Trigger when handed a long,
  mixed agent response at the end of a work session, or on /myriad.
---

# myriad — moved

This skill now lives at [06-session/myriad/SKILL.md](../../06-session/myriad/SKILL.md) in this repo. Re-point your symlink (`ln -sfn "$PWD/06-session/myriad" ~/.claude/skills/myriad`) or re-run the README install loop. This stub exists for one release (v1.1.0) so existing symlinks keep resolving, and is removed in the release after.
