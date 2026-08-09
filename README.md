# Giant Brains Claude Skills

<img width="1941" height="1058" alt="giant-brains-02" src="https://github.com/user-attachments/assets/d5a0e02b-eec2-4026-b83e-cf725def5942" />

A suite of Claude Code skills that catch you at the moment of a decision, again when you're improving something, and once more before you call it done — and force a short, honest answer you can act on in seconds. An eleven-skill decision-and-improvement core, plus a widening set for debugging, docs, repo, and session hygiene.

**New here?** Jump to [Install](#install) — a symlink loop puts the whole suite in Claude Code in under a minute.

## About

A suite of skills for [Claude Code](https://claude.com/claude-code) that bring hygiene to the whole life of getting something better — first **deciding well**, then **improving it verifiably**. Each fires at a different moment and forces the response into a short, scannable shape — so a human operator can act fast without missing what matters. The throughline: *make the implicit explicit, lead with the line that survives skimming, and refuse rather than fake it.*

## What you get

- **Faster calls, fewer blind spots.** Every answer leads with the one line that must survive skimming, then adds only the fields that change the decision — no wall of text to wade through.
- **Hidden tradeoffs made explicit.** The cost you're actually paying — the corner you're sacrificing, the assumption you're betting on, the blast radius of the path you picked — gets named out loud *before* you commit.
- **A shared reversibility read.** The decision skills speak one vocabulary — **Easy / Costly / One-way door** — so a cheap two-way door never gets treated like a commitment that's expensive to unwind.
- **Honest signal, not constant alarm.** They stay quiet when a change is small and reversible, and refuse rather than fake a verdict they can't stand behind. Calibration is as much about declining as raising a flag.
- **Improvement you can prove.** Act II turns "make it better" into a metric, an un-gameable oracle, and a baseline, then runs a self-verifying loop that returns a real, numbered win — or a clean "no gain found."
- **A paper trail that outlives the chat.** The decision, the bet it rides on, and a revisit date get written to the repo at commit time — so six months later, "why is it built this way?" has an answer.

## When to reach for it

- **An agent handed you a menu of options that all sound complicated** and you want to check it isn't hiding a false dilemma or bundling two problems into one — [better-options](01-decide/better-options/SKILL.md).
- **You're about to commit to a plan or migration** and want to pressure-test the framing before you start — [take-a-step-back](01-decide/take-a-step-back/SKILL.md).
- **You're unsure a feature or refactor is worth building** and want the payoff priced against the cost before you spend the effort — [worth-it](01-decide/worth-it/SKILL.md).
- **A deadline is squeezing you** and you need to name which of speed, cost, or quality you're actually trading away — [iron-triangle](01-decide/iron-triangle/SKILL.md).
- **You're eyeing a refactor or schema change** and need to know how far it ripples and how hard it is to undo — [blast-radius](01-decide/blast-radius/SKILL.md).
- **An agent handed you a wall of options** and you just need the call — [bottom-line](01-decide/bottom-line/SKILL.md).
- **An agent gave you scattered steps or a verbose completion message** and you need the execution sequence — [linear](02-plan/linear/SKILL.md).
- **You told an agent "make this faster"** but can't tell whether it actually did — [baseline-spec](03-improve/baseline-spec/SKILL.md) to define what "better" means, then [auto-improve](03-improve/auto-improve/SKILL.md) to prove it.
- **The work feels finished** and you want what's missing enumerated, executed, and committed before you say "done" ("close the loop") — [loose-ends](05-close/loose-ends/SKILL.md).
- **The done list is frozen** and you want a bounded closure audit that reports only evidenced blockers while deterministically parking everything else — [finish-line](05-close/finish-line/SKILL.md).
- **You just made a call that's expensive to unwind** and want the bet written down before it evaporates — [record-decision](05-close/record-decision/SKILL.md).
- **You have a whole plan doc, not one decision,** and want it stress-tested before work starts — [giantbrains](giantbrains/SKILL.md) triages once, runs the right two or three lenses, and returns one combined verdict.

## Act I — Deciding well (decision hygiene)

Five skills that fire around a decision, each answering a different question at a different moment.

| Skill | The operator's question | Its job |
|---|---|---|
| [better-options](01-decide/better-options/SKILL.md) | "Is this menu itself honest — one problem or several, and is the simplest option even on it?" | **Scrub** — catch a conflated ask or a false dilemma before any option is chosen |
| [take-a-step-back](01-decide/take-a-step-back/SKILL.md) | "Am I making the best decision possible?" | **Frame** — challenge the plan and the problem before committing |
| [iron-triangle](01-decide/iron-triangle/SKILL.md) | "Which of speed, cost, or quality am I trading away?" | **Price** — make the implicit tradeoff explicit |
| [blast-radius](01-decide/blast-radius/SKILL.md) | "How big is the path I chose, what breaks, how hard to undo?" | **Size** — measure cost and reversibility of a chosen path |
| [bottom-line](01-decide/bottom-line/SKILL.md) | "There's too much here — what's the call?" | **Cut** — compress overload and analysis paralysis into a decision, with a brief anchor to where the work sits |

They **chain** along the life of a decision: **scrub** the menu (is it even honest?), **frame** it (should I, and is this the right problem?), **price** the tradeoff (which corner gives?), **size** the chosen path (how big, what breaks?), then **cut** to the bottom line when the analysis balloons. The same situation can touch all five precisely because they answer different questions at different moments.

## The bridge — from deciding to doing

Once the call is made, one skill turns it into motion.

| Skill | The operator's question | Its job |
|---|---|---|
| [linear](02-plan/linear/SKILL.md) | "The steps are scattered — what's the execution order?" | **Sequence** — extract and order procedural steps into one top-to-bottom plan |

[linear](02-plan/linear/SKILL.md) is not a decision skill — it fires once a call exists and the *doing* is scattered. It's the natural handoff from `bottom-line` (decision made → ordered plan), but it earns its keep anywhere steps hide in prose: a verbose how-to from an agent mid-project, or a completion message at the tail end whose remaining work is smeared across "what I didn't do," "open items," and "next steps." Whenever someone must execute three or more steps, linear collapses them into one numbered, top-to-bottom plan — branches as sub-bullets, verification inline, a brief "where are we now?" context anchor up top when needed, and nothing actionable after the list.

## Act II — Improving verifiably (measure, then optimize)

Once you've decided to make something concretely better, a second pair carries it from a vibe to a proven result.

| Skill | The operator's question | Its job |
|---|---|---|
| [baseline-spec](03-improve/baseline-spec/SKILL.md) | "What does 'better' even mean, and how would I know?" | **Define** — turn "make it better" into a metric, oracle, budget, and baseline |
| [auto-improve](03-improve/auto-improve/SKILL.md) | "Now make it better — provably, not just plausibly." | **Improve** — run a bounded, self-verifying loop, or honestly report no gain |

These **chain** too: **define** the measurable contract, then **improve** against it. The routing is deliberately one-directional — a cold-start request like *"optimize this"* belongs to [baseline-spec](03-improve/baseline-spec/SKILL.md) (the **definer**), which fires first; [auto-improve](03-improve/auto-improve/SKILL.md) (the **executor**) defers any undefined request back to it and only runs once a metric, an un-gameable oracle, and a budget already exist. baseline-spec refuses to optimize a goal it can't measure — exactly the Act I instinct of *refuse rather than fake it* — and hands off to auto-improve once the three pillars are locked. auto-improve is the suite's one **executional** skill: instead of emitting a verdict, it runs a ratcheted mutate-measure-keep-or-revert search and returns either a verified, numbered win or a clean "no real improvement found." See its [README](03-improve/auto-improve/README.md) and [operator FAQ](03-improve/auto-improve/FAQS.md).

The two acts join end to end: decide *whether and what* (Act I), sequence the work ([linear](02-plan/linear/SKILL.md)), then *prove the improvement* (Act II) — and sweep the loose ends before calling it done.

## The sweep — declaring done honestly

Work rarely ends where the request did. Two skills fire at the last moment — after the work, before the word "done."

| Skill | The operator's question | Its job |
|---|---|---|
| [loose-ends](05-close/loose-ends/SKILL.md) | "What did I forget?" / "Close loop" | **Sweep & Execute** — diff work against the ask, enumerate what's absent, run custom sequence scripts, execute final fixes, and commit/push |
| [finish-line](05-close/finish-line/SKILL.md) | "Is this frozen done list actually closed?" | **Close & Park** — run a bounded evidence gate, report only Critical/High blockers, and park excluded findings locally |

[loose-ends](05-close/loose-ends/SKILL.md) (alias "close-loop") is Act I's mirror image: the decision skills guard the moment *before committing*; this one guards the moment *before declaring done*. It reconstructs the contract (the original request, including the throwaway clauses), inventories what was actually delivered, and sweeps for the classic forgettables — the dropped requirement, the unrun test, the stale README, the leftover debug print. It also explicitly checks for a local or global `.claude/loose-ends-sequence.md` manifest to load and run project-specific custom end sequences. Crucially, it then actively offers to **close the loop**: executing the missing steps, running custom scripts and linters, auto-syncing the docs, and generating the final git commit and push. Findings come back blocking-first, each with an evidenced address and an offer to execute the fix. It is strictly post-work: "what am I missing?" asked *before* the work exists belongs to [take-a-step-back](01-decide/take-a-step-back/SKILL.md), gating the phases of a plan doc belongs to [phase-qa](02-plan/phase-qa/SKILL.md), and bugs in code that *is* present belong to a code review — this skill hunts the absent, not the wrong.

[finish-line](05-close/finish-line/SKILL.md) is the narrower terminal gate: the user supplies a frozen done list, it verifies only that list, reports objective Critical/High blockers with evidence, and parks every other finding in a local ignored `PARKED/` file. Use it when the task is to end scope, not to discover more work; a request to finish active implementation still belongs to the implementation workflow.

## The ledger — remembering why

Every skill above produces a sharp one-shot verdict — and then the verdict evaporates when the chat ends. One skill makes them durable.

| Skill | The operator's question | Its job |
|---|---|---|
| [record-decision](05-close/record-decision/SKILL.md) | "We made the call — what did we bet on, and when will we know we were right?" | **Record** — write the bet to the repo at commit time, close the loop when reality reports back |

[record-decision](05-close/record-decision/SKILL.md) is the suite's memory. At commit time it writes the decision to a dated file — the call, the fragile assumption it rides on, the expected signal with a by-when, the reversibility read, and a revisit trigger — then keeps the record *and* the project docs current as findings arrive. It's mostly a receiver: take-a-step-back's fragile assumption becomes the bet, blast-radius's verdict becomes the reversibility line, baseline-spec's metric becomes the expected signal. The records carry machine-readable frontmatter, so "find every Costly decision not yet Validated" is one query, and a date-based revisit trigger can become a `/schedule` appointment instead of a hope.

It is deliberately **not** Claude's memory (`MEMORY.md` / `CLAUDE.md`): memory is operator-private and about *how Claude should work with you*; decision records live in git, address the whole team — humans and future agents — and answer *why the system is shaped this way*. The skill file carries the full comparison.

## The router — one door to the suite

When the input is a whole doc rather than a single decision, one skill picks the lenses for you.

| Skill | The operator's question | Its job |
|---|---|---|
| [giantbrains](giantbrains/SKILL.md) | "Stress-test this whole plan — which lenses should run?" | **Route** — triage once, run the 2–3 stage-matched lenses report-only, synthesize one verdict |

[giantbrains](giantbrains/SKILL.md) is the suite's front door for docs. It triages in one message (which doc, what stage), then routes to at most three lenses — a draft gets frame/price/size, an in-progress plan gets a size-and-squeeze check, a retro gets the ledger audit and the outcome cut — runs them report-only, and dedupes the overlap into a single bottom-line-shaped verdict: one reversibility read, one do-next. It never edits the doc: writers ([phase-qa](02-plan/phase-qa/SKILL.md) for phased plans, [record-decision](05-close/record-decision/SKILL.md) for bets, [linear](02-plan/linear/SKILL.md) for scattered steps) are offered afterward as explicit opt-ins. And on a one-pager it refuses the battery and hands off to the single matching lens — running five lenses on one decision is ceremony, not hygiene.

## More in the suite

The core above is the decision-and-improvement throughline. Around it sit skills that apply the same *make-the-implicit-explicit, refuse-rather-than-fake-it* discipline to other moments — planning, debugging, and keeping a repo honest.

| Skill | When it fires | Its job |
|---|---|---|
| [worth-it](01-decide/worth-it/SKILL.md) | "Is this feature/refactor even worth building?" | **Price the payoff** against the cost across every constituency a change serves, versus doing nothing |
| [spike-360](02-plan/spike-360/SKILL.md) | A change might introduce, move, or replace a source of truth | **Interrogate authority** before planning anything that touches authoritative state |
| [swe](02-plan/swe/SKILL.md) | Authoring or reviewing a v1.x build doc / spec / RFC | **Governance lens** — minimal scope, designed for diagnosis, verifiable before code |
| [phase-qa](02-plan/phase-qa/SKILL.md) | A phased plan needs checks baked in, or completed phases reviewed | **Plan QA** — append phase-appropriate checklists, then diff-review the finished phases |
| [feynman](02-plan/feynman/SKILL.md) | "Explain this simply", "ELI5 this doc", "translate this for execs" | **Translate, don't dilute** — a layered plain-English rebuild with analogies that name where they break, and an honest list of what the source left unclear |
| [debug-mantra](04-build/debug-mantra/SKILL.md) | A bug, a stack trace, a "where is this coming from?" | **Debugging discipline** — reproduce, trace the fail path, falsify the hypothesis, cross-reference |
| [rabbit-hole](04-build/rabbit-hole/SKILL.md) | An agent keeps surfacing one-more-thing on a simple task | **Stop the drip** — one end-to-end triage that puts every issue on the table at once. Optional [always-on guard](#beta--the-always-on-rabbit-hole-guard) *(beta)* |
| [stay-focused](04-build/stay-focused/SKILL.md) | A long session keeps wandering off the task it started on | **Hold one anchor** — lead every reply with the original task's live status, in minimum-viable text. Optional [always-on guard](#the-always-on-stay-focused-anchor) |
| [ponytail](04-build/ponytail-refined/SKILL.md) | Over-engineering, bloat, "what's the simplest version?" | **Force the laziest implementation** that works — YAGNI on code and abstractions, not on explicit feature requirements |
| [honest](repo-health/honest/SKILL.md) | "What's the real state of this repo?" before a stakeholder update | **Ground-truth read** — how mature the codebase really is and what you can safely claim |
| [front-door](repo-health/frontdoor/SKILL.md) | Auditing onboarding — "can a new user install this?" | **Walk the front door** — does clone-to-working actually work, and is a secret leaked? |
| [readme-audit](repo-health/readme/SKILL.md) | "Is the README accurate / clear / still matching the code?" | **Audit the README** as artifact and as map — then follow its links as a doc-hygiene litmus |
| [shakedown](repo-health/shakedown/SKILL.md) | A skill's bundled script runs in one session but is "not found" in another | **Shake out path bugs** — static path audit plus a live foreign-CWD / nested / spaces / install-mode matrix, then a graded report with the fix |
| [snapshot](repo-health/snapshot/SKILL.md) | "Save this session" before signing off or a crash | **Checkpoint the session** to an additive `snapshot.md` you can resume from later |
| [btw](repo-health/BTW/SKILL.md) | "Focus mode", declaring up to 3 tasks for a session, "no side quests" | **Session attention firewall** — anchor to declared focus, park off-task findings as Action / Review Later / Interesting instead of surfacing them |

Standalone tooling that isn't part of the suite (read-only permission presets, recent-prompt allowlisting, gh/git auth repair, a time-boxed get-this-repo-building runner, per-repo VS Code window tinting, a daily Obsidian habit FSM, a dotfiles-sync kit) lives under [utils/](utils/README.md).

## Beyond the suite — the relay

A standalone collaboration tool, not one of the ten decision skills: [relay](04-build/relay/SKILL.md) runs a turn-based review loop between two Claude Code agents — a **Producer** who builds and a **Reviewer** who critiques and proposes fixes the author applies — entirely inside one dated Markdown file, so a human stops copy-pasting output between two windows. The file is the shared bus, the change-log, and the decision record at once: graded findings (`Blocker` / `Should` / `Nit` / `Pass`), a mandatory disposition on every proposal, an **evidence contract** per turn (the Producer logs what it *ran / skipped / couldn't run*; the Reviewer logs whether its verdict is `behaviorally proven` or `textual only`), and a clean exit on **Approved**. The protocol is model-agnostic — run a different model in the Reviewer window (Codex, Gemini, another Claude tier) for genuinely independent eyes. See the worked [sample thread](04-build/relay/RELAY-sample.md).

**Optional automation add-on.** Relay is human-locked by default (one "your turn" nudge per handoff). A fuller, `tick`-backed automation engine lives in a sibling repo: [xyz-3-agents-swarm · relay-system](https://github.com/Claude-AI-Tools-Ventura-County/xyz-3-agents-swarm/tree/main/relay-system/2026-06-14). It turns the manual, human-nudged relay into a hands-free, self-healing loop — `tick` coordination primitives enforce strict Producer/Reviewer turn-taking, auto-detect and recover stalled turns, and gate termination on an LLM-written `Approved` with a clean tree. It ships as a sibling self-extracting skill powered by `tick`, leaving the portable `/relay` protocol completely untouched and dependency-free.

## Beta — the always-on rabbit-hole guard

> **Beta.** Opt-in, off by default, and not yet proven across enough real sessions to claim it changes agent behavior. Installing the hooks changes nothing until you switch the guard on; switching it off returns you to a stock session. Try it and tell us whether the drip actually stops.

Invoking [rabbit-hole](04-build/rabbit-hole/SKILL.md) by hand means *noticing* the drip first — usually two or three interruptions after it started costing you. Skill auto-invocation keys off the `description` field, which competes with every other skill's description and loses badly mid-task, exactly when you need it.

An optional pair of Claude Code hooks closes that gap. A `SessionStart` hook injects the skill's trigger rule as hidden system context; a `UserPromptSubmit` hook re-anchors a short reminder each turn. The agent then fires the triage **on itself** before the third unsolicited finding, instead of waiting for you to get annoyed enough to type the slash command.

**It is not a response template.** The hooks inject *when to fire*, never a format to fill. Ordinary replies stay ordinary. The rule explicitly forbids inventing a finding to fill an empty bucket, and forbids firing on genuinely exploratory work or mid-debug when each finding narrows the same bug — the `refuse-rather-than-fake-it` discipline the rest of the suite runs on, applied to the guard itself.

```bash
04-build/rabbit-hole/hooks/install.sh              # wire the hooks in (guard stays off)
04-build/rabbit-hole/hooks/install.sh --uninstall  # take them back out
```

| Command | Effect |
|---|---|
| `/rabbit-hole on` | Guard on. Persists across sessions until turned off. |
| `/rabbit-hole off` | Guard off. Hooks stay installed and emit nothing. |
| `/rabbit-hole` | Unchanged — a one-shot triage, guard or no guard. |

`stop` is deliberately **not** an off-switch phrase: *"stop going down rabbit holes"* is one of the skill's own trigger phrases — someone saying it wants a triage now, not to disable the thing that produces one.

State is one flag file, `$CLAUDE_CONFIG_DIR/.rabbit-hole-active`. Absent means off; no hook ever creates it implicitly, and a corrupted, oversized, or symlinked flag reads as off. Both hooks silent-fail on every filesystem error and exit 0 — a broken hook must never block session start.

Cost, when on: roughly 470–575 tokens once per session, plus 95–110 per turn (heuristic bounds from character and word counts, not a tokenizer count). Zero when off. Full detail, including the manual `settings.json` entries for a commented config the installer refuses to touch, in [HOOKS.md](04-build/rabbit-hole/HOOKS.md).

The hook architecture and its symlink-hardened flag helpers are adapted from [caveman](https://github.com/JuliusBrussee/caveman) by Julius Brussee, MIT licensed — the notice is retained in `rabbit-config.js`, and MIT permits relicensing into this GPL v2 work.

## The always-on stay-focused anchor

[stay-focused](04-build/stay-focused/SKILL.md) locks a whole session to **one anchor task** and makes every reply lead with that task's live status — *fixed? shipped? blocked on an unmerged branch?* — over a horizontal rule, followed by a tight rabbit-hole-style body (What's Shipped / What's Blocked / Recommended / Optional / Only Useful FYIs), each bucket one line, empty buckets dropped. You set it once at the top of a session: `stay focused on <task>` (or `stay on track for <task>`).

The whole promise is *never lose the original task* — and that is exactly what plain skill instructions are worst at holding, because the anchor fades from attention as context fills with tangents and tool output. So here the hooks are **recommended, not just a beta opt-in**. A `SessionStart` hook re-injects the anchor and reply shape into every session (including one resumed the next morning); a `UserPromptSubmit` hook sets the anchor from your phrasing, clears it on an explicit off, and re-anchors a short reminder each turn.

```bash
04-build/stay-focused/hooks/install.sh              # wire the hooks in (no anchor set)
04-build/stay-focused/hooks/install.sh --uninstall  # take them back out
```

| Command | Effect |
|---|---|
| `stay focused on <task>` | Set the session anchor. Persists until cleared. |
| `/stay-focused off` | Clear the anchor. Hooks stay installed and emit nothing. |
| `stay focused` *(no task)* | If nothing is set, the model asks what to lock onto. |

A bare `stop` is deliberately **not** an off-switch — it clears the anchor only when bound to focus/track (*"stop staying focused"*). A tangent you explicitly ask for is served but does **not** replace the anchor: the next reply reopens with the original task's status.

State is one flag file, `$CLAUDE_CONFIG_DIR/.stay-focused-anchor`, holding the sanitized anchor text (single line, capped at 512 bytes). Absent or empty means off; a corrupted, oversized, or symlinked flag reads as no-anchor. It coexists with the rabbit-hole guard — both register on the same events, each strips only its own entries. Cost, with an anchor set: roughly 485–535 tokens once per session, plus 185–205 per turn (heuristic bounds, not a tokenizer count); zero when off. Full detail in [HOOKS.md](04-build/stay-focused/HOOKS.md). The hook architecture and its symlink-hardened flag helpers are again adapted from [caveman](https://github.com/JuliusBrussee/caveman) (MIT), the notice retained in `focus-config.js`.

## What they share

- **Short, structured output.** Every skill leads with the one line that must survive skimming, then adds only the fields that change the call. Drop anything that doesn't; never pad the template. When the work is part of an ongoing phase or status thread, the compression skills also add a brief location marker so the user knows what was just done and where the next steps fit. `baseline-spec` follows the same one-shot, scannable shape as the four decision skills; `linear`'s output *is* the structure — one numbered list, nothing actionable outside it; `record-decision` writes the same scannable shape to a file instead of the chat; `auto-improve` is the lone exception — it *executes* a loop rather than emitting a verdict, but still leads with an honest headline number.
- **A shared reversibility read.** Where it applies, the skills speak one vocabulary — **Easy / Costly / One-way door** — so a two-way door is treated differently from a commitment that is expensive to unwind. (Iron-triangle's version asks whether a sacrificed corner stays *contained* or *compounds*.)
- **Refuse rather than fake it.** Accurate signal over constant alarm. The decision skills stay quiet when a change is small and reversible; `baseline-spec` refuses to optimize a goal it can't measure; `auto-improve` rejects any "win" that's gamed or lost in the noise; `loose-ends` returns "swept clean — ship it" rather than inventing a finding to justify firing. Calibration is as much about declining as raising a flag.

## Calibration — what good output looks like

Good output names the *one* thing that changes the call and ends with a move that reduces uncertainty. Example, from `take-a-step-back`:

> **Decision:** You're about to execute the 3-PR plan doc as written — cherry-picking and sequencing the PRs onto the drifted source branch.
>
> **Step-back check:**
> - **Most fragile assumption:** That the plan doc is still the right path now that the branch has drifted — it was written against a tree that no longer exists.
> - **Alternative frame:** This may not be a "merge the existing PRs" problem at all, but a "re-land the *ideas* as fresh work against current main" problem.
> - **Reversibility:** Costly — once the PRs are cherry-picked and merged in sequence, untangling them from main is real work.
>
> **Do next:** Diff each PR's *intent* against current main and decide per PR — cherry-pick as-is, or re-cut as new work. The plan doc is an input, not a destiny.

What makes it good:
- **One sharp counterpoint, not five.** It names the single fragile assumption instead of listing every possible risk.
- **It challenges the frame**, not just the option — the real question is "follow the plan, or re-cut?", not "how do I cherry-pick cleanly?".
- **Concrete, honest reversibility** — a specific cost, on the shared scale.
- **A do-next that reduces uncertainty** rather than describing it.

The inverse matters just as much: a good skill also knows when *not* to escalate. See `blast-radius`'s small-change example, where the right answer is "ship it, low risk" — calibration is as much about staying quiet as raising a flag.

The compression skills earn their keep on the *delta* — what goes in versus what comes out. From `linear`:

> **In:** "To get this working you'll first want to install the CLI, which you can do with npm. Then there's some configuration to think about — the config file lives at ~/.toolrc and needs your API key. Oh, and note that on Linux you may need sudo for the install. Once configured, run `tool sync` to pull data. If sync fails with a 401, your key is wrong. Finally you can run `tool build`, though if you're on the beta channel you'd use `tool build --beta` instead."
>
> **Out:**
> 1. Install the CLI: `npm install -g tool`
>    - If on Linux: prefix with `sudo` if you get a permissions error.
> 2. Add your API key to `~/.toolrc`.
> 3. Run `tool sync` to pull data. → expect "Sync complete"
>    - If 401 error: API key is wrong — fix step 2 before continuing.
> 4. Build:
>    - Stable channel: `tool build`
>    - Beta channel: `tool build --beta`

Every detail survived — the sudo caveat, the 401 diagnosis, the beta variant — but now it executes top-to-bottom without re-reading.

## Install

These are [Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) built on the open `SKILL.md` standard, so the same files install across every Claude surface.

### Claude.ai (web) and Claude Desktop

The web app and desktop app share one flow: enable code execution, then upload each skill as its own ZIP.

1. **Enable execution.** Open **Settings > Capabilities** and turn on **Code execution and file creation**. (Available on Free, Pro, Max, Team, and Enterprise plans. On Team/Enterprise, an owner must first enable it under **Organization settings > Skills**.)
2. **Zip each skill folder** — one ZIP per skill, each with a `SKILL.md` at its root. Run from the repo root:
   ```bash
   ROOT="$PWD"
   for d in 01-decide/*/ 02-plan/*/ 03-improve/*/ 04-build/*/ 05-close/*/ repo-health/*/ giantbrains/; do
     [ -f "$d/SKILL.md" ] || continue
     (cd "$d" && zip -rX "$ROOT/$(basename "$d").zip" . -x '.*')
   done
   ```
3. **Upload.** In Claude, go to **Customize > Skills**, click **+ > + Create skill > Upload a skill**, and select one ZIP. Repeat for each skill.
4. **Turn it on** under **Customize > Skills**.

Uploaded custom skills are private to your account. Install only from sources you trust, and review each `SKILL.md` before enabling.

### Claude Code

Put each skill directory where Claude Code looks for skills — **personal (all projects):** `~/.claude/skills/`, or **project (shared with a repo):** `<project>/.claude/skills/`. Symlink them so a `git pull` keeps them current (run from the repo root):

```bash
mkdir -p "$HOME/.claude/skills"
for d in "$PWD"/01-decide/*/ "$PWD"/02-plan/*/ "$PWD"/03-improve/*/ "$PWD"/04-build/*/ "$PWD"/05-close/*/ "$PWD"/repo-health/*/ "$PWD"/giantbrains/; do
  [ -f "$d/SKILL.md" ] || continue
  ln -s "${d%/}" "$HOME/.claude/skills/$(basename "$d")"
done
```

Claude auto-invokes a skill when the request matches its `description`, or you can call it by name. The entry file must be named exactly `SKILL.md` (uppercase) — the loader matches it case-sensitively even on case-insensitive macOS, so a lowercase `skill.md` is silently never discovered.

## Authoring conventions

Lessons baked into these files. Keep them if you add more skills:

- **Valid frontmatter on line 1.** The file must open with `---` and a YAML `name` + `description`, with no prose preamble and no ` ```yaml ` code fence wrapping it — otherwise the skill silently fails to load and never appears.
- **Entry file must be `SKILL.md`, exact case.** The loader matches it case-sensitively even on case-insensitive macOS, so a lowercase `skill.md` is silently skipped — and watch for git hiding a case-only rename when `core.ignorecase` is true.
- **ASCII punctuation.** Straight quotes and regular hyphens. Curly quotes and non-breaking hyphens (U+2011) look identical to their ASCII twins but break grep, copy, and matching. Em-dashes are fine.
- **Triggers live in the `description`.** That is the surface Claude matches against — keep it concrete and observable ("about to recommend a migration"), never circular ("fire when the change is major", which the skill can only know *after* running).
- **Examples calibrate behavior.** Include at least one counter-example where the skill correctly does *not* escalate — a small change, a cheap reversible call — or it will skew toward alarm.
- **Brevity is the product.** Each skill's output should be just enough meat that a human operator will actually read it.

## Layout

Abbreviated — skills and their entry points only. Repo meta (`AGENTS.md`, `CHANGELOG.md`, `CLAUDE.md`, `LICENSE`) and the dotfiles-sync kit's inner files (`INSTALL.md`, `HANDOFF.md`, `templates/`) are omitted; see [utils/README.md](utils/README.md) for the kit's contents.

The `0X-*/` folders group the skills by their place in the project lifecycle; the thematic sections above (Act I/II, the bridge, the sweep, the ledger) are the better map to *what each skill does*.

```
.
├── 01-decide/
│   ├── better-options/SKILL.md     # Act I — scrub the menu before anything is chosen
│   ├── blast-radius/SKILL.md       # Act I — size cost & reversibility
│   ├── bottom-line/SKILL.md        # Act I — cut to the call
│   ├── iron-triangle/SKILL.md      # Act I — price the tradeoff
│   ├── take-a-step-back/SKILL.md   # Act I — frame the decision
│   └── worth-it/SKILL.md           # Value lens — is the payoff worth the cost
├── 02-plan/
│   ├── feynman/SKILL.md            # Plain-English translation without dilution
│   ├── linear/SKILL.md             # The bridge — decide → do
│   ├── phase-qa/SKILL.md           # Plan QA checklists + phase diff review
│   ├── spike-360/SKILL.md          # Classify authority before planning
│   └── swe/SKILL.md                # Engineering-governance lens for build docs
├── 03-improve/
│   ├── auto-improve/               # Act II — the executor (self-verifying loop)
│   │   ├── SKILL.md
│   │   ├── README.md
│   │   └── FAQS.md
│   └── baseline-spec/SKILL.md      # Act II — the definer (metric/oracle/budget)
├── 04-build/
│   ├── debug-mantra/SKILL.md       # Four-step debugging discipline
│   ├── ponytail-refined/SKILL.md   # Force the laziest implementation that works
│   ├── rabbit-hole/                # Stop the one-more-thing drip; triage once
│   │   ├── SKILL.md
│   │   ├── HOOKS.md                # Beta — always-on guard (opt-in hooks)
│   │   └── hooks/                  # SessionStart + UserPromptSubmit, install.sh
│   ├── stay-focused/               # Lock a session to one anchor; status-first replies
│   │   ├── SKILL.md
│   │   ├── HOOKS.md                # Always-on anchor guard (opt-in hooks)
│   │   └── hooks/                  # SessionStart + UserPromptSubmit, install.sh
│   └── relay/                      # Two-agent review relay (one file, no copy-paste)
│       ├── SKILL.md
│       └── RELAY-sample.md
├── 05-close/
│   ├── finish-line/SKILL.md       # Bounded closure gate — report blockers, park the rest
│   ├── loose-ends/SKILL.md         # The sweep — before "done"
│   └── record-decision/SKILL.md    # The ledger — record → revisit
├── repo-health/
│   ├── BTW/SKILL.md                # Session attention firewall — anchor to 1-3 tasks, park the rest
│   ├── frontdoor/SKILL.md          # Audit onboarding — clone → working
│   ├── honest/SKILL.md             # Ground-truth read of the repo
│   ├── readme/SKILL.md             # Audit the README + doc-hygiene litmus
│   ├── shakedown/                  # Harden a script-calling skill against path-discovery bugs
│   │   ├── SKILL.md
│   │   └── scripts/                # audit.sh (static), harness.sh (live matrix), lib.sh
│   └── snapshot/SKILL.md           # Session recovery
├── giantbrains/SKILL.md            # The router — one door to the suite
├── utils/                          # Standalone tooling — not part of the suite
│   ├── README.md
│   ├── github-auth-debug/SKILL.md  # Fix the gh-vs-git auth split on macOS
│   ├── install-improve-audit/SKILL.md  # Get an unfamiliar repo building (native or container), then PR the fixes
│   ├── obsidian-habit/             # Daily one-tactic-a-day Obsidian habit FSM (adopt/decline/defer)
│   │   ├── SKILL.md
│   │   ├── scripts/                # habit.py (FSM), archive_stale_notes.py, streak_update.py
│   │   ├── references/tactics.md
│   │   └── templates/Today.md
│   ├── read-only/SKILL.md          # Pre-approve read-only permissions
│   ├── rpr/                        # React to recent permission prompts → narrow allowlist rules
│   │   ├── SKILL.md
│   │   ├── scan.py
│   │   ├── write_rules.py
│   │   └── tests/
│   ├── skill-sync/                 # Keep installed skills in sync with this repo
│   ├── vscode-color/               # Give each repo a stable, distinct VS Code background tint
│   │   ├── SKILL.md
│   │   └── vscode-color.py
│   └── claude-code-dotfiles-fork/  # Kit: sync ~/.claude across machines (INSTALL.md + templates/)
└── README.md
```

## Maintainer & reviewers

- **Maintainer:** Noel Saw
- **Built with:** Claude Code (Effort Max)
- **Cross-reviewed by:** Gemini Pro 3.1, ChatGPT 5.5, and DeepSeek DeepThink

## Sponsored by

This project is supported by two Southern California meetup communities and HiQS.ai.

- [Claude & AI Tools — Ventura County](https://www.meetup.com/claude-ai-tools-ventura-county/)
- [Love2SoCal — Vibe Coding Meetup](https://www.meetup.com/love2socal/)

## License

GPL v2 — see [LICENSE](LICENSE) for details. Provided "as is", without warranty of any kind.
