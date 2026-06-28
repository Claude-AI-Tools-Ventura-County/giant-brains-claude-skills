# auto-improve

A bounded, self-verifying optimization loop — and the discipline to refuse one when the problem can't be measured honestly.

The idea comes from Karpathy's `autoresearch`: an LLM-driven hill-climber that mutates a single file, evaluates it against a strict metric, keeps the change if the metric improves, and discards it if it doesn't. Karpathy uses it to train an LLM on a GPU overnight. The same architecture scales *down* to a near-zero-cost, few-minute refactoring or optimization sprint on your own code — but only if you keep the parts that make the result trustworthy.

## Useful, or hype?

Both — depending on the problem. This loop is genuinely valuable for a narrow class and quietly harmful for the rest. The line between them is not the loop; it's whether you can **measure the result honestly** and **catch a cheated win**.

**It's real when three things hold:**

1. **A scalar metric** you can measure cheaply and repeatably — median latency, peak memory, bundle bytes, token count, throughput, eval pass-rate.
2. **A strong oracle** — a correctness check the optimizer can't cheaply game: randomized/held-out inputs, property tests, or differential comparison against a frozen reference. *If gaming the oracle is easier than satisfying it, stop.*
3. **A fixed budget** — a hard cap on iterations, time, or spend, plus a diminishing-returns stop.

When those hold, you've turned optimization into a **ratcheted, verifiable search**: every kept change is empirically proven better, and every rejected one reverts for free.

**It's hype — and subtly harmful — when:**

- The goal is vague ("cleaner," "more DRY"): no gradient to climb, so the agent games it.
- The oracle is weak: it overfits the fixture and ships subtly broken code that scores well.
- The metric is noisy: single-run timings turn keep/revert into coin flips, and a random walk *looks* like progress.

So the skill's first job is to **gate on those three preconditions and refuse when they're missing** — naming what's absent instead of running a feel-good loop. That refusal is the skill working, not failing.

## The three-file architecture

- **The judge (immutable).** Imports the target, generates *fresh, randomized* inputs each run, asserts correctness against a reference or properties, and emits one scalar — measured with **warmup + N repetitions + median**, reporting the spread. The agent may never edit it. A judge that reuses a fixed fixture the agent can read is an invitation to overfit.
- **The target (the only mutable file).** The parsing logic, FSM transitions, query, or prompt under optimization — and nothing else.
- **The brief.** Goal, the exact metric, the don't-touch list, and the budget.

## The loop

1. **Baseline** — run the judge K times; record the median and its spread.
2. **Snapshot** — copy the *single target file* aside (or use a dedicated worktree/branch), so revert is mechanical and can't disturb unrelated work — never a whole-repo `git stash` or per-iteration commits.
3. **One change** — a single targeted edit to the target only.
4. **Re-judge** — reject if correctness fails, if it's slower, **or if the gain falls inside the measured noise band.** Accept only a statistically real win.
5. **Commit or revert** — accept → keep the change and update the baseline; reject → restore the target file from its snapshot, touching nothing else.
6. **Repeat** until the budget is spent or M consecutive rounds yield no real improvement.
7. **Validate the winner** against a *second held-out eval the agent never saw*, to catch benchmark overfit.
8. **Report honestly** — start → end metric, % gain, the spread, and what actually changed.

## What it costs

- **Time:** the loop runs its iterations in minutes while you work on something else.
- **Money:** a handful of context windows of text generation — pennies on standard API pricing, or your existing subscription, rather than an H100 cluster.
- **The result:** a module that is *empirically and repeatably* faster against a hard-to-game correctness gate — reported with an honest number and spread — or a clear "no real improvement found within budget." Never a faster-looking number backed by a gamed oracle or hidden in noise.

> The earlier framing of "mathematically proven more efficient" overclaims. The honest claim is narrower and stronger: *empirically faster on a correctness gate the optimizer couldn't cheat, beyond measurement noise, validated on held-out inputs.*

## Before you run it

This loop assumes you already have a metric, an oracle, and a budget. Defining those — turning a vague "make it better" into a runnable contract and capturing the starting baseline — is the job of the companion [baseline-spec](../baseline-spec/SKILL.md) skill. Run that first; it hands off to this loop once the three pillars are locked.

---

See [SKILL.md](SKILL.md) for the full skill, the precondition gate, and worked good-fit / refuse examples, and [FAQS.md](FAQS.md) for operator guidance including non-code use.
