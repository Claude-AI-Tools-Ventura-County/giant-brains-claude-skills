---
name: finish-line
description: >
  Use when the user asks to close, wrap up, finalize, ship, or define "done"
  for a plan, chapter, PR, milestone, or project; or says any of:
  "finish line", "definition of done", "done list", "stop adding scope",
  "no new items", "wrap it up", "close the chapter". Runs a bounded closure
  audit: reports only objective Critical/High blockers and parks everything
  else deterministically in /PARKED. Overrides any default urge to re-audit
  or expand scope.
---

# Finish Line

A bounded closure protocol. Its job is to END work, not to discover work.
A supplied laundry list is source material, not an automatic finish line.
Discovery and narrowing happen once, here, under a strict gate; everything
that does not pass the gate is parked deterministically and never re-raised.

## Protocol (exact order)

1. SOURCE. Pick the highest-precedence candidate available, in this order:
   (a) an explicit user-stated done/completion list in this conversation —
   if the user has stated more than one, the most recent supersedes earlier
   ones; (b) a checklist the user has already accepted or confirmed, even if
   assistant-drafted; (c) an authoritative PRD, spec, plan, issue, or PR
   already known in context or memory; (d) an assistant-generated summary
   with no user confirmation. Derive candidates only from the selected
   source. Do not ask the user to paste material already available.
   Two sources CONFLICT only when they sit at the same precedence tier and
   name different outcomes — not when one is just more detailed or granular
   than the other; merge same-outcome sources instead of picking one. If no
   source is available at any tier, or two same-tier sources conflict, ask
   exactly one question and stop:
   "What should define done: an existing PRD, spec, plan, issue, PR, or a
   numbered list?"
   The list FREEZES at this step. Work completed after the freeze does not
   extend it, and a later "are we done?" does not re-run SOURCE.
2. NARROW silently. Turn the candidate list into the smallest verifiable done
   list that closes the user's stated outcome. Keep only explicit, current
   commitments directly tied to that outcome; collapse duplicates and
   implementation details into one outcome item. Park every other candidate
   under the matching X rule — a candidate that is a legitimate requirement
   but simply not needed for this closure parks under X4: narrowing scope is
   itself a decision, not a defect. Do not ask the user to choose or confirm
   the narrowing, add new commitments, or re-scope the outcome. A release
   ledger, if one exists, is not an input here (see Release Context below).
3. AUDIT silently. Check each frozen item against the repo (met / not met).
   Collect any new findings. Apply the Severity Gate below.
4. PARK everything that does not pass the gate, using the PARKED File
   Protocol below. Zero exceptions; do not mention individual parked items
   in chat.
5. REPORT using the Chat Output format below. Nothing else.
6. CLOSE. After this turn the chapter is closed per the verdict. Never
   re-audit, re-open, or reframe any parked or frozen item unless the user
   explicitly asks to reopen or revisit it.
   This binds every later turn, not just this one. A follow-up such as "are we
   done?", "is that everything?", "will this close it?", or "anything else?"
   is answered by restating the existing verdict — it is not a new audit and
   must not produce a candidate that was not in the frozen list. Re-entry is
   the failure mode this skill exists to prevent; the Severity Gate only
   bounds a single pass, this step bounds the number of passes.

## Release Context (optional sub-routine — never a gate)

Many repos keep a forward-looking release ledger with named goal posts. When
one exists, naming the release that closure is running against costs one line
and tells the reader which goal post the verdict belongs to.

This sub-routine is **display-only**. Its entire output is the `RELEASE:` line.
It never reads into the done list, never changes what is frozen, parked, or
reported, and never blocks. A repo with no ledger produces byte-identical
output to a version of this skill without the sub-routine. Whenever a step
below does not resolve cleanly, skip the whole sub-routine silently — an
unlabelled close is always correct; a mislabelled one is not.

DISCOVER. Look in exactly two places at repo-root
(`git rev-parse --show-toplevel`; fallback: current directory):
`RELEASES.md`, then `MILESTONES.md`. First one found wins. No directory walk,
no fuzzy matching, no ROADMAP.md fallback — a queue ledger is not a milestone
doc. Neither present → skip silently and never mention it.

SELECT one block, or none.

A block starts at a line beginning `Release:` and runs to the next such line
or end of file. Do **not** split on blank lines: real ledgers omit the blank
line between blocks, which would merge two releases into one block carrying
two `Release:` values and make the selected label ambiguous.

A block is a candidate only if it is outside HTML comments, has a concrete
`Release:` value (not empty, `TBD`, `none`, or `-`), and has no shipped
`Status:` (Shipped / Released / Done / Complete). A block with no `Status:`
field counts as unshipped. Then:
- If the user named a release or codename, use the block whose `Release:` or
  `Codename:` matches. This is the only fully reliable signal and it always
  wins. No match → skip silently.
- Otherwise, among candidates carrying a parseable `Target Date:`, take the
  **earliest** date. Releases ship in date order, so the earliest unshipped
  target is the one in flight. Include overdue dates: a release that slipped
  yesterday is exactly when the label is most useful, and the printed date
  shows the reader the slip.
- If no candidate carries a parseable `Target Date:`, or two or more tie for
  earliest — **skip silently**. Both are common; neither is a defect.
- Never rank by file order or version number. A ledger is not reliably sorted:
  a real one in use today lists `1.5.0` above `1.4.270`, with both actively
  worked. There is no ordering convention to lean on, and inventing one to
  make the rule terminate is how a confident wrong label gets printed.
- Every branch above terminates in a named block or a silent skip. There is no
  judgement call left to the agent — if you find yourself weighing which
  release "feels" active, the rule has already said skip.

HARD LIMITS:
- Never a SOURCE candidate at any tier. The ledger is forward-looking
  planning, not an accepted done list; its `Description` prose is intent, not
  a frozen commitment. If it disagrees with the selected SOURCE, the SOURCE
  wins silently — this is not a same-tier conflict and never triggers the
  Step 1 question.
- Never an input to NARROW. The ledger must not be used to argue that a
  candidate belongs to a later release and can therefore be dropped: a
  mis-selected block would silently delete real work from the frozen list and
  report a clean close over it. Scope exclusions come from the user's stated
  outcome alone.
- Never adds to or removes from the frozen list, and never changes a
  met/not-met call.
- Never affects `revisit_when` or any other PARKED field. Parked entries are
  written exactly as they would be without a ledger.
- Never blocks closure. A missed target date, an empty `Milestone:`, a stale
  or self-contradicting ledger, and a ledger that disagrees with the repo are
  all invisible here — not a finding, not a HIGH, not even a parked item.
  Auditing the ledger is a different job than closing against it.
- Never writes to the ledger.

## Severity Gate — the only definitions that exist

A finding may enter chat ONLY if it satisfies one code below verbatim,
with evidence. Anything else is parked.

CRITICAL (blocks closure):
- C1 Loss or corruption of persisted, acknowledged-written data,
  reproducible on this branch.
- C2 Security: unauthorized access, privilege escalation, secret leak,
  injection.
- C3 Unintended crash, unhandled rejection, or hang on a path reachable in
  the current production configuration.
- C4 Silent wrong output on a primary path (wrong data, no error signal).

HIGH (reported; user decides fix-now or park):
- H1 Regression introduced by this branch vs main; cite the diff hunk or a
  failing test.
- H2 Violates an explicit requirement quotable from the issue/PR/spec text;
  quote it.
- H3 A frozen done-list item is not actually met; show file:line.
- H4 Loud failure on a primary path with no recovery, requiring manual
  intervention.
- H5 Latent defect in code on this branch that would meet C1–C4 if a config
  value that exists and is settable TODAY were changed; name the exact knob
  and its current value, and cite file:line. Unreachable in the current
  configuration is why this is HIGH and not CRITICAL: it is surfaced for a
  decision and can be deferred under X6, where a CRITICAL cannot.

PARK BY DEFINITION (never report; park with the matching rule id):
- X1 Pre-existing on main and not worsened by this branch (including known
  robustness gaps; that is backlog, not this chapter).
- X2 Missing enhancements, refactors, naming, docs, tests for hypotheticals,
  thresholds, observability wishes, machinery hygiene, architecture taste.
- X3 Anything worded as "if someday / as it grows / should have".
- X4 Anything that is a decision rather than a defect, including a candidate
  that would be legitimate elsewhere but is not required to close this
  specific outcome (a NARROW-stage scope exclusion, not an AUDIT-stage
  defect call).
- X5 Anything without file:line evidence.
- X6 A reported HIGH the user chose to defer. Assigned only by the post-report
  deferral below — never during an audit pass, and never to a CRITICAL.

Gate mechanics:
- Burden of proof is on INCLUSION. If unsure whether a code is satisfied,
  it is not satisfied → park.
- A pre-existing issue may be reported ONLY if it meets C1–C4 on main today;
  flag it PRE-EXISTING, do not add it to scope; cap: one per run.
- Use X1 only after confirming the finding is pre-existing on main and not
  worsened here. If that comparison is uncertain, use the supported X code;
  use X5 when evidence is insufficient.
- H5 is the one exception to "unsure → park", and it is narrow: the knob must
  exist and be settable today, and you must state it. A toggle that would have
  to be built first is X3; a knob you cannot name is X5. H5 exists because
  "not firing right now" and "not a defect" are different claims, and parking
  the first as the second is how a real bug ships inside a clean close.

## Post-report HIGH deferral (the only permitted follow-up)

When the user says `park H<code> from this run` or names a run as
`park H<code> from PARKED/<filename> R-<id>`, do not re-audit. Append that
reported HIGH item to its original run with `exclusion_rule: X6
(user-deferred)`, increase only that run's `parked_items`, and return the
follow-up output below. If a filename has multiple runs and the user did not
identify one, ask exactly one question naming the available run ids. Do not
otherwise reopen, extend, or reframe the audit.

```
CLOSED: yes|no — <one clause>
PARKED: 1 item → PARKED/<filename> (R-<id>)
```

## PARKED File Protocol (deterministic — never invent names or formats)

What these files are for: a durable, uniform record that survives the
conversation, so a parked item can be found later by date, repo, rule, or
anchor and linked to the plans and issues that do the real work. They are
nodes in a project graph — not plans, specs, PRDs, or backlogs. Every field
below is either an identifier or an edge. The moment an entry starts
explaining, justifying, or sequencing, it has stopped being a node.

Location: `<repo-root>/PARKED/` — create the folder if missing.
repo-root = `git rev-parse --show-toplevel`; fallback: current directory.

Filename: `YYYY-MM-DD-<reponame>-HHMM.md`
- YYYY-MM-DD: local calendar date at invocation.
- reponame: basename of repo-root, lowercased; every run of non-[a-z0-9]
  replaced by one `-`; leading/trailing `-` stripped.
- HHMM: local 24-hour zero-padded hour+minute at invocation (14:05 → 1405).
- Example: `2026-08-08-reminders-service-1430.md`
- Create one file for every audit run, including a run with zero parked items.
- If the exact filename already exists, append a new run to `## Runs`, assign
  the next R-id and P-id, and never create a variant name. Keep each run's
  counts separate; never change another run's counts.

Content: exactly this template, fields in this order, no extra fields,
no free prose, no additional files (no README, no index):

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
- claimed_severity: <what this was tempted to be called, e.g. "robustness gap">
- exclusion_rule: <X-code verbatim, e.g. X1>
- evidence: <exactly one file:line, or "none">
- summary: <one sentence, ≤ 40 words>
- remediation: <one sentence, ≤ 20 words — direction only, or "unknown">
- issue: <existing #N or URL, or "none">
- revisit_when: <one concrete, checkable trigger condition, or "never">
```

R-ids are zero-padded and assigned in run-creation order; P-ids are
zero-padded and assigned in finding-notice order.

Field discipline — these three fields are the ones that grow into a plan doc
if left unbounded, so bound them:

- `evidence` is ONE `file:line` — the single most load-bearing location, not
  the first one found, not a range, not a list. A concrete defect that
  recurs at multiple call sites still has one most load-bearing anchor: cite
  that site as `evidence` and use `remediation` to flag the recurrence (e.g.
  "apply the same fix at every call site matching X") — it is not lost, just
  pointed at through one exemplar. Reserve `evidence: none` under X2 for
  genuinely diffuse themes with no concrete instance to anchor to (naming,
  architecture taste, observability wishes) — not for a real bug that merely
  has more than one location.
- `remediation` names a direction, not a solution: "gate it behind the same
  coverage check", "reset the shared global in teardown". It exists so a
  reader knows which way to walk, not so they can skip the thinking. No
  steps, no options, no rationale, no code, no second sentence.
- `issue` is only for a tracker item that ALREADY exists. Never file one to
  populate the field, and never write "should file one" — that is a decision
  (X4) and it belongs to the user, not the audit.

When an item will not fit these bounds, the answer is to file a GitHub issue
and put its number in `issue` — never to expand the entry. The PARKED file is
a set of pointers into the work, not a description of it.

## Chat Output (exact; nothing before or after)

```
CLOSED: yes|no — <one clause>
RELEASE: <release> (<codename>) — target <date>
DONE LIST: <source already in context, or file path>
#1 met|not met — reason (file:line)
...
NEW BLOCKING FINDINGS: none | <code> <file:line> — <one-sentence proof>
PARKED: <n> item(s) → PARKED/<filename> (R-<id>)
```

The `RELEASE:` line is the only optional line in this block. Print it when the
Release Context sub-routine selected a block; **omit the line entirely** —
not blank, not "none" — when there is no ledger or no block was selected.
Drop any field the block leaves empty (`0.71.0 (Daily Driver)` with no target
date; `0.71.0 — target 2026-10-15` with no codename). It is a label, never a
verdict: it does not explain, justify, or state progress against the release.

Set CLOSED to `no` if any CRITICAL or undecided HIGH from that run remains.
Set it to `yes` only when neither exists, or when every HIGH was deferred
under X6. A CRITICAL item cannot be deferred under this protocol.

After the PARKED line: stop. No rules restated, no summaries, no suggestions,
no questions.

## Counter-example — do not invoke

Do not fire when the user is asking to complete active work, even if they use
"finish" casually. For example, "finish implementing the export and commit
it" is an implementation request, not a closure audit; do the requested work
instead.

## Anti-patterns this skill forbids

- Leading with gaps before the verdict.
- Re-raising anything parked, in this or any later turn.
- Treating "will this close it?" as an open-ended audit invitation.
- Reporting severity by vibe ("important", "should", "risky") instead of code.
- Creating any file other than the single PARKED file for this run.
- Answering a repeated "are we done?" with a fresh sweep instead of the
  standing verdict. Each re-ask that surfaces one more item teaches the user
  that closure is unreachable, which is worse than any item it finds.
- Downgrading a latent defect to X-park because it is not firing today. That
  is H5, and H5 is reported.
- Treating a release ledger as the done list, or letting its `Description`
  prose add an item the frozen list never had.
- Reporting on the ledger itself — a slipped target date, an empty field, a
  block that disagrees with the repo. Closing against a release is not
  auditing the release plan.
- Asking which release is in flight. The selection rule is deterministic; if
  it does not resolve, the sub-routine is skipped, not escalated to a question.
- Growing a PARKED entry past its field caps, or adding structure to a PARKED
  file — sub-bullets, priorities, sequencing, effort estimates, owners,
  status. A parked file that reads like a plan has become one.
