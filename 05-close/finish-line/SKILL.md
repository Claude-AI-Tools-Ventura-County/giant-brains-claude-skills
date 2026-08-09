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
Discovery happens once, here, under a strict gate; everything that does not
pass the gate is parked deterministically and never re-raised.

## Protocol (exact order)

1. FREEZE. The done list is whatever the user provides in the invoking
   message. If none is provided, ask exactly one question and stop:
   "Paste the frozen done list (numbered, one line per item)."
   Do not infer, extend, or re-scope the list yourself.
2. AUDIT silently. Check each frozen item against the repo (met / not met).
   Collect any new findings. Apply the Severity Gate below.
3. PARK everything that does not pass the gate, using the PARKED File
   Protocol below. Zero exceptions; do not mention individual parked items
   in chat.
4. REPORT using the Chat Output format below. Nothing else.
5. CLOSE. After this turn the chapter is closed per the verdict. Never
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
- If the user later chooses to defer a reported HIGH item, park it with
  exclusion_rule: X6 (user-deferred).

## PARKED File Protocol (deterministic — never invent names or formats)

Location: `<repo-root>/PARKED/` — create the folder if missing.
repo-root = `git rev-parse --show-toplevel`; fallback: current directory.

Filename: `YYYY-MM-DD-<reponame>-HHMM.md`
- YYYY-MM-DD: local calendar date at invocation.
- reponame: basename of repo-root, lowercased; every run of non-[a-z0-9]
  replaced by one `-`; leading/trailing `-` stripped.
- HHMM: local 24-hour zero-padded hour+minute at invocation (14:05 → 1405).
- Example: `2026-08-08-reminders-service-1430.md`
- If the exact filename already exists, append to its `## Items` section and
  continue the P-id sequence; never create a variant name. Keep
  `created_local` unchanged and update `frozen_items` and `parked_items` to
  their cumulative totals across every run in that file.

Content: exactly this template, fields in this order, no extra fields,
no free prose, no additional files (no README, no index):

```
---
schema: finish-line/parked/v1
created_local: YYYY-MM-DDTHH:MM
repo: <reponame>
frozen_items: <count>
parked_items: <count>
---

# Parked — YYYY-MM-DD HH:MM — <reponame>

## Items

### P-001 — <short title, ≤ 8 words>
- claimed_severity: <what this was tempted to be called, e.g. "robustness gap">
- exclusion_rule: <X-code verbatim, e.g. X1>
- evidence: <file:line, or "none">
- summary: <one sentence, ≤ 40 words>
- revisit_when: <one concrete, checkable trigger condition, or "never">
```

Ids zero-padded three digits, assigned in the order items were noticed.

## Chat Output (exact; nothing before or after)

```
DONE LIST:
#1 met|not met — reason (file:line)
...
NEW BLOCKING FINDINGS: none | <code> <file:line> — <one-sentence proof>
PARKED: <n> item(s) → PARKED/<filename>
CLOSED: yes|no — <one clause>
```

After the CLOSED line: stop. No rules restated, no summaries, no
suggestions, no questions.

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
