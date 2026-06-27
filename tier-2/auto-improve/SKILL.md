---
name: auto-improve
description: "The EXECUTOR of the optimization pair: run a bounded, self-verifying loop that measurably improves a single file, only AFTER a measurable contract already exists. Fire when a scalar metric, a strong correctness oracle, and a fixed budget are ALREADY defined — typically handed off by baseline-spec, or when the user says they have a benchmark/eval and a baseline — or when the user explicitly invokes the loop: 'run the auto-improve loop,' 'let it iterate until it's faster,' 'hill-climb this,' 'auto-tune against my benchmark,' 'Karpathy-style optimization loop.' For a cold-start request that has NOT yet named a number, gate, and stop — 'optimize this,' 'make it faster,' 'make it cleaner,' 'tune this prompt' — do NOT run this loop; defer to baseline-spec to define the contract first. Re-gate on the three preconditions before every run; if any is missing, refuse and name it. Skip entirely when the goal is subjective with no number behind it."
---

# Auto-Improve

Turn optimization into a verifiable, ratcheted search — and know when not to.

The appealing idea — point an agent at a file, let it mutate-measure-keep-or-revert until the code is faster — is real for a narrow class of problems and pure hype for the rest. What separates the two is not the loop. It's whether you can **measure the result honestly** and **catch a cheated win**. This skill enforces that, and refuses the loop when you can't. Most real-world code lacks a trustworthy oracle, so expect this skill to refuse more often than it runs — that is the design, not a shortfall.

**Bundled resources** (read on demand, not by default): [README.md](README.md) for the Karpathy `autoresearch` origin, the useful-vs-hype framing, and cost expectations; [FAQS.md](FAQS.md) for operator guidance — especially non-code use (prose, copy, prompts), oracle-strength litmus tests, and the high-stakes-text disclaimer. Read FAQS.md whenever the target is not code.

## Core idea

The LLM *proposes* changes; the harness *decides* whether to keep them. A change survives only if a strong correctness gate still passes on fresh inputs **and** a cheap, repeatable metric improves beyond measurement noise. Every rejected change is reverted mechanically, for free. Done right, you return to code that is empirically, repeatably better — with an honest number — or to a clear "no real improvement found." You never ship a gamed or noise-driven win.

## Gate first — three preconditions

Run the loop **only** when all three hold. If any fails, stop and say which one — that refusal is the skill working, not failing. Defining these three (and capturing the baseline) is the job of the companion **baseline-spec** skill (sibling skill `baseline-spec`; in the repo at `../baseline-spec/SKILL.md`); this skill assumes they exist and executes. If baseline-spec is not installed, define the three pillars with the user directly before running.

1. **A scalar metric.** One number, cheap and repeatable to measure: median latency, peak memory, bundle bytes, token count, throughput, eval pass-rate. If the goal is "cleaner" or "more DRY," there is no gradient to climb — convert it to a real metric (LOC, cyclomatic complexity, a passing test count) or do a normal review instead.
2. **A strong oracle.** A correctness check the optimizer cannot cheaply game — randomized/held-out inputs, property-based or metamorphic tests, or differential comparison against a frozen reference implementation. Litmus test: *if gaming the oracle is easier than satisfying it, stop.* A weak oracle doesn't produce faster code; it produces subtly broken code that scores well. **Weak oracle, concretely:** a fixed set of five inputs the optimizer can read, memorize, and special-case — it will. The harder the domain (e.g. verifying a React component's render output), the more you need *generated* inputs plus metamorphic relations, not a hand-picked fixture. Constructing the oracle is usually the hardest part of the whole setup; don't overestimate the suite you already have.
3. **A fixed budget.** A hard cap on iterations, wall-clock, or spend, set up front — plus a diminishing-returns stop (halt after M consecutive non-improvements).

## The setup — three files

- **The judge (immutable).** Generates *fresh, randomized* inputs each run, asserts correctness against the reference or properties, and emits one scalar. It measures with **warmup + N repetitions + median**, and reports the spread. The agent may never edit it. A judge that reuses a fixed fixture the agent can read is an invitation to overfit.
- **The target (the only mutable file).** The code under optimization, and nothing else.
- **The brief.** Goal, the exact metric, the don't-touch list, and the budget.

**Isolation precondition (don't skip).** Snapshot and revert operate on the **single target file only** — never `git stash` or commit the whole repo. A whole-repo stash can clobber unrelated uncommitted work; per-iteration commits litter your history. Before starting, either commit/stash *your own* in-progress work so the target's directory is clean, or run the loop in a dedicated git worktree or throwaway branch. The loop must never be able to touch anything but the target.

## The loop

1. **Baseline.** Run the judge K times (default K=5); record the median and its spread.
2. **Snapshot the target only.** Copy the single target file aside (e.g. `cp target target.bak`), or rely on the dedicated worktree/branch. Snapshot *only the file under optimization* — never `git stash` the whole repo — so revert is mechanical *and* can't disturb the rest of your tree.
3. **One change.** Make a single targeted edit to the target only — so every accept/reject is attributable to one cause.
4. **Re-judge.** Reject if correctness fails, if it's slower, **or if the gain doesn't clear the noise band** — concretely, require the improvement to exceed **2× the baseline's median absolute deviation (MAD)**. Fix that threshold once, up front; never loosen it mid-run to rescue a change.
5. **Commit or revert.** On accept, keep the change and update the baseline — both the median *and* its spread, so the noise band tracks the current code. On reject, restore the target from its snapshot (`mv target.bak target`) — touching nothing else.
6. **Repeat** until the budget is spent or M consecutive iterations yield no real improvement. **Escape hatch:** if the loop stalls after M flat rounds, permit *one* paired mutation — up to two coordinated edits that only pay off together (e.g. inlining + loop interchange) — under the exact same gate. The escape hatch fires once per run: if the paired mutation also fails to clear the gate, end the run. Some wins are unreachable one line at a time; don't let the single-change rule halt the search prematurely.
7. **Validate the winner.** Re-run the final version against a *second held-out eval the agent never saw* to catch benchmark overfit. For prompt/eval tuning especially, make this a **different, truly blind metric** — not just another split of the same eval format — because an optimizer that sees the judge repeatedly can meta-overfit its scoring quirks, not only its inputs.
8. **Report honestly:** start → end metric, % gain, the spread (so the gain is credible), and what actually changed.

## Principles

**The harness decides, the model proposes.** Keep/revert is mechanical. The moment the agent is trusted to judge its own win, the ratchet breaks.

**Trust the oracle, not the agent.** "Better" means a hard-to-game correctness gate still passes on inputs the agent didn't see — not the agent's say-so.

**A win inside the noise is not a win.** Require improvement beyond measured variance. Otherwise a random walk masquerades as progress.

**Free, file-scoped revert is the whole point.** Every iteration starts from a known-good snapshot of the target, so a bad mutation costs nothing and never touches the rest of your tree. Be honest about the limit, though: reverting the *file* does not wipe the model's *context* — it still recalls the diffs it tried and the verdicts it got this run, so it can in principle learn the judge's quirks across iterations. What actually stops gaming is the **oracle** (fresh/generated inputs, not a fixed fixture) and the **held-out second eval** — not context erasure. On a long or high-stakes run, clear the context between iterations if you want that memory gone too.

**Measure honestly or not at all.** Warmup, repeat, median, report spread. Single-run milliseconds lie.

**Guard against overfit.** Hold out a second eval the loop never optimizes against, and validate the final winner on it.

**Bound it up front, stop on diminishing returns.** Fixed budget; halt when wins dry up. The tail of the search is where cost outruns value.

**Don't optimize the unmeasurable — but offer to make it measurable.** No scalar, no loop. Before falling back to a review, offer a one-shot proxy: *"If you can define a proxy — cyclomatic complexity ≤ 5, no function over 20 lines, tests at 100% — I can run a constrained loop."* That converts many "make it cleaner" requests into good fits instead of a flat refusal.

## Examples

### Good fit — hot parser path

**Metric:** median ms to parse over a freshly generated 10k-payload batch (warmup + 20 runs).
**Oracle:** differential test — output must match a frozen reference parser on randomized inputs each run.
**Budget:** 8 iterations or 10 minutes, whichever first; stop after 3 flat rounds.
**Why it works:** real number, cheap to repeat, and a cheated parser fails the differential check immediately. Return with "143ms → 91ms (±4ms), 36% faster" — and it's true.

### Bad fit — "make the FSM more DRY"

**Verdict:** don't run the loop. "DRY" is not a scalar and has no correctness oracle, so the agent would optimize toward whatever it can game.
**Instead:** either convert to a measurable proxy (cyclomatic complexity or LOC, with the existing test suite as the oracle) and then run the loop — or just do a normal refactor review. Say which, and why.

### Good fit — prompt / eval tuning

**Metric:** pass-rate on a held-out eval set.
**Oracle:** the eval itself, scored on inputs not shown to the optimizer.
**Guard:** keep a *second* eval split the loop never touches; the reported gain is only trustworthy if it survives that split. This is the case where overfit is most seductive and the held-out check matters most.

## What success looks like

The operator gets one of two honest outcomes: a change that is **repeatably, verifiably better** against a correctness gate that's hard to cheat — reported with its real number and spread — or a clear **"no real improvement found within budget."** What they never get is a faster-looking number backed by a gamed oracle or hidden in measurement noise. And when the problem was never measurable to begin with, the skill said so before burning a single iteration.