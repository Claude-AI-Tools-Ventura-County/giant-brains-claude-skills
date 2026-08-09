---
name: better-options
description: |
  Pressure-test an option set before the operator picks. Catches an AI agent — this one included — conflating two separate problems into one menu, or quietly narrowing the field to a false dilemma that skips the boring option. Borrows debug-mantra's falsify-the-hypothesis rigor (disprove each option before trusting it) then ponytail's minimalism bias (of what survives, favor the smallest) to surface the option nobody named because it wasn't impressive enough.

  Trigger when an agent — this one included — presents two or more options for a non-trivial engineering decision, especially when every option involves new abstractions, infrastructure, or a rewrite; when the framing sounds like "you have to either X or Y," "there's no way around it," or "we'd need to..."; or when the user asks "is that really the only way," "feels like you're overcomplicating this," "are these actually the same problem," or "what's the simplest version that still works."  Also self-trigger before presenting any option menu on a complicated technical decision — pressure-test it before showing it.

  Do not trigger when only one viable path exists and the menu is honest about that, when the choice is low-stakes and reversible (take-a-step-back's "lighter than it feels" territory), or when an option list already exists and the ask is just to compress it into a call — that's bottom-line's job.
---

# Better Options

Before the operator picks from a menu, check whether the menu is honest.

Two failure modes make an option set worse than useless: it silently **bundles distinct problems** into one set of choices (so every option is really "fix A and B together," and the cheap fix for A alone never gets named), or it presents a **false dilemma** — a field narrowed to the options an agent finds natural to reach for (new service, new abstraction, a rewrite) while the boring option that would actually resolve it sits off the list. Both failure modes look identical from the outside: a confident menu, plausible tradeoffs, nothing wrong that a skim would catch.

## Core idea

Two borrowed disciplines, applied in sequence to the menu itself rather than to a single plan:

1. **Falsify before trusting** (from [debug-mantra](../../04-build/debug-mantra/SKILL.md)) — treat "these are the options" and "this requires X" as hypotheses, not facts. For the leading option, find the cheapest disproof and run it before building on top of the option. If the option's justification doesn't survive a real attempt to knock it down, it doesn't belong on the menu.
2. **Favor the smallest survivor** (from [ponytail](../../04-build/ponytail-refined/SKILL.md)) — once options survive falsification, don't default to the most architecturally satisfying one. Actively check whether a config flag, an existing feature, a one-line change, or deleting code resolves the actual observed problem — not the theorized one.

The conflation check comes first, because it's the cheapest disproof of all: half of inflated option menus dissolve the moment you notice they're answering two questions at once.

## How this differs from the sibling skills

- **take-a-step-back** — "Am I making the best decision possible?" Challenges the frame of a single plan already in motion.
- **iron-triangle** — "Which of speed, cost, or quality am I trading?" Prices a trade once you're inside one option.
- **blast-radius** — "How big is the path I chose, what breaks, how hard to undo?" Sizes an option already picked.
- **bottom-line** — "There's too much here — what's the call?" Compresses an *honest* option list that's just too verbose.
- **better-options** — "Is this menu itself honest — one problem or several, and is the simplest real option even on it?" Fires *before* any of the above, at the moment the menu is assembled, not after one option is chosen or the analysis balloons.

If the menu is already trustworthy and just needs cutting to a call, hand off to bottom-line. If the menu is trustworthy and one option is chosen, take-a-step-back and iron-triangle pick up from there.

## Output format

Lead with what the menu actually is. Then run the check — most decisions need only the core three lines.

**The menu:** [The options as presented, in one line, plus the decision they're supposedly resolving.]

**Better-options check** — core:
- **Conflation:** [Is this one problem or several wearing one option set? If several, name the split — each sub-problem may have its own trivial fix.]
- **Falsified survivor:** [Walk the cheapest disproof of the leading option's justification. Does it survive? If it doesn't, say so plainly — that option is dead, not "worth keeping in mind."]
- **Simplest surviving option:** [Among what survives, the smallest fix that resolves the *actual observed* problem — config, flag, existing feature, one-liner, deletion — named explicitly, even if it wasn't on the original menu.]

Add from the menu only when it changes the call:
- **Dropped option:** [The boring option that never made the list, and why it likely got skipped — usually because it isn't architecturally interesting, not because it doesn't work.]
- **False dilemma:** [Only two or three options were named, but a smaller move avoids the tradeoff between them entirely.]
- **What the bundle was hiding:** [When conflation is the finding, name what got obscured — usually the cheap fix for the smaller of the two bundled problems.]

**Do next:** [The smallest concrete action that tests the simplest surviving option — not "consider it," an actual step.]

**Missing:** [Only if a fact you don't have would change which option survives. Omit by default.]

## Principles

**Check for conflation first.** It's the highest-leverage, cheapest question: "is this actually one decision?" A menu that quietly answers two questions at once inflates every option on it.

**Disprove, don't just describe.** Don't list an option's tradeoffs and move on — try to knock the option's stated justification down. An option whose justification doesn't survive a real attempt at disproof shouldn't be presented as equally valid to one that does.

**The smallest surviving option wins by default.** Complexity has to earn its place by surviving falsification, not by being the more thorough-sounding answer. When two options both survive, the smaller one is the recommendation unless something specific rules it out — name that thing if so.

**Name what a menu-builder would skip, not what's easy to defend.** New service, new abstraction, and rewrite are natural options for an agent to reach for because they're generically defensible. Config flag, delete, and one-liner require actually looking at the specific case — do that looking.

**Distinguish "harder to build" from "actually necessary."** The finding that matters is whether the small option resolves the problem that's actually happening, not whether it feels satisfying next to the more ambitious ones.

**One clean disproof beats a survey of every option's pros and cons.** Resist restating each option's tradeoffs symmetrically — that's bottom-line's job on an honest menu. Here, the job is deciding whether the menu itself deserves to stand.

## Scaling

- **Menu is honest, no conflation, options already minimal** → say so in one line and stop. Don't manufacture a finding — a clean menu is a valid outcome, not evidence the skill missed something.
- **Conflation found** → lead with it; it's usually the whole finding. The falsified-survivor and simplest-option lines then apply per sub-problem, not to the original bundle.
- **False dilemma found (menu is honest about being one problem, but narrow)** → lead with the dropped option and why it got skipped.
- **High-stakes / expensive-to-reverse decision** → add the "What the bundle was hiding" or "False dilemma" line explicitly, and treat "Do next" as a real spike, not a suggestion.
- **User already ran their own falsification and it holds** → confirm briefly and defer; don't re-litigate a check that already happened.

## Example 1 — a conflated bug report

Input (abridged): An agent reports, "This flaky test needs either a rewrite of the fixture harness or a retry wrapper around the assertion — the harness doesn't isolate state well enough for a single fix."

Output:

> **The menu:** Rewrite the fixture harness, or add a retry wrapper — to fix one "flaky test."
>
> **Better-options check:**
> - **Conflation:** This is two failures wearing one bug report. Test A fails on a timing race; Test B fails from a global left dirty by a prior test. They only look like one flaky test because they run in the same file.
> - **Falsified survivor:** The harness-rewrite justification claims neither test can be isolated without structural change. Disproof: Test B's failure disappears the moment its shared global is reset in teardown — no harness change needed, and Test A never touched that global.
> - **Simplest surviving option:** Add one `afterEach` teardown call that resets the shared global (fixes Test B). Test A's timing race needs its own look — likely a `waitFor` instead of a fixed sleep, not a harness rewrite either.
>
> **Dropped option:** A one-line teardown call was never on the table because the report treated both failures as one symptom needing one structural fix.
>
> **Do next:** Add the teardown reset, rerun both tests in isolation to confirm Test B is the one that clears, then look at Test A's wait condition separately.

## Example 2 — a false dilemma from scale anxiety

Input (abridged): "We're hitting load limits — we should either migrate to Postgres or shard the current MySQL instance."

Output:

> **The menu:** Migrate to Postgres, or shard MySQL — to fix a load problem.
>
> **Better-options check:**
> - **Conflation:** None — this is genuinely one problem (load), not two bundled together.
> - **Falsified survivor:** Both options assume the current schema/indexing is already load-bearing-efficient and the ceiling is structural. Disproof: the slow endpoint runs an unindexed query scanning the full table on every request — that's a single missing index, not a capacity ceiling.
> - **Simplest surviving option:** Add the missing index. Neither migration nor sharding is justified until load is retested against an indexed query.
>
> **False dilemma:** Migrate-or-shard were the two options an agent under scale pressure reaches for by default; "check whether the query is even indexed" isn't architecturally interesting, so it never made the list.
>
> **Do next:** Add the index, rerun the load test, and only revisit migrate-vs-shard if the ceiling persists against an indexed query.
