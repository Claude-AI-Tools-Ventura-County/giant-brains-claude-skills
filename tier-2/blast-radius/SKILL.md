---
name: blast-radius
description: >
  Flag the true cost of a recommendation before the user commits, so a large or
  hard-to-reverse change is never presented like a minor tweak. Fire automatically
  when you are about to recommend a refactor, a migration, a schema change, a
  dependency or framework swap, a public API or contract change, a move across
  service boundaries, or anything else expensive to adopt or painful to undo. Also
  trigger when the user asks whether something is "a big change," "a major
  refactor," "risky," "breaking," "hard to unwind," "a one-way door," "painting us
  into a corner," or "more work than it sounds." Skip only when the user explicitly
  asks for the best path regardless of cost.
---

# Blast Radius

Make hidden implementation cost impossible to miss.

You often recommend the structurally "best" option without flagging that it is actually a major refactor, a breaking change, or a hard-to-reverse commitment. This skill forces the answer to name the size of the change, show the blast radius, and offer a safer reversible path when one exists.

## Core idea

Don't just judge whether the recommendation is good in theory. Judge whether it is **cheap or expensive to adopt**, **safe or risky to roll out**, and **easy or painful to undo** — and say so plainly.

The goal is not to block ambitious changes. It is to stop large commitments from being presented like minor tweaks — and equally, to *not* dramatize work that is genuinely small.

## Output format

Lead with the TL;DR — it is the one line that must survive skimming. Then add only the supporting fields that earn their place, one line each. Drop any field that doesn't apply; never pad the template. A genuinely small change might be just a TL;DR and a Do next.

**TL;DR:** [⚠️ for Medium/Major, ✅ for Small] **[Small / Medium / Major]** — [one sentence: what makes it this size, and the safer path if there is one.]

**Change level:** [Small / Medium / Major] — [the single most severe signal that sets the tier.]

**Blast radius:** [Concretely what has to change and who breaks — schema, API consumers, tests, deploy flow, client code, infra, docs, team coordination. Name the systems, not "it's complex."]

**Reversibility:** [Easy / Costly / One-way door] — [what locks in, and how hard it is to back out.]

**Safer path:** [A smaller, more reversible first step — pilot, adapter, flag, abstraction — or "none meaningful."]

**Do next:** [The cheapest step that validates the recommendation before full commitment.]

*Add only when you can't size it confidently —* **Missing:** [the one or two facts that would settle the tier]. **Confidence:** [High / Medium / Low].

## Classifying the change

Pick the tier of the **most severe** signal present.

**Small** — local and reversible. One module or file; no schema or public-contract change; no user-facing disruption; easy rollback.

**Medium** — bounded but spreading. Several modules or integration points; coordinated testing; maybe a data backfill, adapter, or rollout plan; rollback has cost but is manageable.

**Major** — changes architecture, contracts, or ownership boundaries. Schema migration with application impact; public API or interface change; breaking changes for downstream consumers; replacing a foundational library or framework; moving logic across service boundaries; vendor or pattern lock-in; coordinated frontend + backend + infra rollout.

**Tie-breaker:** between Medium and Major, choose Major when rollback is expensive or coordination cost is high.

## Principles

**Don't bury the warning.** If it is a major refactor or likely to break things, that is the TL;DR — not a footnote.

**Name the blast radius, don't gesture at it.** "Touches auth, billing, and the public API contract" is useful. "This may take some effort" is not.

**Separate "good idea" from "cheap idea."** A recommendation can be strategically right and operationally expensive. Say both.

**Always check reversibility.** Can it be piloted behind a flag, adapter, or abstraction first? If yes, that is the safer path.

**Don't manufacture drama.** Accurate warning, not constant alarm. If the change is genuinely local and reversible, say so in one line and move on.

**Count the hidden follow-on work.** Migration scripts, test rewrites, rollout sequencing, backward-compat shims, observability, customer comms, docs — these are part of the size.

**Flag missing facts instead of guessing.** If you can't size it, say what you'd need rather than faking confidence.

## Examples

### Small change — correctly not alarmed

**TL;DR:** ✅ **Small** — adds a nullable column and one read path; isolated and easy to roll back.

**Reversibility:** Easy — additive migration, no consumer changes; drop the column to revert.

**Do next:** Ship through the existing migration flow; no special rollout needed.

### Major refactor — sounds smaller than it is

**TL;DR:** ⚠️ **Major** — moves core business logic across a service boundary, affecting every existing integration. Extract behind an adapter inside the monolith first.

**Change level:** Major — logic crosses a service boundary and changes its ownership, not just its location.

**Blast radius:** Hook-based integrations need rewiring; in-process callers must handle network failure; testing, deploy, and on-call all change once logic lives behind an API.

**Reversibility:** One-way door — once multiple consumers depend on the new API shape, reversing is expensive.

**Safer path:** Build an internal service layer inside the monolith, then extract one bounded workflow behind an adapter.

**Do next:** Prove the seam on a single workflow before touching every hook.

## What success looks like

The operator scans the response and within seconds knows whether this is a quick tweak, a bounded project, or a big commitment to treat with caution — and if it is expensive or hard to reverse, they can't miss it. If they read only the TL;DR, they still got the warning.
