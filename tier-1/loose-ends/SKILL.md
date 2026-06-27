---
name: loose-ends
description: |
  Post-work completeness sweep: check what was forgotten before declaring existing work done. Use only after work exists: a diff, draft, or completed change session. Compare what was delivered against what was requested, then look for dropped requirements, sibling surfaces still saying the old truth (docs, READMEs, changelogs, configs, counts, install scripts), verification claimed but not rerun after the last edit, and leftover scaffolding such as debug prints, skipped tests, TODOs, or hardcoded test values.

  Trigger when the user asks “what did I forget,” “did I miss anything,” “is this done,” “ready to ship/PR?”, or is about to call a multi-file or multi-requirement task complete. Also self-trigger before reporting substantial multi-step work finished.

  Do not trigger before work exists; if the question is about a plan, decision, or approach, route to take-a-step-back. Do not use for phased-plan QA (phase-qa) or line-by-line code review (/code-review). This skill hunts what is absent, not what is wrong.
---

# Loose Ends

Sweep the gap between what was asked and what was delivered — before "done" is said out loud.

This is the suite's post-work counterpart to take-a-step-back. The decision skills guard the moment *before committing*; this one guards the moment *before declaring done*. Work rarely ends where the request did: a requirement falls out mid-session, a README still states the old count, a "tests pass" was true three edits ago, a debug print is still in the handler. The skill's job is to enumerate those absences with evidence — or to clear the work to ship in one line.

## Core idea

Answer one question: *what did I forget?*

The scope is the **delta between the contract and the delivery** — things that should exist and don't. It is explicitly not a review of what *does* exist: code that is present but wrong belongs to /code-review; prose that is present but verbose belongs to bottom-line. This skill hunts the absent, not the broken.

## How this differs from its siblings

- **take-a-step-back** (before the work) — "Am I making the best decision possible?" Challenges the frame before commitment. If the user asks "what am I missing?" about a plan or approach and no work exists yet, that question belongs there, not here.
- **phase-qa** (around a plan doc) — bakes QA checklists into a phased planning doc and gates its phases. loose-ends needs no plan doc at all; it sweeps ad-hoc work against the original ask.
- **/code-review** (on what's present) — finds bugs in delivered code. loose-ends finds the test that was never written, not the assertion that's wrong.
- **bottom-line / linear** (compression) — reshape what's already there. They cannot surface what's absent.

## Method — reconstruct, inventory, cross off

1. **Reconstruct the contract.** Re-read the original request — and any plan doc, ticket, or acceptance list it pointed at. List every named deliverable, *including the throwaway clauses* ("oh, and make sure it doesn't time out"). Those are the ones that get dropped.
2. **Inventory the delivery.** `git diff` / `git status` for code; the artifact itself for prose or config. What actually changed, in which files?
3. **Cross off and sweep.** Match each contract item against the inventory, then run the sweep list below over the changed surface only.

## What to sweep for

- **Dropped requirements** — named in the ask, absent from the diff.
- **Stale sibling surfaces** — the README, changelog, docs page, config, install script, CI job, or count that mirrors the changed thing and still states the pre-change truth. Grep for the old name, the old number, the old path.
- **Unrun verification** — every "tests pass" / "build works" / "verified" claimed during the session: was the command actually run *after the last edit*? Stale verification is unverified.
- **Leftover scaffolding** — TODO/FIXME, debug prints, `debugger`, `.only`/`.skip`, commented-out blocks, hardcoded test values — scanned in the changed files only.
- **Unhandled edges** — for newly written code only: the empty, null, and error paths the happy-path session never exercised.
- **Cleanup and comms** — files created and abandoned, the down-migration for the up-migration, the version bump, the person or channel that needs telling.

## Output format

Lead with the verdict — the one line that survives skimming:

> **3 loose ends — 2 block "done."** — or — **Swept clean — nothing forgotten. Ship it.**

**Contract:** [One line: what the work promised, sourced from the original ask — not from what got built.]

**Loose ends:** (omit entirely on a clean sweep)
1. **[The missing thing]** *(blocks done | worth closing)* — where it should live, the evidence it's absent, and the one-line close-out.

Order blocking-first. *Blocks done* means the original ask is not met without it; *worth closing* means "done" survives, but the operator should ship with it open consciously, not accidentally.

**Also checked:** [Optional, one line — the sweep classes that came back clean, so a short list isn't mistaken for a short look.]

## Principles

**Absence needs an address.** Every finding names where the missing thing should live and the evidence it isn't there. "You should probably add tests" with no pointer is vibes, not a finding.

**Evidence or silence.** Report only what the diff, a grep, or the session transcript can show. If you can't see the work — no diff, no artifact, no transcript — say what you need and stop; never sweep from imagination.

**"Ship it" is a verdict, not a failure.** A clean sweep ends in one line. Never invent a finding to justify firing — a skill that always finds something is a skill nobody believes.

**Hunt the absent, not the wrong.** Re-reviewing delivered code for bugs is scope creep into /code-review. If you notice a bug in passing, hand it off in one clause; don't make it a finding.

**The contract is the request, not your taste.** Don't flag features nobody asked for. The two exceptions are stale sibling surfaces and leftover scaffolding — nobody asks for those either, but "done" implies them.

**Blocking-first, always tagged.** The operator should be able to close item 1, consciously defer item 3, and ship — without re-reading anything.

## Scaling

- **Single-file, single-ask change** → sweep silently, report the verdict in one line either way.
- **Multi-file or multi-requirement work** → the full format, blocking-first.
- **Agent-completed work the user didn't watch** → weight the unrun-verification class heaviest; claims made mid-session decay fastest.
- **No visible work** (no diff, nothing pasted, nothing in session) → refuse the sweep and name what you need — or route to take-a-step-back if the work simply hasn't started.

## Example 1 — a feature that feels finished

Input (abridged): "I think the CSV export feature is done — did I forget anything?" (Original ask, earlier in session: "add CSV export for the transactions table — filterable by date range, and make sure big exports don't time out.")

Output:

> **4 loose ends — 2 block "done."**
>
> **Contract:** CSV export for transactions, filterable by date range, safe on large exports.
>
> **Loose ends:**
> 1. **Date-range filter** *(blocks done)* — named in the ask; `export.ts` takes no date params and the UI has no picker. Close out: add `start`/`end` params, or descope it explicitly with the requester.
> 2. **Large-export safety** *(blocks done)* — the handler builds the whole CSV in memory; nothing in the diff addresses the timeout clause. Close out: stream rows, or cap with a row-count warning.
> 3. **`docs/api.md`** *(worth closing)* — still lists the endpoint table without `/export`. Close out: one row.
> 4. **Debug print** *(worth closing)* — `console.log("rows", rows.length)` left in the handler. Close out: delete the line.
>
> **Also checked:** tests added and run after the last edit (green); no `.only`/`.skip`; changelog entry present.

## Example 2 — a clean sweep that stays quiet

Input (abridged): "Renamed `formatDate` to `formatLocalDate` across the repo — forget anything?"

Output:

> **Swept clean — nothing forgotten. Ship it.**
>
> **Also checked:** grep for `formatDate` returns zero live references; tests run after the last edit, green; no docs mention the old name; no scaffolding introduced.

No manufactured findings, no padded template. Calibration is staying quiet.

## Example 3 — the pre-commit question this skill must not take

Input (abridged): "We're about to start migrating auth to OAuth — what am I forgetting?"

Output:

> Nothing to sweep yet — the migration doesn't exist, so there's no delivery to diff against the ask. That's a pre-commit question: what you want is **take-a-step-back**, which will pressure-test the plan's fragile assumption and reversibility before you start. Come back here when there's a diff and you're about to call it done.

## What success looks like

The operator either closes a short, evidenced list or ships with earned confidence — never wades through speculative cautions, never re-litigates work that was delivered fine, and never finds out a week later that the README still says nine.
