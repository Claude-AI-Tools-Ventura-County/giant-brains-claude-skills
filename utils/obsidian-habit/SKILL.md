---
name: obsidian-habit
description: "Run the daily Obsidian habit-building exercise: a 6-state FSM that rotates one low-friction tactic per day (front-door homepage, frictionless capture, auto-archive stale notes, rebalance-OS RAG morning pull, visible streak, then maintenance) so vault overwhelm stops blocking the habit. Trigger whenever the user asks to run, resume, check in on, or check the status of their Obsidian habit skill, today's Obsidian tactic, or the vault habit-building experiment."
---

# Obsidian Habit Builder

Turns "I should use Obsidian more" into one small, opt-in action a day. Never
presents the whole vault, never asks the user to decide the plan — the FSM
already decided it. The only thing the user picks each day is: adopt, decline,
or defer.

## Prerequisites

- [ ] `OBSIDIAN_VAULT_PATH` env var set, or pass `--vault /path/to/vault` on first run
- [ ] `python3` on PATH
- [ ] rebalance-OS MCP reachable (optional — Tactic 4 degrades to a manual step if not)

First run auto-initializes. Nothing below requires the user to read a schema.

## How Claude Code should run this, every invocation

1. Always call status first — never assume state:
   ```
   python3 scripts/habit.py status --vault "$OBSIDIAN_VAULT_PATH"
   ```
   If it errors "not initialized," run `init` once, then re-run `status`.
2. If `last_run_date` == today (UTC), the day already ran — report the existing
   result in 2-3 lines and stop. Do not re-run or re-ask. (Idempotent by design.)
3. Otherwise, look up the current tactic from `tactic_order[current_index]` and
   follow that tactic's row in the table below.
4. Run the tactic's action (script if it has one; otherwise read the matching
   section in `references/tactics.md` and present the 2–5 minute manual steps).
5. Show the user what happened in under 10 lines. Then ask exactly **one**
   question: *"Adopt this, decline it, or defer to tomorrow?"* — use
   `ask_user_input_v0` with three options if the interface supports it.
6. Record the answer:
   ```
   python3 scripts/habit.py respond <adopt|decline|defer>
   ```
   `adopt`/`decline` both advance to tomorrow's tactic (a decision was made —
   that's the win, not just whether they said yes). `defer` keeps the same
   tactic queued for tomorrow instead of losing it.
7. Never move, delete, or archive files without the tactic script's own
   `--apply` gate. Default is always dry-run. This is a hard rule, not a
   suggestion.

## FSM

| State | Tactic | Entry action | Adopt/Decline → | Defer → |
|---|---|---|---|---|
| `homepage` | 1. Front-door homepage | Print 3-step Homepage plugin setup | next tactic | stay |
| `archive` | 3. Auto-archive stale notes | Dry-run `archive_stale_notes.py`, show candidates | next tactic | stay |
| `capture` | 2. Frictionless capture shortcut | Print OS-shortcut setup for `Inbox.md` | next tactic | stay |
| `pull` | 4. rebalance-OS morning pull | Query RAG for 2-3 resurfaced notes (or print manual cron step if unreachable) | next tactic | stay |
| `streak` | 5. Visible streak | Run `streak_update.py --mark`, show current streak | `MAINTENANCE` | stay |
| `MAINTENANCE` | — | Re-check adopted tactics still active; light touch only | loops daily | — |

Default order is 1→3→2→4→5 (this was validated as the easiest-first sequence).
The user can reorder anytime with `habit.py reorder homepage,capture,archive,pull,streak`.

## Opt-in & flexibility commands

| User says | Run |
|---|---|
| "skip today" | `habit.py respond defer` |
| "I don't want tactic X at all" | `habit.py decline-permanently <tactic>` |
| "jump to the streak one" | `habit.py jump streak` |
| "pause this" | `habit.py pause` |
| "resume" | `habit.py resume` |
| "undo the archive" | `python3 scripts/archive_stale_notes.py --undo <manifest-path-from-events-log>` |
| "what's my status" | `habit.py status` (read-only, always safe) |

## Safety rules (non-negotiable)

- **Dry-run by default.** `archive_stale_notes.py` only prints candidates
  unless `--apply` is passed. Every apply writes a manifest so it's reversible.
- **Bounded scan.** File scans cap at 500 files per run (`--max-files`).
- **UTC timestamps only**, everywhere.
- **Single writer.** Only `habit.py` writes `state.json`, via atomic
  write-tmp-then-rename. Nothing else touches it.
- **Append-only log.** Every run appends one JSON line to `events.jsonl`.
  Never edited, never truncated.

## File locations (inside the vault, portable with it)

```
<vault>/_meta/obsidian-habit/state.json              # current FSM position, single writer
<vault>/_meta/obsidian-habit/events.jsonl            # append-only run/decision log
<vault>/_meta/obsidian-habit/archive-whitelist.txt   # files Tactic 3 must never move (auto-created)
<vault>/Older than 21 days/                          # where Tactic 3 moves stale notes (vault root, not nested in _archive)
```

rebalance-OS already indexes the whole vault path, so archiving is non-destructive
to search/RAG — nothing disappears from `ask`, it just leaves the visible tree.

To exempt a note from archiving regardless of its last-edit date, add it to
`archive-whitelist.txt` — one entry per line, either a bare filename
(`README.md`, matches anywhere in the vault) or a vault-relative path
(`Projects/README.md`, matches only that file). The file is auto-created
with format instructions the first time the archive script runs.

## References

- `references/tactics.md` — full detail + manual steps for tactics 1, 2, 4 (not
  scriptable generically: plugin installs, OS shortcuts, Slack/cron wiring).
  Read this before presenting those tactics' setup steps.

## Review History

<!-- Append-only: one row per review/audit pass. Never edit or delete a past row. -->

| Date | Reviewer | Outcome | Notes |
|---|---|---|---|
| 2026-07-04 | noelsaw1 | Seeded | Baseline row from git history (last content change); no formal review conducted yet. |
