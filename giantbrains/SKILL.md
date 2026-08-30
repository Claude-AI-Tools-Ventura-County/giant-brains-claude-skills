---
name: giantbrains
description: >-
  Router for the Giant Brains suite: stress-test one doc (a plan, spec,
  proposal, or migration doc) by running the two or three suite lenses that
  match the doc's stage, report-only, then synthesizing one combined verdict.
  Triages in a single message (which doc, what stage), routes by stage —
  draft: take-a-step-back, iron-triangle, blast-radius; in progress:
  blast-radius, iron-triangle; complete: decision-record audit, bottom-line —
  and never edits the doc: writers (record-decision, linear; phase-qa when giant-brains-swe-skills is installed) are
  offered afterward as explicit opt-ins. Trigger when the user invokes /giantbrains,
  says "stress test this plan/doc", "pressure-test this", "run the battery",
  "run all the lenses/brains against this", or asks for a full multi-angle
  review of a planning doc. Do NOT trigger for a single quick decision (route
  to the one matching skill), line-by-line code or correctness review
  (/code-review), or a request to edit, reformat, or rewrite the doc itself.
---

# Giant Brains (Router)

One door to the suite: hand it a doc, it triages once, runs the right two or three
lenses report-only, and returns one synthesized verdict — not N separate ones.

## Core idea

The suite's skills are different lenses on the same doc — take-a-step-back asks if
the frame is right, iron-triangle which corner is being traded, blast-radius how big
and how reversible, baseline-spec whether "better" is measurable, record-decision
whether the bet got written down. Nobody remembers to run five lenses by hand, and
running all of them every time produces a wall of findings that gets skimmed.

This skill routes instead: pick the lenses the doc's stage actually needs (three at
most), apply them report-only, dedupe what they share, and close with one
bottom-line-shaped call. It is a **router, not a runner** — member skills keep their
own logic, and nothing writes to the doc during the battery.

## Step 1 — Triage in one message

Ask only the questions the invocation didn't already answer, all at once:

> 1. Which doc? *(only if none is named and multiple candidates exist)*
> 2. Where does it stand? (a) draft — work hasn't started, (b) in progress —
>    roughly where, (c) complete — this is a retro.
> 3. Any lens you want added or skipped? *(optional — silence means the default route)*

If the user named the doc and stage at invocation, skip the questions entirely. The
battery is report-only, so once the stage is known there is nothing left to confirm —
announce the route in one line and run.

## Step 2 — Route by stage

Default routes, three lenses maximum per battery:

| Doc stage | Lenses (in order) | Each lens is asked |
|---|---|---|
| Draft | take-a-step-back, iron-triangle, blast-radius | Is the frame right? Which corner is being traded? How big and how reversible is the chosen path? |
| In progress | blast-radius (remaining work), iron-triangle (squeeze check) | How big is what's left, and has the deadline quietly shifted a corner since the plan was written? |
| Complete | decision-record audit (read-only), bottom-line (outcome cut) | Which Costly or One-way calls in this doc have no record in `decisions/`? What call does the retro actually support? |

Content overrides — swap a lens in, never exceed three. Each override names what
it displaces:

- The doc's goal is "better / faster / cheaper" with no metric attached →
  **baseline-spec replaces iron-triangle** (when "better" is unmeasured, the
  metric question subsumes the corner question); on a two-lens route it fills
  the empty third slot instead.
- The doc has ballooned — hedged, repetitive, restating itself → **bottom-line
  fills the empty third slot**; on a full draft route it replaces iron-triangle
  (its regret check preserves a thinner price read).
- If both overrides fire on a draft, the route becomes take-a-step-back,
  baseline-spec, bottom-line — **take-a-step-back is never displaced**.
- The doc is one decision, not a plan → no battery. Route to the single matching
  lens and say why (see the counter-example).

Never battery lenses:

- **record-decision** writes `decisions/` files. The Complete route's
  decision-record audit is the router's own read-only check for *missing*
  records — do not invoke the record-decision skill mid-battery; recording
  stays a Step 5 opt-in.
- **phase-qa** edits the doc — it is the follow-up *writer* for phased plans, never
  run mid-battery.
- **auto-improve** executes a loop — it only ever follows baseline-spec, on request.
- **linear** sequences execution — offer it after the report when the doc's steps
  are scattered.

Announce the route before running: "Running take-a-step-back, iron-triangle,
blast-radius against PLAN.md (draft)."

## Step 3 — Run the lenses, report-only

For each selected lens, in route order:

- Apply the member skill's method, by the first mechanism available: (1) invoke
  the sibling skill if it is installed; (2) otherwise, if the suite is on disk
  (this repo or a checkout), read the lens's `SKILL.md` and apply it; (3)
  otherwise apply its minimum contract below and say so in the report.
  Exception: the decision-record audit is always the router's own read-only
  check — never an invocation of record-decision.
- Suppress per-lens standalone output. Carry forward only the lens's headline and
  the one or two findings that would change the call — two to four lines each.
- Findings cite the doc (section or line), not vibes.
- A clean lens reports "no flag" in one line. Do not manufacture a finding to
  justify the lens having run.
- Hard rule: nothing writes to the doc, the repo, or `decisions/` during the
  battery. Writers come later, opt-in (Step 5).

### Lens minimum contracts (fallback only)

One line each — just enough to preserve a lens's calibration when its skill
can't be loaded. When the skill is available, its own definition wins.

- **take-a-step-back:** name the single most fragile assumption, the downside if
  it's wrong, and reversibility (Easy / Costly / One-way door) — one sharp
  counterpoint, not five.
- **iron-triangle:** name which of speed / cost / quality the plan quietly
  sacrifices and where the doc commits to it; point to scope as the release valve.
- **blast-radius:** size the path Small / Medium / Major, name concretely what
  breaks, rate undo as Easy / Costly / One-way door.
- **bottom-line:** compress to the decision and recommendation already in the
  doc — add nothing of your own but a one-line regret check; dramatically
  shorter than the source.
- **baseline-spec:** check that "better" has a scalar metric, an un-gameable
  oracle, and a budget with a captured baseline; name the missing pillar rather
  than blessing an unmeasurable goal.
- **decision-record audit:** list the doc's Costly / One-way calls that have no
  record in `decisions/` — read-only; recording happens in Step 5.

## Step 4 — Synthesize

Dedupe before reporting — the suite shares vocabulary, so overlaps are mechanical:
reversibility surfaces in both take-a-step-back and blast-radius — report it once,
strictest read wins; a sacrificed corner (iron-triangle) and a fragile assumption
(take-a-step-back) are often the same fact — merge them.

Report shape:

```markdown
**Battery:** PLAN.md (draft) — lenses: take-a-step-back, iron-triangle, blast-radius

**Frame (take-a-step-back):** [headline + the finding that changes the call, or "no flag"]
**Price (iron-triangle):** [...]
**Size (blast-radius):** [...]

**Bottom line:** [ship as-is / fix N named things first / reframe before starting]
**Regret check:** [the one hard-to-undo item across all lenses, or "all reversible"]
**Do next:** [single action]
```

## Step 5 — Offer writers, opt-in, one at a time

The battery never edits the doc; the report ends with at most the follow-ups the
findings justify:

- Phased plan that survived the battery → "/phase-qa to bake QA checklists into it?" (phase-qa lives in giant-brains-swe-skills; offer only if it is installed)
- A Costly or One-way bet surfaced → "/record-decision to write it down?"
- Steps scattered across the doc → "/linear for the execution sequence?"

Run one only on an explicit yes. If none is justified, end at Do next — no menu
for its own sake.

## Calibration

- **One-pager or single decision** → one lens, no battery (counter-example below).
  The battery earns its length on multi-phase, multi-commitment docs.
- **All lenses clean** → say so in about four lines and stop. "No real findings —
  plan is sound, all reversible" is a first-class result, not a failure to find
  something.
- Default cap is three lenses; exceed it only on the user's explicit request.

## Example — draft migration plan

Input: "/giantbrains MIGRATION.md — haven't started yet"

> Running take-a-step-back, iron-triangle, blast-radius against MIGRATION.md (draft).
>
> **Battery:** MIGRATION.md (draft) — lenses: take-a-step-back, iron-triangle, blast-radius
>
> **Frame (take-a-step-back):** The plan assumes the slow queries are the DB's
> fault — section 2 never tests whether the ORM's N+1s survive the migration. If
> they do, you migrate and keep the latency.
> **Price (iron-triangle):** The 3-week timeline with the same team quietly trades
> quality — section 4's "we'll backfill tests after cutover" is the sacrificed
> corner, named nowhere.
> **Size (blast-radius):** Medium and Costly — six services read this schema; the
> dual-write window in section 5 is the rollback path, but it ends at cutover.
> After that, undo is a second migration.
>
> **Bottom line:** Fix two things before starting: prove the N+1s die under the new
> DB (or the migration is moot), and move the test backfill before cutover, where
> the dual-write window still protects you.
> **Regret check:** Cutover ends the dual-write window — the one one-way step.
> Everything before it is reversible.
> **Do next:** Benchmark the top 5 slow queries against the new DB with the ORM in
> the loop — half a day, and it tests the plan's load-bearing assumption.
>
> Follow-up if useful: /phase-qa to bake checklists into the plan's phases,
> /record-decision to log the cutover bet.

## Counter-example — one decision is not a battery

Input: "/giantbrains — stress test this: should we name the internal CLI shipit
or deploykit?"

> This is one decision, not a plan — a three-lens battery would be ceremony.
> Routing to take-a-step-back alone.

Then take-a-step-back fires normally — and correctly deflates it: internal tool,
rename is a find-and-replace, Easy, pick one and move.

## When NOT to run

- **No doc.** A conversational question routes to a single skill or a plain answer.
- **A single decision** → the one matching lens, not a battery.
- **Line-by-line correctness or bug review** → /code-review; a QA-checklist diff
  review of a completed phase → /phase-qa (giant-brains-swe-skills, if installed).
- **The user wants the doc edited, reformatted, or rewritten** — this skill reads
  and reports; it never writes.
- **The lenses already ran individually this conversation** — re-running them as
  a battery is nagging, not coaching.
