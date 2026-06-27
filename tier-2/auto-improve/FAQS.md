# auto-improve — Operator FAQ

Practical guidance for running (or refusing to run) the loop. For the full skill see [SKILL.md](SKILL.md); for the spec-and-baseline gate that comes before it, see [baseline-spec](../baseline-spec/SKILL.md).

---

## Getting started

### Where does this idea even come from?

It's a scaled-down take on Karpathy's `autoresearch` — an LLM-driven hill-climber that mutates a single file, evaluates it against a strict metric, keeps the change if it improves, and discards it if it doesn't. Karpathy uses it to train an LLM on a GPU overnight; this skill applies the same mutate-measure-keep-or-revert architecture to a few-minute, near-zero-cost refactor or copy-editing sprint on your own files. See [README.md](README.md) for the origin and the "useful vs hype" framing.

### How is a run physically set up?

Three files, always:

- **The target** — the *only* file the agent may edit (the parser, the FSM, the pitch).
- **The brief** — goal, metric, don't-touch list, and budget.
- **The judge** — an immutable harness that generates fresh inputs, runs the oracle, and emits the scalar. The agent may never touch it.

For code the judge runs tests; for prose it runs keyword/readability checks. Same shape either way.

### What do I have to define before the loop will run?

Three things — the **three pillars**. If any is missing, the loop won't (and shouldn't) start:

1. **Metric** — one number to drive up or down (median ms, memory, bundle KB, word count, Flesch-Kincaid grade, token count).
2. **Oracle** — a programmatic correctness gate the agent can't cheat (differential test, property test, mandatory-keyword checklist).
3. **Budget** — a hard cap (e.g. 10 iterations) plus an early stop (e.g. quit after 3 flat rounds).

If you can't supply all three, that's not a failure — it means the problem isn't ready for an autonomous loop yet. See *"My goal is subjective."*

### Why does this thing refuse so much?

Because **refusal is the feature.** Most real-world tasks lack a trustworthy oracle, and running a loop without one doesn't produce better output — it produces subtly broken output that *scores* well. The skill would rather stop and make you define boundaries than hand you a confident-looking, gamed result.

### What does a finished run actually give me?

One of two honest outcomes: a change that is **repeatably, verifiably better** against a hard-to-game gate — reported with its real number and spread — or a clear **"no real improvement found within budget."** You never get a faster-looking number that's secretly gamed or hiding inside measurement noise.

---

## Using it beyond code

> ### ⚠️ Disclaimer — legal, compliance, and other high-stakes text
>
> This software is licensed under **GPL v2** and is provided **"as is", without warranty of any kind** (see [LICENSE](../LICENSE) and sections 11–12 of the GPL). We cannot control how you use it.
>
> **We do not encourage or condone using this skill to review, simplify, or rewrite legal, regulatory, compliance, medical, financial, or safety-critical documents.** The examples in this FAQ that touch such material (e.g. Terms of Service simplification) describe what the loop is *mechanically capable of* — they are **not** recommendations and **not** legal advice.
>
> The oracle this skill relies on — including any LLM-as-judge — **cannot prove semantic preservation.** A run can score as "passing" while quietly weakening, broadening, or voiding a legal obligation. For anything where wording carries legal or regulatory weight, have a qualified human professional review every change. **You assume all risk for how you apply this tool.**

### Can I use this on non-code work — prose, contracts, marketing copy?

For low-stakes copy — marketing pitches, SEO snippets, internal docs — yes, absolutely. The framework doesn't care whether it's mutating a TypeScript file or a marketing pitch; it only cares that the text can be evaluated against **a hard number and a strict correctness gate.** Swap the unit tests for a prose-checking harness and the architecture is identical.

For **high-stakes text where wording carries legal, regulatory, or safety weight, read the disclaimer above first** — the framework can run, but no automated oracle can guarantee it preserved meaning, so it is not an appropriate place to trust an autonomous loop.

### So what's actually the hard part for non-code work?

Not the LLM — **your ability to build an automated, programmatic "Judge" for human language.** The metric and the loop are easy. Writing an oracle that proves the agent didn't quietly gut the meaning to win the metric is the real work.

### How do I stop the agent from "winning" by deleting everything?

That's exactly what the **oracle** is for. Take optimizing a cold outbound pitch for a SaaS dashboard like GitDaily, where the metric is word count. Without an oracle, the agent hits 0 words by deleting the email. So the harness hard-fails the iteration if:

- The phrase "unified view" or "activity stream" is missing.
- The target audience ("freelance") is removed.
- The call-to-action link (`https://...`) is broken or missing.
- It trips a spam-word blacklist ("Guarantee", "Free", "Act Now", "10X").

Anything mandatory to the *meaning* becomes a gate the metric can't bypass.

### What metrics actually work for prose?

Anything scalar and cheap to compute: **word count** (lower is better), **Flesch-Kincaid reading grade** (e.g. target Grade 6–8 for fast reading), keyword density, or character count. You can combine two — e.g. "shrink word count while landing reading grade 6–8."

### Can you walk me through a non-code run?

The cold-outbound example end to end:

1. **Baseline** — the starting draft is 210 words, Grade 11. The Judge records it.
2. **Snapshot** — the harness backs up `outbound_pitch.md`.
3. **Mutation** — the agent rewrites for punchiness.
4. **Verification:**
   - *Iteration 1:* cut to 90 words — but the calendar link is gone. **Oracle fails → hard-revert** to 210.
   - *Iteration 2:* cut to 140 words, all mandatory keywords and links intact, grade drops to 8. **Oracle passes, metric improved → commit.** New baseline.
   - *Iteration 3:* tries 100 words but uses "Revolutionary." **Spam-filter oracle catches it → revert.**
5. **Completion** — after 10 rounds: a verified **85-word pitch at a 7th-grade reading level** that still contains every mandatory detail and link.

### Where does the non-code version shine?

- **SEO meta descriptions** — maximize keyword density while staying strictly under Google's ~160-character truncation limit.
- **Legal / compliance simplification** — lower the reading grade of a Terms of Service, using an LLM-as-judge oracle prompted to confirm all (say) 10 distinct legal liabilities still survive. **⚠️ See the disclaimer below — we do not recommend this. An LLM-as-judge cannot prove semantic preservation, and a "passing" run can silently weaken or void legal obligations. This bullet illustrates a *mechanically possible* use, not an endorsed one.**
- **System prompts (meta-optimization)** — shrink the token count of a large system prompt while it still passes a suite of 20 benchmark questions.

### When does it fail for prose?

When the goal is **subjective.** Set it loose to make a blog post "more engaging" or "funnier" and you have no oracle and no scalar — the agent thrashes, hallucinates, and outputs generic, stylized slop. The rule never changes: **No scalar, no loop. If you can measure it honestly, you can optimize it autonomously.**

---

## Trusting the result

### How do I know my oracle is strong enough?

Apply the litmus test: **if gaming the oracle is easier than satisfying it, stop.** A *weak* oracle is a fixed set of five inputs the agent can read, memorize, and special-case — it will. Strong oracles use *generated* inputs each run (randomized payloads, fresh examples) or differential comparison against a frozen reference. The harder the domain, the more you need generated inputs plus property/metamorphic checks, not a hand-picked fixture.

### What counts as a "real" improvement versus noise?

A win has to clear the noise band: require the gain to exceed **2× the baseline's median absolute deviation (MAD)**, measured with warmup + repeated runs. Fix that threshold up front and never loosen it mid-run to rescue a change — that's how you fool yourself.

### No single edit beats the noise, but I think two together would. Am I stuck?

No. After the loop stalls for M flat rounds, it has an **escape hatch**: permit *one* paired mutation — up to two coordinated edits that only pay off together (e.g. inlining + loop interchange) — under the exact same gate. Some wins are genuinely unreachable one line at a time.

### How do I know the result didn't just overfit the benchmark?

The winner is re-validated against a **second held-out eval the agent never saw.** For prompt/eval tuning especially, make that a *different, truly blind* metric — not just another split of the same format — because an optimizer that sees the judge repeatedly can overfit its scoring quirks, not only its inputs.

---

## Cost, speed, and operations

### Is this expensive? Do I need a GPU?

No. You're paying for a handful of context windows of text generation — **pennies on standard API pricing**, or your existing subscription — not an H100 cluster. The whole loop runs its iterations in **minutes** while you work on something else.

### Why is the revert mechanical instead of letting the agent decide?

So the agent can't talk itself into keeping a bad change. Keep/revert is a mechanical decision, not an opinion — on reject, the harness restores the target file from its snapshot.

One honest correction to an earlier framing: reverting the file does **not** mean "the model never sees the rejected state again." The model still has the rejected diff and the judge's verdict in its context, so across many iterations it can in principle learn the judge's quirks. What actually prevents gaming is a strong oracle (fresh/generated inputs, not a fixed fixture) plus the held-out second eval — not context erasure. On a long or high-stakes run, clear the context between iterations if you want that memory gone too.

### Is it safe to run this in a repo with uncommitted changes?

Be careful — snapshot and revert must operate on the **single target file only** (`cp target target.bak`, restore on reject). Do **not** `git stash` the whole repo or commit each loop iteration to your working branch: a whole-repo stash can clobber unrelated uncommitted work, and per-iteration commits litter history. Safest is to start from a clean target — commit or stash *your own* work first — or run the loop in a dedicated git worktree or throwaway branch, so nothing the loop does can touch the rest of your tree.

---

## When to walk away

### My goal is subjective ("make it cleaner / punchier / better"). Am I out of luck?

Not necessarily — but don't run the loop as-is. Convert the vibe into a **proxy metric** first: "cleaner" becomes cyclomatic complexity ≤ 5 or LOC with tests at 100%; "punchier" becomes word count plus a reading-grade target plus a mandatory-keyword oracle. If you can define a proxy, you can run a constrained loop. If you genuinely can't, do a normal review instead.

### What's the difference between baseline-spec and the loop itself?

[baseline-spec](../baseline-spec/SKILL.md) is the **definer** — it refuses to write any optimization code and instead returns a one-shot spec sheet (Metric, Oracle, Budget, Baseline, and the single missing fact), dropping into one-question-at-a-time interrogation only if you engage. It stress-tests your proposed oracle ("if the test is just *does it compile*, the loop will delete the function to hit 0ms — what *must* survive?"). Once all three pillars are locked, it captures the baseline, generates the judge harness (`benchmark.ts` or equivalent), and clears you: *"You are cleared to run the auto-improve loop."* This skill ([SKILL.md](SKILL.md)) is the **executor** — it runs the ratcheted search from there. baseline-spec protects you from starting a loop that was never measurable to begin with.
