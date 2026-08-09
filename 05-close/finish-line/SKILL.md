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

1. SOURCE. Reuse the clearest laundry list, done list, or completion criteria
   already in the conversation, task context, persistent project memory, or an
   earlier assistant response. A user list or accepted checklist supersedes an
   assistant-generated one. If none is available, use the relevant PRD, spec,
   plan, issue, or PR already known in context or memory; derive candidates
   only from that source. Do not ask the user to paste material already
   available. If no authoritative source is available, or sources conflict,
   ask exactly one question and stop:
   "What should define done: an existing PRD, spec, plan, issue, PR, or a
   numbered list?"
2. NARROW silently. Turn the candidate list into the smallest verifiable done
   list that closes the user's stated outcome. Keep only explicit, current
   commitments directly tied to that outcome; collapse duplicates and
   implementation details into one outcome item. Park every other candidate
   under the matching X rule. Do not ask the user to choose or confirm the
   narrowing, add new commitments, or re-scope the outcome.
3. AUDIT silently. Check each frozen item against the repo (met / not met).
   Collect any new findings. Apply the Severity Gate below.
4. PARK everything that does not pass the gate, using the PARKED File
   Protocol below. Zero exceptions; do not mention individual parked items
   in chat.
5. REPORT using the Chat Output format below. Nothing else.
6. CLOSE. After this turn the chapter is closed per the verdict. Never
   re-audit, re-open, or reframe any parked or frozen item unless the user
   explicitly asks to reopen or revisit it.

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

PARK BY DEFINITION (never report; park with the matching rule id):
- X1 Pre-existing on main and not worsened by this branch (including known
  robustness gaps; that is backlog, not this chapter).
- X2 Missing enhancements, refactors, naming, docs, tests for hypotheticals,
  thresholds, observability wishes, machinery hygiene, architecture taste.
- X3 Anything worded as "if someday / as it grows / should have".
- X4 Anything that is a decision rather than a defect.
- X5 Anything without file:line evidence.

Gate mechanics:
- Burden of proof is on INCLUSION. If unsure whether a code is satisfied,
  it is not satisfied → park.
- A pre-existing issue may be reported ONLY if it meets C1–C4 on main today;
  flag it PRE-EXISTING, do not add it to scope; cap: one per run.
- Use X1 only after confirming the finding is pre-existing on main and not
  worsened here. If that comparison is uncertain, use the supported X code;
  use X5 when evidence is insufficient.

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
schema: finish-line/parked/v1
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
- evidence: <file:line, or "none">
- summary: <one sentence, ≤ 40 words>
- revisit_when: <one concrete, checkable trigger condition, or "never">
```

R-ids are zero-padded and assigned in run-creation order; P-ids are
zero-padded and assigned in finding-notice order.

## Chat Output (exact; nothing before or after)

```
CLOSED: yes|no — <one clause>
DONE LIST: <source already in context, or file path>
#1 met|not met — reason (file:line)
...
NEW BLOCKING FINDINGS: none | <code> <file:line> — <one-sentence proof>
PARKED: <n> item(s) → PARKED/<filename> (R-<id>)
```

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
