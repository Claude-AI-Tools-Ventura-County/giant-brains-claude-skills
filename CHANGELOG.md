# Changelog

All notable changes to Giant Brains Claude Skills are documented here. This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **relay** (v1.0) — a turn-based, file-based review loop between two agents carried entirely inside one Markdown file: a Producer builds and is the only writer of the artifact; a Reviewer critiques and *proposes* graded fixes (it never edits directly); the Producer, with the operator, decides and implements each proposal. The human's only job is to say "your turn" in the other window — no copy-pasting output between sessions, which an opt-in **hands-free poll** (all-Claude relays only) can automate away via a guarded `/loop` that fires each turn on a readiness condition (it's my turn + the tree is clean), never a blind timer. The file is the shared bus, change-log, and decision record at once; each turn appends a structured block, flips a `NEXT` pointer, and commits so the other agent can `git diff` exactly what changed. Runtime logs live under `relay-system/` (local scratch; gitignore is the operator's call). Model-agnostic by design: the protocol is embedded in every relay file, so a non-Claude Reviewer (e.g. Codex) can take a turn without the skill installed — which is the recommended way to get genuinely independent eyes, since two same-model agents share blind spots. Ground rules enforce one-window-at-a-time with a clean tree at every handoff, smallest-change fixes, graded findings (`[Blocker]`/`[Should]`/`[Nit]`), and termination on **Approved** or escalation. Repo extra, not part of the curated suite.
- **spike-360** — architecture premise check that runs *before* any plan, spike, or migration. Forces an authority classification first — audit-only, read projection, dual-written peer, source of truth, or replacement runtime — because "source of truth" is a different problem class than "audit log," and that difference sets the scope. Dual-written-peer, source-of-truth, and replacement-runtime verdicts trigger a current-state audit (every reader, writer, persisted field, and external side effect) and a failure-scenario pass (crash before/after write, crash after a side effect, concurrent interleaving across `await`, replay from an empty or partial log, store divergence, legacy import); audit-only and read-projection levels stop at the smallest fix. Hard rule: no migration plan until authority is classified and the read/write/side-effect surfaces are audited. Runs upstream of the phase-0-spike workflow, which already assumes a source of truth exists. Repo extra, not part of the curated suite.
- **giantbrains** — *Route.* The suite's router for whole-doc stress tests: triages the doc in a single message (which doc, what stage), runs the two or three stage-matched lenses report-only (frame/price/size for a draft; size-and-squeeze for in-progress; ledger audit and outcome cut for a retro), and dedupes overlapping findings into one synthesized verdict — one reversibility read, one do-next. Never edits the doc: writers (phase-qa, record-decision, linear) are offered afterward as explicit opt-ins. Refuses the battery on a single decision and routes to the one matching lens instead.
- **utils/claude-code-dotfiles-fork** — standalone kit for syncing `~/.claude` across machines via a private git repo and Claude Code SessionStart/SessionEnd hooks: machine-agnostic INSTALL.md, templates (allowlist `.gitignore`, three hook scripts, settings hooks snippet), the maintainer's live-deployment HANDOFF.md, and the upstream MIT-0 documentation fork. Self-sufficient — replicating the sync requires nothing outside this folder.
- **loose-ends** — *Sweep.* The suite's post-work completeness check — Act I's mirror image, guarding the moment before "done" instead of the moment before committing. Reconstructs the contract from the original ask (including the throwaway clauses), inventories the delivered diff, and enumerates what's absent: dropped requirements, sibling surfaces still stating the pre-change truth (docs, changelogs, counts, install loops), verification claimed but not run after the last edit, and leftover scaffolding. Findings return blocking-first, each with an evidenced address and a one-line close-out; a clean sweep returns "swept clean — ship it" as a first-class verdict. Strictly post-work: the pre-commit "what am I missing?" routes to take-a-step-back, plan-doc gating to phase-qa, and bugs in code that is present to code review.

### Changed

- **relay** — added a *claim-versus-file reconciliation* guardrail to close the gap where a relay ends (`Approved`) but the artifact's final edits never fully landed — the failure mode that bites hardest on a non-executable artifact (design-spec / plan doc), where there's no runtime check to catch it. Three reinforcing rules across all three surfaces (Claude-facing Guardrails, the portable TAKE YOUR TURN block, and Ground rules): (1) the closing `Approved` is verified against the **artifact file itself**, never the relay log — a claimed-implemented fix that is missing or partial flips the verdict to `Changes requested` with a `[Blocker] claimed-implemented-but-absent @ file:line`; (2) the Producer self-reconciles each `Implemented → @ file:line` against the file before flipping `NEXT`, catching a dropped edit one step earlier; (3) every `Implemented` disposition must cite the line as it appears in that turn's commit diff, so a claim with no matching hunk is false on its face.

## [1.0.0] - 2026-06-06

First public release: a six-skill suite for [Claude Code](https://claude.com/claude-code) spanning two acts — **deciding well**, then **improving verifiably**. Every skill shares one throughline: make the implicit explicit, lead with the line that survives skimming, and refuse rather than fake it.

### Act I — Deciding well (decision hygiene)

Four one-shot skills that fire around a decision, each answering a different question at a different moment, and chain Frame → Price → Size → Cut.

- **take-a-step-back** — *Frame.* A brief 360 reset before committing to a plan or recommendation: surfaces the most fragile assumption, an alternative framing, and the reversibility cost.
- **iron-triangle** — *Price.* Forces the implicit speed/cost/quality tradeoff explicit, names the corner being sacrificed, and points to scope as the release valve.
- **blast-radius** — *Size.* Sizes a chosen path as Small / Medium / Major, names concretely what breaks, and rates reversibility on a shared Easy / Costly / One-way door scale.
- **bottom-line** — *Cut.* Compresses verbose or repetitive output into the real decision, a recommendation, and any hard-to-reverse choice.

### Act II — Improving verifiably (measure, then optimize)

A new pair that carries a concrete improvement from a vibe to a proven result, chaining Define → Improve.

- **baseline-spec** — *Define.* Turns a vague "make it better" into a runnable contract — a scalar metric, an un-gameable correctness oracle, a fixed budget, and a captured baseline. Leads with a one-shot spec sheet; drops into one-question-at-a-time interrogation only if the operator engages. Stress-tests weak oracles ("if the gate is just *does it compile*, the loop deletes the function to hit 0ms") and offers proxies for subjective goals instead of a flat refusal. Hands off to auto-improve once all three pillars exist.
- **auto-improve** — *Improve.* The suite's one executional skill: a bounded, self-verifying mutate-measure-keep-or-revert loop. Gates on three preconditions and refuses when any is missing; rejects any gain that fails an oracle on fresh inputs or falls within 2× the baseline's median absolute deviation; reverts rejected changes mechanically (never model-judged); validates the winner on a held-out eval. Returns either a verified, numbered win or an honest "no real improvement found." Ships with a conceptual [README](auto-improve/README.md) and an operator [FAQ](auto-improve/FAQS.md) covering non-code (prose, SEO, legal, prompt) use.

### Shared design

- **Short, structured output.** Lead with the headline line, then only the fields that change the call; never pad the template.
- **Shared reversibility vocabulary.** Easy / Costly / One-way door, so a two-way door is treated differently from an expensive commitment.
- **Refuse rather than fake it.** Stay quiet on small reversible changes; refuse to optimize the unmeasurable; reject gamed or noise-level wins.

### Authoring conventions

- Valid YAML frontmatter on line 1; entry file named exactly `SKILL.md` (case-sensitive loader).
- ASCII punctuation only (straight quotes, regular hyphens; em-dashes permitted).
- Triggers live in the `description` and are concrete and observable.
- Each skill includes at least one counter-example where it correctly does *not* escalate.

[1.0.0]: https://github.com/Claude-AI-Tools-Ventura-County/giant-brains-claude-skills/releases/tag/v1.0.0
