---
name: myriad
description: >-
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

# Skill: Myriad — End-of-Day Agent-Output Triage

## What this solves
An agent hands you a wall of text that blends several different things. This skill
**separates signal from noise and puts each kind where it belongs**:

- **Completed**, **Critical Blockers**, and **Awaiting Your Call** stay visible —
  your working view; act on these now.
- The **myriad** (everything else) gets **out of your face but not lost** — parked
  in a dated weekly backlog file.

The myriad file is a **parking lot, not a burndown list.** The value is the
*separation*, not the listing — and the parking lot must be trustworthy enough
that deferring an item *feels safe*. If people don't trust it, they won't defer,
and they'll carry the whole list in their head. So logging is idempotent and
verified (step 4).

## When to Use
When you receive a long, messy agent completion message that mixes finished work,
blockers, gated next steps, and follow-up items — typically at the end of a work
session. Also on `/myriad`.

## Instructions

You will be given the raw agent output. Perform these steps in order.

### 1. Parse the input into four buckets
- **Completed** — the main deliverables actually finished.
- **Critical Blockers** — issues that stop progress *now* or demand immediate attention.
- **Awaiting Your Call** — real next steps that are gated on your decision: human-gated
  deploy/cutover sequences, "want me to proceed?" prompts, choices the agent parked for
  you. These are the critical path, not someday-maybes — they must stay visible.
- **Myriad (non-critical)** — everything else: ideas, nice-to-haves, suggestions,
  loose observations, duplicates, repeated information.

Dedup + precedence (if an item fits more than one bucket, keep the single highest):
`Critical Blockers > Awaiting Your Call > Myriad`. (Completed is judged independently.)
Never duplicate an item across buckets.

### 2. Show the cleaned summary
Output exactly these sections, in this order:

```markdown
## Completed
- [task 1]
- [task 2]

## Critical Blockers
- [blocker 1]

## Awaiting Your Call
- [gated next step / decision prompt 1]
```

For any empty section write `None.` (Do not drop the heading — its emptiness is signal.)

**Never** put myriad items in these sections — they belong only in the weekly file (step 4).

### 3. Show current git status (mandatory)
Immediately after the summary, run `git status` in the project root and show it:

```markdown
## Git Status
<output of git status>
```

If you cannot run commands, output instead:

```markdown
## Git Status
⚠️ Reminder: run `git status` to review your working tree before proceeding.
```

This reminder is **not optional** — it keeps uncommitted work from being abandoned.

### 4. Log the myriad — via the logging helper (deterministic + verified)
The parking lot only earns trust if nothing is ever lost or double-written, so the
mechanical guarantees — week-file resolution, fuzzy dedup, atomic write, and read-back
verification — live in a helper script and must not be skipped or hand-rolled.
**Do not hand-edit the weekly file.** Let the script own the write.

**Resolve two paths first.** `<skill-dir>` = the absolute directory this SKILL.md was loaded
from (the helper is at `<skill-dir>/scripts/log_myriad.py`). `<2-working>` = the `2-WORKING/`
directory in the current project root; the script creates it if missing, so pass the intended
absolute path even when it doesn't exist yet.

**4a. Your job first (the semantic part).** For each myriad item, write ONE clean,
actionable sentence. Strip preamble and keep only the action — e.g.
*"I left this as a plan only — nothing built. Want me to file a GH issue?"* becomes
*"File a backing GH issue to mirror the other Focus5 lanes."* (Note: a "Want me to…?"
decision prompt is **Awaiting Your Call**, not myriad — see step 2. Only the deferrable
nice-to-have goes here.)

**4b. Preview first — always dry-run before writing.** Pipe one clean item per line:
```bash
printf '%s\n' "item 1" "item 2" | python3 "<skill-dir>/scripts/log_myriad.py" --dir "<2-working>" --dry-run
```
The JSON receipt shows the target file, what would be logged, and what it would skip as a
duplicate. Show the user the target file and the proposed items, then ask **"Append now? (y/n)"**.
**Stop here — do not run 4c until the user replies yes.** The dry-run writes nothing, so it is
safe to pause indefinitely.

**4c. On yes — write + verify.** Same command without `--dry-run`:
```bash
printf '%s\n' "item 1" "item 2" | python3 "<skill-dir>/scripts/log_myriad.py" --dir "<2-working>"
```
The script resolves the week file (Monday-of-week, so the whole week shares one file),
fuzzy-dedups against everything already logged that week, appends under today's
`### <date>` section without touching any existing line, seeds a PDDA-style
frontmatter block at the top when the weekly file is first created (and upgrades a
legacy frontmatter-less week file on the next write), then **reads the file back to
confirm every item is on disk.**

**4d. Report the receipt honestly.** Relay the script's `message` verbatim, e.g.
*"Logged 2 new item(s), skipped 1 duplicate(s), all verified on disk."*
- If `verified` is `false` or the script exits non-zero (code 3), the write did **not**
  verify — tell the user it FAILED and do not claim anything was logged.
- If neither `python3` nor `python` (3.6+) is available, **do not hand-write to the weekly
  file** — a manual append would miss Monday-of-week resolution and dedup and could corrupt
  the parking lot. Instead show the user the clean items and the intended file path, and say
  plainly the logging script couldn't run so the items are **not logged yet**.

### 5. Final output
Your response contains, in order:
1. The cleaned summary (Completed + Critical Blockers + Awaiting Your Call)
2. The Git Status section
3. A section titled **Myriad Items (to be logged)** showing the clean items and the target
   file from the dry-run receipt (step 4b), and **asking whether to append them**.
4. On confirmation: run the helper (step 4c) and relay its verified receipt (step 4d).

## Example final output

```markdown
## Completed
- Reproduced the dirty baseline (11 mismatches), wrote 34 baseline events, shadow-diff clean (26/26, 24/24)
- PR #357 green, merged to development (cc91e6a); worktree + marathon branch cleaned up

## Critical Blockers
None.

## Awaiting Your Call
- Prod cutover is staged and gated on you: deploy development→main, run the baseline import on prod, flip SUMMARIZE_WEEK_COMPLETED_SOURCE=projection

## Git Status
On branch main — up to date with origin/main
Untracked: SKILLS/PDDA-EOD/myriad/
```

---

**Myriad Items (to be logged)** — append to `2-WORKING/MYRIAD-WEEK-2026-07-06.md`:

```markdown
---
title: Myriad — Week of 2026-07-06
status: Active (weekly myriad parking lot)
created: 2026-07-08
updated: 2026-07-08
owner: noelsaw
goal: >-
  Park non-critical follow-up items from end-of-day agent triage in one
  durable weekly backlog.
doc_type: backlog
roadmap_exempt: true
---

```

```markdown
### 2026-07-08
- [ ] Offer a per-lane code-diff drill-down (Zapier ingest, Focus5Float) instead of commit-level view
```

*(The filename is keyed to **Monday 2026-07-06** — the week — while `### 2026-07-08` is the
actual day. Every day that week appends to this same file. Intended, not a mismatch.)*

Append now? (y/n) → on yes the helper runs and returns:
`Logged 1 new item(s), skipped 0 duplicate(s), all verified on disk.`

## Guardrails
- **Four buckets, no leaks.** Myriad items never appear in Completed / Blockers / Awaiting.
  Gated next steps and decision prompts go in **Awaiting Your Call** — never the parking lot.
- **The parking lot is sacred — the helper owns the write.** Don't hand-edit the weekly file;
  `scripts/log_myriad.py` guarantees Monday-of-week resolution, fuzzy dedup, atomic append, and
  read-back verification. Never claim an item was logged unless the receipt says `verified: true`.
  Trust is the whole point — if the user can't trust the file, the skill has failed even when the
  summary looks clean.
- **Always** include the git-status reminder. Not optional.
- **Respect the flow:** the user sees what's done, what's broken, and what needs their call,
  sees their git state, and safely defers everything else.
