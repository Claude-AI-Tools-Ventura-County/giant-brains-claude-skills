---
name: record-decision
description: >-
  Record or update durable decision records in a repo — the call, the
  assumption it bets on, the expected signal, reversibility, and a revisit
  trigger — then keep the record and the project docs current as findings
  arrive. Use ONLY when the choice clears the threshold: a meaningful bet
  that could be wrong, Costly or One-way-door reversibility, or a future
  signal worth checking. Above that threshold, trigger RECORD mode when the
  user says "record this decision", "log this", "write this down", commits
  to an option after weighing tradeoffs ("let's go with X" / "we're going
  with X"), or a decision emerges from take-a-step-back, iron-triangle,
  blast-radius, or bottom-line output. Trigger UPDATE mode when evidence
  arrives, an experiment concludes, an assumption is confirmed or broken, a
  recorded decision is reversed or superseded, or the user says "update the
  decision log" / "the migration worked" / "that bet didn't pay off". Never
  trigger for formatting, naming, lint-level, or five-minute-revert choices.
---

# Record Decision

Decisions evaporate. The framing, the tradeoff, the fragile assumption — all explicit in the chat at commit time, all gone a week later. This skill writes the bet down when it's made, then closes the loop when reality reports back. It is the suite's memory: the other skills produce sharp one-shot verdicts; this one makes them durable.

## Core idea

You are recording, not re-deciding. Pull the decision, the bet, and the reversibility read from what's already in the conversation — often directly from another skill's output (take-a-step-back's *most fragile assumption* becomes **The bet**; blast-radius's verdict becomes **Reversibility**; baseline-spec's metric becomes **Expected signal**). If a field is genuinely unknown, write `Unknown — [what would pin it down]` rather than faking it. This doubles as the quick-record path: a record filed at commit time with `Unknown` fields beats a complete record that never gets written — fill the gaps later via Updates. The minimum viable record states the Decision and the Reversibility; every other field may be `Unknown`. Don't block recording to interrogate the user for perfect metadata.

## Execution environment

If a writable repo is available, create and update the files directly. If not — chat-only contexts, read-only workspaces — produce the exact record content and its suggested path, and list the docs that should be updated. Never claim files were written unless they were. Harness-specific moves (offering `/schedule` for a revisit date) apply only where that harness is actually running.

## Where records live

- Use an existing decisions directory if the repo has one: `decisions/`, `docs/decisions/`, or `docs/adr/` — match the convention you find.
- Otherwise create `decisions/` at the repo root.
- One decision per file, named `YYYY-MM-DD-short-slug.md` (e.g. `2026-06-09-self-hosted-postgres.md`). If the filename already exists, prefer a more specific slug over a `-2` suffix.
- A decision spanning multiple repos lives once, in the repo that owns the change (or a dedicated org decisions repo if one exists); the other repos get the one-line link, never a copy.

## Record template

```markdown
---
status: Decided            # Decided | Validated | Revisited | Reversed | Superseded
date: YYYY-MM-DD
reversibility: Costly      # Easy | Costly | One-way-door
revisit: YYYY-MM-DD        # or a metric condition: "p95 > 200ms for 7d"
related: []                # optional: paths to superseded, superseding, or dependent records
decider: "@handle"         # optional: who owns the call (the DRI). Omit unless actually known — never invent a handle
---

# [Decision title — the call, not the topic]

**Decision:** [what was chosen, one line]

**The bet:** [the assumption this rides on — the thing that, if wrong, unwinds the decision]

**Rejected:** [the losing alternative — and the one-line reason it lost. Optional; include for Costly / One-way-door records, where re-deriving the decision boundary later would be expensive]

**Expected signal:** [the observable result that says the bet paid off] — by [date] or on [event: "when the v1 API deprecates"]

**Reversibility:** Easy | Costly | One-way door — [why, one line]

**Revisit trigger:** [a date or an event: "if p95 isn't under 200ms by Jul 15, reopen"]

## Updates
<!-- append-only, newest last -->
```

The frontmatter exists for scripts and agents — it makes records queryable without parsing prose ("find all Costly records not yet Validated"). The body exists for humans. Reversibility and the revisit trigger appear in both; keep them in agreement when updating. A metric-based `revisit` condition is preferable to a bare date when one exists — a scheduled check can evaluate it programmatically, and it never goes stale the way a calendar date does. The `related` array turns the log into a graph: "show every decision downstream of the Postgres migration" becomes one query.

Treat **status** as a strict finite state machine: `Decided` → `Validated` (signal arrived, bet paid off) | `Revisited` (trigger fired, under re-evaluation) | `Reversed` | `Superseded`. Use these exact strings only — never invent intermediate statuses like `Partially Validated` or `Pending Reversal`, and never embed prose in the field. When a record is superseded, the link to the superseding record goes in `related` and in a dated Updates line, not in `status`. If the evidence is partial, the status stays put and the nuance goes in an Updates line. The same exactness applies to `reversibility`: frontmatter uses one of `Easy | Costly | One-way-door` (hyphenated); the body writes it human-friendly ("One-way door").

## Mode 1 — Record

1. Fill the template from the conversation. Don't pad; don't invent.
2. Write the file to the decisions directory.
3. **Propagate to project docs.** Sweep the docs that state the affected approach — README, plan/spec docs, CLAUDE.md — and update any that now contradict the decision. The doc carries the *current state*; the *why* lives in the record. Link back with one line: `Decided in [decisions/2026-06-09-self-hosted-postgres.md]`. Never paste the full record into a doc — one source of truth. The link-back line is also the sweep convention: `grep -r "decisions/"` across the project docs finds every doc bound to a record, so future propagation is mechanical, not diligence-dependent. If a full sweep isn't feasible right now, the floor is a `## Decisions` section in the README linking to the decisions directory — a findable index beats silently stale docs.
4. Report coverage honestly, in three buckets: docs updated, docs checked and already consistent, docs likely affected but not checked. The third bucket is the one that matters — a vague "docs touched" hides exactly the staleness this skill exists to prevent.
5. If the revisit trigger is a date and you're in Claude Code, offer `/schedule` so the revisit is an appointment, not a hope.

## Mode 2 — Update

First find the record. "The migration worked" names an outcome, not a file:

- Search the decisions directory for matching slugs, titles, affected systems, and expected signals; prefer records whose status is `Decided` or `Revisited`.
- Exactly one plausible match → update it. Several → name the candidates and ask only if picking wrong would corrupt the log. None → say so, and offer a retrospective record with `Unknown` fields where the original context is gone.

Then, when a finding, outcome, or reversal lands:

1. Append a dated line to the record's **Updates** section: `- YYYY-MM-DD — [what happened, one line]`.
2. Flip **Status** only when the evidence justifies it — a promising early signal is an update, not a `Validated`.
3. **Never rewrite history.** The original bet stays exactly as written, even if it turned out wrong — *especially* if it turned out wrong. A decision log that's been retroactively cleaned up is worthless for calibration.
4. Re-propagate: if the outcome changes the current state (reversed, superseded), update the project docs again the same way.
5. **Automated signals count.** If automated evidence is available in the current environment — CI output, test results, a metric query, a scheduled check — treat it exactly like an operator-reported finding: append the update with its source (`- 2026-07-09 — nightly ETL run #412: zero timeout failures over 30 days — signal met`) and hold the same evidence bar before flipping status. This skill reads evidence that's present; it does not monitor in the background.

## This is not Claude's memory

Claude Code keeps its own memory (`MEMORY.md`, `CLAUDE.md`) and people reasonably ask what the difference is:

| | Claude's memory | Decision records |
|---|---|---|
| **Audience** | Claude, working with one operator | The team — humans and any future agent |
| **Lives** | In the operator's Claude setup | In the repo, versioned in git |
| **Content** | How to work: preferences, conventions, environment quirks | Why the system is shaped this way: the bet, the signal, the outcome |
| **Lifespan** | Until the preference changes | Permanent — the history *is* the value |

Rule of thumb: if a new teammate (human or agent) would need it to understand *why the project is the way it is*, it's a decision record. If it's about *how you like Claude to behave*, it's memory. When a decision is recorded, Claude's memory may hold a pointer to the decisions directory — never the record itself.

## When NOT to record

A choice with no real bet gets no file. "We went with the linter's default quote style" — Easy to reverse, no assumption at risk, no expected signal worth tracking. Recording it would bury the decisions that matter under ones that don't. The threshold: there's an assumption that could be wrong, or the reversibility is Costly or a One-way door. When the Easy/Costly line feels fuzzy in the moment, use this tiebreaker: **if undoing it would cost more than a day of focused work, record it.** When below threshold, say so in one line and move on.

## Example

> **Recorded:** `decisions/2026-06-09-self-hosted-postgres.md`
>
> **Decision:** Move the ETL pipeline to self-hosted Postgres on GCE.
> **The bet:** Ingest volume keeps growing past the managed tier's function timeouts — the timeout that broke the pipeline once will recur.
> **Expected signal:** Zero timeout-caused pipeline failures over 30 days of full-volume ingest — by 2026-07-09.
> **Reversibility:** Costly — migrating back is real work; keeping the schema portable keeps the door two-way.
> **Revisit trigger:** 2026-07-09, or sooner if ops burden exceeds ~2 hrs/week.
>
> **Docs touched:** `README.md` (architecture section now says self-hosted Postgres, links to the record), `docs/etl-plan.md` (managed-DB step replaced).

## Quality check before responding

- Is the bet falsifiable — could a future reading say "this was wrong"? If not, it's a description, not a bet; sharpen it.
- Does the expected signal have a by-when? A signal with no date never fires.
- Did every project doc that states the old approach get updated or listed? Stale docs that contradict the record are worse than no record.
- Is the Updates section append-only and dated? No edits above the line.
- Do the frontmatter scalars (status, reversibility, revisit) still agree with the body? A record that disagrees with its own frontmatter breaks every script that trusts it.
