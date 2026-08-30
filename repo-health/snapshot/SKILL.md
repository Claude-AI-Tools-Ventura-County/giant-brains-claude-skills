---
name: snapshot
description: MOVED within this repo to 06-session/snapshot — invoke it from there. Original triggers follow. Save the most recent substantive response — plus session metadata, recent test findings, and phase status — to a persistent, additive snapshot.md file so the user can re-find and resume the session later (next morning, after a crash, or across chat tabs). Trigger whenever the user says "snapshot", "snapshot this", "save this session", "save our progress", "save before I go to bed / sign off / wrap up", "checkpoint this", or expresses worry about losing work, losing the chat, or VS Code crashing. Also offer it proactively when a long working session reaches a natural stopping point with unsaved findings. Use only to preserve session progress — not when the user wants to save or export a specific artifact (a file, PDF, image, code snippet, or document).
---

# snapshot — moved

This skill now lives at [06-session/snapshot/SKILL.md](../../06-session/snapshot/SKILL.md) in this repo. Re-point your symlink (`ln -sfn "$PWD/06-session/snapshot" ~/.claude/skills/snapshot`) or re-run the README install loop. This stub exists for one release (v1.1.0) so existing symlinks keep resolving, and is removed in the release after.
