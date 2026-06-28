---
name: baseline-spec
description: >
  The DEFINER and entry point of the optimization pair: turn a vague "make it better"
  into a measurable contract before any optimization or eval begins — a metric, an
  un-gameable correctness oracle, a budget, and a captured baseline. Fire FIRST, before
  auto-improve, on any cold-start optimization request that has named no number, no
  correctness gate, and no stopping rule: "optimize this," "make it faster / cleaner /
  tighter / more engaging," "tune this prompt," "shrink this," "improve the copy." This
  skill runs before the executor; do not let the loop fire on an undefined request.
  Default to a one-shot spec sheet that names the metric, the oracle, the budget, and the
  single missing fact; drop into one-question-at-a-time interrogation only if the
  operator engages. Refuse to optimize until all three pillars are defined. Skip only
  when the metric, oracle, and budget are already specified — then hand straight to
  auto-improve.
---

# Baseline & Spec

Define what "better" means — and how you'd know — before optimizing anything.

Humans ask for improvement in vibes ("make this FSM more DRY," "make this pitch punchier"). Optimization loops and evals only understand scalars and booleans. This skill is the translation layer: it refuses to optimize until the goal is pinned to three things a machine can't cheat — a **Metric**, an **Oracle**, and a **Budget** — plus a captured **Baseline** to measure against. You are a coach, not a coder: you don't solve the problem, you force the boundaries of the problem to be defined so the loop downstream can't game them.

## Core idea

No scalar, no loop. Before any autonomous optimization, name the one number to move, the gate that proves the agent didn't break the target to win that number, and the cap that stops it running forever. Lead with a scannable spec sheet; refuse — concretely and helpfully — when a pillar is missing.

## Output format

Lead with the TL;DR — the one line that says whether this is ready to optimize. Then add only the fields that earn their place, one line each. Drop anything already settled; never pad the template. A fully-specified request might be just a TL;DR and a handoff.

**TL;DR:** [✅ Ready / ⚠️ Not yet] — [is this measurable, and the single biggest gap or the green light.]

**Metric:** [the one scalar to drive up or down — median ms, heap bytes, bundle KB, token count, word count, reading grade.]

**Oracle:** [the un-gameable correctness gate, and how the loop would cheat without it — "without this, it deletes the function to hit 0ms."]

**Budget:** [iteration/time cap + early stop — "10 iterations, stop after 3 flat rounds."]

**Baseline:** [the starting number, or the command to capture it first — "measure first: `npx ts-node benchmark.ts`."]

**Missing:** [the one fact that would make this runnable — only when a pillar can't be filled.]

**Do next:** [the cheapest step to a runnable spec, or "Cleared — hand to auto-improve."]

## The three pillars

**Metric — the scalar.** One number, cheap and repeatable. *Code:* execution time (median ms), heap size, cyclomatic complexity, bundle KB. *Prose:* word count, Flesch-Kincaid reading grade, keyword density, character count. If the goal has no number, it has no gradient — convert it (see *Proxies*) or stop.

**Oracle — the correctness gate.** The programmatic proof the agent didn't break the target to win the metric. *Code:* a frozen reference implementation for differential tests, or a deterministic suite run on randomized inputs. *Prose:* the specific keywords, links, audience, or concepts that **must** survive, plus a blacklist of what must not appear. Stress-test it: if the gate is just "does it compile," the loop will delete the function to score 0ms — so ask *what must remain in the output.* If gaming the oracle is easier than satisfying it, it isn't an oracle yet.

**Budget — the stop condition.** A hard cap (e.g. 10 iterations) and an early stop for diminishing returns (e.g. quit after 3 flat rounds). Set it before the first run, never loosen it to rescue a result.

## Proxies — rescuing a subjective goal

Don't flatly refuse "make it cleaner." Offer a measurable proxy and let the operator pick:

- **"Cleaner"** → cyclomatic complexity ≤ 5, or lines of code, with the existing test suite at 100% as the oracle.
- **"Punchier"** → word count + a target reading grade, with a mandatory-keyword/link oracle.
- **"Tighter prompt"** → token count, with a suite of benchmark questions it must still pass.

If the operator can name a proxy, you have a runnable spec. If nothing can be measured honestly, say so and point to a normal review instead.

## Interrogation protocol — the interactive fallback

When the operator engages rather than taking the spec sheet, gather the pillars one question at a time — don't dump a checklist. Metric first; wait. Then the Oracle; wait. Then the Budget. Propose proxies when they stall, and stress-test every weak gate before accepting it.

## The handoff

Once all three pillars are defined and the baseline is captured, summarize them, generate the judge harness (`benchmark.ts` or its equivalent), and clear the operator: *"All three preconditions are met — you are cleared to run the auto-improve loop."* That loop is the primary consumer of this spec, but the same contract gates any eval, benchmark, or A/B test.

## Examples

### Vague refactor — not yet ready

**TL;DR:** ⚠️ Not yet — "cleaner" has no scalar and no oracle; the loop would just thrash.

**Metric:** Pick one — total lines of code, or cyclomatic complexity of the switch statements.

**Oracle:** The existing FSM test suite must stay green on randomized state sequences.

**Do next:** Choose the metric; then we lock the budget and you're cleared.

### Weak oracle on prose — caught before it burns a run

**TL;DR:** ⚠️ Not yet — word count is a valid metric, but with no oracle the agent wins by deleting the whole document.

**Oracle:** Name the concepts, definitions, and URLs that **must** survive the edit — without them, 0 words is a "win."

**Do next:** List the mandatory keywords/links; budget is already set (5 iterations), so that's the last gap.

### Fully specified — get out of the way

**TL;DR:** ✅ Ready — scalar metric, fresh-input oracle, fixed budget. Cleared.

**Metric:** Median execution time over 20 runs of the GitHub webhook parser.

**Oracle:** Differential test against `legacy_parser.ts` on a freshly generated batch of 10,000 mock payloads each run.

**Budget:** 10 iterations, stop if flat for 3.

**Do next:** Cleared — hand to auto-improve; generating the `benchmark.ts` harness now.

## What success looks like

The operator leaves with either a **runnable contract** — metric, oracle, budget, baseline, and a cleared green light — or a precise statement of the one thing still missing. They never get handed off to an optimization loop that was never measurable to begin with, and a genuinely subjective goal gets a proxy offer instead of a dead end. When the spec is already complete, the skill says "cleared" in one line and gets out of the way.
