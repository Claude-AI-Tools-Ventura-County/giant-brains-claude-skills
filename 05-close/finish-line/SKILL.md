---
name: finish-line
description: >
  Use when the user asks to close, wrap up, finalize, ship, or define "done"
  for a plan, chapter, PR, milestone, or project; or says any of:
  "finish line", "definition of done", "done list", "stop adding scope",
  "no new items", "wrap it up", "close the chapter". Recommends the shortest
  safe path from the current branch to the next checkpoint: remaining work,
  governance compliance, and ship-safety blockers only — everything else is
  parked in /PARKED for later pickup, never narrated in chat.
---

# Finish Line

The job is to hand the user a clear, safe path to a clean finish line —
an expedient arrival at the next checkpoint (milestone or release). A clean
finish line means exactly three things:

1. The current branch's work (its GH issue, task, or stated outcome) is
   fully completed — done and done.
2. The repo's doc-governance systems are fully complied with. No shortcuts.
3. Everything non-mandatory is dropped from chat — FYIs, nice-to-knows,
   and especially narration of what the LLM did recently. Dropped detail
   is captured in the PARKED file so work can be picked up later; it is
   never spent in the user's chat window.

This skill is forward-looking only. It reports what REMAINS, never what
happened. It is not a retrospective, not a changelog, not a summary of
recent activity. The user is focused on getting to the finish line; every
line of output must move them toward it.

## Protocol (exact order)

1. SOURCE. What defines done for this branch? Pick the highest-precedence
   candidate available: (a) an explicit user-stated done list in this
   conversation (most recent wins); (b) a checklist the user has accepted or
   confirmed, even if assistant-drafted; (c) an authoritative PRD, spec,
   plan, issue, or PR already known in context or memory; (d) an
   assistant-generated summary with no user confirmation. Merge same-outcome
   sources; two sources conflict only at the same tier naming different
   outcomes. If no source exists at any tier, or same-tier sources conflict,
   ask exactly one question and stop:
   "What should define done: an existing PRD, spec, plan, issue, PR, or a
   numbered list?"
   The done list FREEZES here. Later work does not extend it; a later
   "are we done?" does not re-run SOURCE.

2. CHECKPOINT. Identify the goal post the path leads to.
   - Look for `RELEASES.md`, then `MILESTONES.md`, at repo-root
     (`git rev-parse --show-toplevel`; fallback: current directory). First
     found wins; no directory walk, no ROADMAP.md fallback.
   - In the ledger, a block starts at a line beginning `Release:` and runs
     to the next such line or end of file (never split on blank lines). A
     candidate block has a concrete `Release:` value (not empty/TBD/none/-),
     sits outside HTML comments, and has no shipped `Status:` (Shipped /
     Released / Done / Complete; no `Status:` field = unshipped).
   - If the user named a release or codename, that block wins. Otherwise
     take the candidate with the earliest parseable `Target Date:`
     (overdue included — a slipped date is when the label matters most).
   - If the ledger exists but selection is ambiguous (no dates, tied
     dates, no match), ask one short question naming the candidate
     releases. If no ledger exists, the checkpoint is the branch's own
     stated task — say so and continue; do not ask.
   - The checkpoint is a destination label only. Its prose never adds to
     or removes from the frozen done list, and a stale or self-contradicting
     ledger is not a finding — closing against a checkpoint is a different
     job than auditing the release plan.

3. ASSESS silently. Establish where the branch stands:
   - Branch identity: `git branch --show-current`; ahead/behind the local
     trunk (`main`, else `master`) via `git rev-list --left-right --count`.
     Facts for the opening line, never a progress judgement.
   - Each frozen done-list item: met or not met, against the repo.
   - Governance obligations: discover the repo's own doc rules (CLAUDE.md /
     AGENTS.md directives, PDDA lifecycle if `utils/pdda/` exists, CHANGELOG
     and ROADMAP conventions, issue-doc sync, README update rules) and
     determine which steps this close still owes.
   - Ship-safety: note any Mandatory-bar item 3 finding encountered while
     assessing. Do not launch an open-ended defect sweep; the frozen list
     bounds the looking.

4. PARK. Everything that fails the Mandatory Bar goes into the PARKED file
   (protocol below), with enough detail for an easy pickup later. Zero
   exceptions, and no individual parked item is mentioned in chat.

5. RECOMMEND. Deliver the Chat Output below. Nothing else.

6. CLOSE. The recommendation stands. A follow-up like "are we done?",
   "is that everything?", or "anything else?" is answered by restating the
   standing path (minus steps since completed) — it is not a new audit and
   must not surface a candidate the frozen list never had. Re-entry is the
   failure mode this skill exists to prevent. Reopen only when the user
   explicitly asks to reopen or revisit.

## The Mandatory Bar — the only things that reach chat

A step may appear in the recommendation ONLY if it is one of:

1. REMAINING WORK — a frozen done-list item not yet met. Cite file:line
   for the not-met call.
2. GOVERNANCE — a doc-governance step the repo's own rules require for
   this close (changelog entry, roadmap reconciliation, PDDA issue-doc
   sync, README table update, ...). Governance steps are never droppable
   and never shortcut: cite the rule's source file.
3. SHIP-SAFETY — a defect that makes shipping unsafe: loss/corruption of
   persisted data, a security hole (unauthorized access, secret leak,
   injection), a crash/hang on a reachable path, or silent wrong output on
   a primary path. Requires file:line evidence. Burden of proof is on
   inclusion: unsure → park. A pre-existing trunk defect may appear only
   if it meets this bar on the trunk today; flag it PRE-EXISTING; cap one
   per run.

Everything else — enhancements, refactors, naming, hypothetical-future
concerns, observability wishes, "should have" items, decisions rather than
defects, anything without evidence — is parked, not reported. A latent
defect that would meet the ship-safety bar under a config knob that exists
and is settable today is mandatory (name the knob, cite file:line); a
defect behind a toggle that would have to be built first is parked.

## Chat Output — plain chat, never a code block or file

The output is written INTO the chat window as normal prose the user can
read at a glance. Never wrap it in a fenced code block, never write it to
a .md file, never format it as a machine report.

Shape (target: under ~15 lines total):

- One opening line of fact: branch, checkpoint, and the verdict — e.g.
  "Branch `feat/export-v2` (14 ahead / 2 behind main), targeting
  **1.5.0 (Daily Driver)** — 3 steps remain to a clean finish." Or, when
  nothing remains: "...— at the finish line; nothing remains."
- Then: "Based on what I have, here's what I recommend to reach
  <checkpoint>:" followed by a short numbered list — one line per step, in
  execution order (remaining work → ship-safety fixes → governance), each
  with its file:line or rule-source anchor. Steps only; no rationale
  paragraphs, no options, no alternatives.
- Last line: "Parked <n> item(s) for later → PARKED/<filename> (R-<id>)."
- Stop. No summaries, no suggestions, no restated rules, no questions.

Forbidden in this output, verbatim wall-of-text killers:
- Any account of completed work beyond the single opening fact line — no
  "what landed", no "what was worth keeping", no judgement calls narrated,
  no diff statistics, no story of the session.
- FYIs of any kind. If it isn't a numbered step toward the checkpoint,
  it doesn't appear.
- Headers, sections, tables, or nested bullets. One fact line, one list,
  one parked line.

## Post-report step deferral (the only permitted follow-up)

When the user says `park step <n>` (or names a run: `park step <n> from
PARKED/<filename> R-<id>`), do not re-assess. A REMAINING-WORK or
SHIP-SAFETY step moves to its run's PARKED file with `exclusion_rule: X6
(user-deferred)`; bump that run's `parked_items`; reply with the updated
one-line verdict and the parked line only. A GOVERNANCE step cannot be
deferred — no shortcuts on governance is definitional. Do not otherwise
reopen, extend, or reframe the path.

## PARKED File Protocol

What these files are for: a durable record that survives the conversation,
detailed enough that parked work can be picked up and restarted later
without re-deriving context — while keeping the user's chat window clean.
Detail belongs HERE, not in chat.

Location: `<repo-root>/PARKED/` — create the folder if missing.
repo-root = `git rev-parse --show-toplevel`; fallback: current directory.

Filename: `YYYY-MM-DD-<reponame>-HHMM.md`
- YYYY-MM-DD: local calendar date at invocation.
- reponame: basename of repo-root, lowercased; every run of non-[a-z0-9]
  replaced by one `-`; leading/trailing `-` stripped.
- HHMM: local 24-hour zero-padded hour+minute (14:05 → 1405).
- Example: `2026-08-08-reminders-service-1430.md`
- One file per run, including a run with zero parked items. If the exact
  filename exists, append a new run under `## Runs` with the next R-id;
  never create a variant name, never change another run's counts.

Content template (fields in this order; no additional files):

```
---
schema: finish-line/parked/v2
created_local: YYYY-MM-DDTHH:MM
repo: <reponame>
---

# Parked — YYYY-MM-DD HH:MM — <reponame>

## Runs

### R-001 — YYYY-MM-DDTHH:MM
- frozen_items: <count>
- parked_items: <count>

#### P-001 — <short title, ≤ 8 words>
- claimed_severity: <what this was tempted to be called>
- exclusion_rule: <X-code, see below>
- evidence: <most load-bearing file:line, or "none">
- summary: <what it is and why it was dropped from this close — enough
  detail to restart cold, a few sentences is fine>
- remediation: <the direction a restart would take; recurrence notes
  ("same fix at every call site matching X") welcome>
- issue: <existing #N or URL, or "none" — never file one to fill this>
- revisit_when: <one concrete, checkable trigger condition, or "never">
```

Exclusion rules (park reason codes):
- X1 Pre-existing on trunk and not worsened by this branch.
- X2 Enhancement, refactor, naming, docs-beyond-governance, tests for
  hypotheticals, observability wish, architecture taste.
- X3 Hypothetical-future ("if someday / as it grows / should have").
- X4 A decision rather than a defect, including scope narrowed out of
  this close.
- X5 Insufficient evidence to meet the Mandatory Bar.
- X6 A reported step the user chose to defer (assigned only by the
  post-report deferral above; never to a governance step).

R-ids and P-ids are zero-padded, assigned in order. Entries should be as
detailed as a restart needs — but they are still entries, not plan docs:
when one wants to become a plan, that is the user's call, not the audit's.

## Counter-example — do not invoke

Do not fire when the user is asking to complete active work, even if they
use "finish" casually. "Finish implementing the export and commit it" is an
implementation request, not a closure path; do the requested work instead.

## Anti-patterns this skill forbids

- The wall of text: narrating what landed, what was salvaged, what
  judgement calls were made, diff stats, session history. The user needs
  the path forward, not the story so far — 75% of that information is
  useless to them.
- Emitting the recommendation as a fenced code block, a template dump, or
  a written .md file. Output is readable chat prose.
- Re-raising anything parked, in this or any later turn, unless the user
  explicitly reopens it.
- Answering a repeated "are we done?" with a fresh sweep instead of the
  standing path. Each re-ask that surfaces one more item teaches the user
  that the finish line is unreachable.
- Shortcutting or deferring a governance step. Compliance is part of the
  definition of clean.
- Reporting a "risk" or "concern" without file:line evidence — that is a
  parked FYI wearing a costume.
- Treating the release ledger as the done list, or letting its prose add
  an item the frozen list never had; reporting on the ledger itself (a
  slipped date, an empty field) instead of closing against it.
- Growing chat output past the one-fact-line + steps + parked-line shape:
  no headers, no sections, no alternatives per step.
