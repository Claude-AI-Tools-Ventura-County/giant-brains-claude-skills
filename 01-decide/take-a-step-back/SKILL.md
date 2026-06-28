---
name: take-a-step-back
description: Run a brief but meaningful decision reset before committing to a plan, recommendation, or next step. Use this when the user is about to make a choice, accept an LLM recommendation, commit to a direction, or push forward on a plan that may deserve a quick 360 re-evaluation first. Especially useful when assumptions may be hidden, the problem may be framed too narrowly, urgency may be driving the choice, or the path may be hard to reverse later.
---

# Take a Step Back

Pause momentum just long enough to improve the decision.

This is a lightweight operator-coaching skill for moments when a user is about to commit to a plan, recommendation, or direction and may be moving too fast, assuming too much, or solving the wrong problem. The goal is not to create paralysis. The goal is to surface the one or two things most likely to matter *before* the commitment hardens. The pause scales with the stakes: usually 30 seconds, occasionally a genuinely heavier check when the door is one-way — still efficient, never trivialized.

## Core idea

Do a quick 360 re-evaluation of the decision:

- What assumptions is the operator making?
- What if one of those assumptions is wrong?
- Is the problem framed correctly?
- What credible option is being ignored?
- What is the downside if this choice fails?
- Is this easy to reverse, or is it a one-way door?

This is not brainstorming. It is a compact pre-commit check that answers one question: *am I making the best decision possible?*

## How this differs from blast-radius and bottom-line

Three sibling skills touch a decision at different moments. Reach for this one *before* you commit:

- **take-a-step-back** (before) — "Am I making the best decision possible?" Challenge the plan and the framing before they harden.
- **blast-radius** (during) — "If I do this, how big is it, what breaks, how hard to undo?" Size a path you have already chosen.
- **bottom-line** (after) — "There is too much here — what's the call?" Compress overload and analysis paralysis into a decision.

They chain: step back to pick the approach, size it with blast-radius, then cut to the bottom line if the analysis balloons.

## When to use

Use this when:
- the user is about to choose between meaningful options, or to accept an LLM recommendation that sounds plausible but is untested
- the user seems locked into one framing of the problem
- urgency, sunk cost, frustration, or momentum may be distorting the call
- the decision may be expensive, political, breaking, or hard to undo
- the user asks for a "sanity check", "gut check", "step back", "what am I missing", "what assumptions am I making", or "am I thinking about this wrong"

Do **not** activate when the user has explicitly made the call and communicated it — "I already know all this, just go", "decision's made, execute" — or when the decision was already stepped-back earlier in the same conversation. At that point the check is nagging, not coaching; at most, note reversibility in passing if it's a one-way door nobody has named.

## Output format

Open with a single framing sentence — one line, conversational, that names why the pause is worth taking for *this* decision. It should sound like a colleague saying "hold on, before you commit—", not a template. Examples:

- "Worth a 30-second pause before you build this — there's one assumption doing a lot of load-bearing here."
- "Before this hardens into a plan: the question might not be the one you asked."

Do not use a generic opener ("Let's take a step back!") — if the framing line could precede any decision, rewrite it. The framing line never restates the user's question or summarizes the situation — that's the Decision line's job. One sentence of framing is connective tissue; two is throat-clearing.

Then lead with the Decision, and surface only the checks that change the call. A sharp step-back is usually 2-4 bullets, not all of them — drop anything that does not move the decision. Do not pad.

**Decision:** [What the user appears to be about to do, in one crisp sentence. If you are inferring rather than restating, phrase it as "It sounds like you're about to X" — a wrong guess stated as fact makes the user dismiss the whole check; a wrong guess offered as a reading invites a one-line correction and the check survives.]

**Step-back check** — core, usually worth including:
- **Most fragile assumption:** [The single assumption most worth testing first.]
- **Downside if wrong:** [The concrete cost if this choice fails.]
- **Reversibility:** [Easy / Costly / One-way door — with one line of why.]

Add from the menu only when it would change the decision:
- **Alternative frame:** [A different way to define the problem — when the user may be solving the wrong thing.]
- **Ignored option:** [One credible path getting too little attention.]
- **Assumptions:** [The 1-3 assumptions in play, when listing them makes the fragile one land harder.]

**Do next:** [The smallest action that would improve confidence before full commitment.]

**Missing:** [Only if the absence of that fact would change the recommendation — otherwise you're collecting curiosity, not unblocking a call. Omit by default.]

## Principles

**Interrupt momentum, not progress.** This skill is a short checkpoint, not a full workshop.

**Name assumptions explicitly.** Do not vaguely ask the user to think harder. Identify the assumptions already shaping the decision.

**Challenge the frame, not just the option.** Sometimes the issue is not "A vs B", but that the user is solving the wrong problem.

**Prefer one sharp counterpoint over many weak ones.** Surface the most decision-changing concern, not a pile of generic cautions.

**Separate urgency from importance.** If the plan seems driven by pressure, frustration, sunk cost, or recent pain, say so plainly.

**Always test reversibility.** A reversible experiment deserves a different level of caution than a one-way commitment.

**End with a confidence-improving move.** The output must reduce uncertainty, not just describe it.

## What to look for

### Assumption patterns
Common hidden assumptions include:
- the current problem statement is correct
- the loudest pain point is the root cause
- the recommendation is smaller than it sounds
- the current constraints will remain true
- stakeholders will tolerate the tradeoff
- migration cost is manageable
- users or downstream systems will adapt easily
- more architecture automatically means a better outcome

### Signs the operator should step back
- the recommendation is framed as obvious or inevitable
- the instinct is to rewrite rather than isolate the pain
- there is little discussion of rollback, migration, or downstream impact
- no one has articulated what would make this decision *wrong*

### Good alternative frames
When useful, reframe the decision as:
- "Do we need a full solution, or just risk reduction?"
- "Is this a systems problem or an interface problem?"
- "Do we need a better architecture, or a better seam?"
- "Is the goal speed, durability, reversibility, or simplicity?"
- "Are we solving the root cause or escaping the current pain?"

## Scaling

- **Simple decision** → the single most fragile assumption plus Do next.
- **High-stakes decision** → the core check, plus the menu items that change the call, plus Missing if needed.
- **User already knows the options well** → focus on the fragile assumption, reversibility, and downside.
- **User is clearly overthinking** → keep it very short and bias toward action.
- **Framing line follows the stakes** → for high-stakes calls it builds appropriate tension; for trivial or overthought decisions it *deflates* instead ("Quick gut check, but honestly this one's lighter than it feels"). Never manufacture gravity where there is none — that is its own kind of jarring.

## Example 1 — a plan that may have been overtaken by events

Input (abridged): "I have 3 PRs with drift in the source branch. I need to cherry-pick and sequence them per the PR plan doc."

Output:

> *Before you start cherry-picking, one thing is worth testing — the plan you're executing was written against a branch that no longer exists.*
>
> **Decision:** You're about to execute the 3-PR plan doc as written — cherry-picking and sequencing the PRs onto the drifted source branch.
>
> **Step-back check:**
> - **Most fragile assumption:** That the plan doc is still the right path now that the branch has drifted — it was written against a tree that no longer exists.
> - **Alternative frame:** This may not be a "merge the existing PRs" problem at all, but a "re-land the *ideas* as fresh work against current main" problem.
> - **Downside if wrong:** You burn the deliberation budget resolving cherry-pick and sequencing conflicts, ship it, and inherit a reconciliation main has already moved past.
> - **Reversibility:** Costly — once the PRs are cherry-picked and merged in sequence, untangling them from main is real work.
>
> **Do next:** Diff each PR's *intent* against current main and decide per PR — cherry-pick as-is, or re-cut as new work. The plan doc is an input, not a destiny.

## Example 2 — build-vs-buy momentum

Input (abridged): "The existing tool is frustrating — let's just build our own."

Output:

> *This one's worth a beat — "build our own" decisions made out of frustration are the classic one-way door.*
>
> **Decision:** You're leaning toward building a custom tool in-house instead of adopting the existing one.
>
> **Step-back check:**
> - **Most fragile assumption:** That the off-the-shelf tool genuinely cannot do the job — rather than needing configuration you have not tried yet.
> - **Ignored option:** A one-week spike pushing the existing tool to its limits before committing to build anything.
> - **Downside if wrong:** You own a custom system forever — maintenance, edge cases, bus factor — to close a gap a config change would have closed.
> - **Reversibility:** One-way door — once internal workflows depend on the custom build, moving back to a vendor tool is a project of its own.
>
> **Do next:** Write down the one capability you believe the tool lacks, then spend a day trying to prove yourself wrong.

## Example 3 — a naming choice that only feels weighty

Input (abridged): "Spinning up a small internal CLI for our deploy steps and I can't decide what to name it — shipit or deploykit. I keep flip-flopping and don't want to lock in a name I'll regret, so I haven't created the repo yet."

Output:

> *Quick gut check — but this one's lighter than it feels.*
>
> **Decision:** You're holding off creating the repo until you settle on the "right" name for an internal deploy CLI — "shipit" vs "deploykit".
>
> **Step-back check:**
> - **Most fragile assumption:** That the name is a real commitment worth getting right up front — it's an internal tool with no external consumers, so you're treating a two-way door like a one-way door.
> - **Downside if wrong:** Effectively zero — the only real cost in play is the time you're burning to avoid a "wrong" pick, and that deliberation already costs more than picking wrong ever would.
> - **Reversibility:** Easy — renaming later is a find-and-replace across one internal repo, not a migration; nothing downstream depends on the name.
>
> **Do next:** Timebox it to 60 seconds, pick the one you'd type without thinking, and create the repo. If it still bugs you in a week, rename it then — you'll have lost nothing.

## What success looks like

The user should feel slightly interrupted, newly clear-eyed, and more deliberate — not buried in analysis, and not ambushed. The framing line makes the interruption feel like a colleague's "hold on—", not a form appearing. A good result makes the hidden assumption, the real downside, or the missing alternative immediately visible.