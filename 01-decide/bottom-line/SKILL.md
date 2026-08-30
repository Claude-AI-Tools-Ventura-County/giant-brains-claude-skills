---
name: bottom-line
description: |
  MOVED within this repo to 02-plan/bottom-line — invoke it from there. Original triggers follow.
  Distill long, verbose, or repetitive output—especially from Claude or other AI agents comparing options, tradeoffs, and recommendations—into a short, deduplicated bottom-line summary. Surface the real decision, a clear recommendation, and any choice that would be hard to reverse later. 

  Trigger when content is decision- or tradeoff-oriented and the user asks for the bottom line, TLDR, gist, takeaway, to cut to the chase, summarize cleanly, says it is too long/verbose/repetitive, or asks what they actually need to decide or might regret. Also self-trigger when prior agent output is long-winded, hedged, or repetitive and a decision needs to be pulled out clearly, even without those exact words. 

  Do not trigger when the user wants procedural steps, commands, or an execution sequence; that is /linear's job, not this skill's. 
---

# bottom-line — moved

This skill now lives at [02-plan/bottom-line/SKILL.md](../../02-plan/bottom-line/SKILL.md) in this repo. Re-point your symlink (`ln -sfn "$PWD/02-plan/bottom-line" ~/.claude/skills/bottom-line`) or re-run the README install loop. This stub exists for one release (v1.1.0) so existing symlinks keep resolving, and is removed in the release after.
