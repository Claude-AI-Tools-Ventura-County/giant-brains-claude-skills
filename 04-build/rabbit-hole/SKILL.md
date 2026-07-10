---
name: rabbit-hole
description: Stop the drip of one-more-thing on a task that was supposed to be simple, and replace it with a single end-to-end triage that puts every issue on the table at once. Use when an agent keeps surfacing problems piecemeal (death by a thousand cuts), keeps adding unrequested work (scope creep, gold-plating, "while I'm here..."), or wanders off the asked task into refactors and tangents. Trigger when the user says "you keep finding one more thing", "stop nickel-and-diming this", "this was supposed to be simple", "stop going down rabbit holes", "just do a full pass and tell me everything", "triage it all at once", or invokes /rabbit-hole. Also self-trigger when you are about to raise a third unsolicited mid-task finding on a task the user explicitly framed as small ("quick", "simple", "one-line", "just"). Do NOT fire on genuinely open-ended or exploratory work where incremental discovery is the point, or during an active debugging session where each finding narrows the next step.
---

# Rabbit Hole

Stop the drip. Do one pass. Put everything on the table at once, sorted by whether it actually matters.

This fires when a task that was supposed to be small keeps growing — not because the work is genuinely large, but because issues, ideas, and "while I'm here" additions are arriving one at a time. Each interruption is individually reasonable and collectively exhausting: death by a thousand cuts. The fix is not to suppress the findings. It is to **consolidate** them — sweep the whole task end to end *once*, surface everything together, sort it into what must happen versus what is optional versus what should be dropped, and then proceed only on an agreed set without re-opening the drip.

## Core idea

When invoked, do three things in order:

1. **Stop.** No more piecemeal "one more thing" for this task. Hold every pending and new finding.
2. **Triage once.** One end-to-end pass over the task. Collect every candidate issue, improvement, and tangent, then sort each into exactly one bucket:
   - **Blocking** — the task is wrong, broken, or incomplete without it.
   - **In scope, optional** — a real improvement that fits the task; the user chooses.
   - **Out of scope / dropped** — gold-plating, YAGNI, or a tangent. Named explicitly so it stops resurfacing.
3. **Get the nod, then proceed.** Recommend the set worth doing (usually: all blocking, maybe one optional), ask the user to confirm that set, then execute only the agreed items — without spawning fresh interruptions. For a blocking-only set the nod can be a quick "go"; don't turn the gate into its own ceremony.

The discipline that makes this work: after the triage, anything new gets appended to the out-of-scope / dropped list, not raised as a new interruption. The user got the full picture once; they don't get nickel-and-dimed again.

## Always-on guard (optional)

Invoking this skill by hand means noticing the drip first — usually two or three
interruptions in. An opt-in hook pair puts the trigger rule in the model's
context every turn so it fires on itself instead. See [HOOKS.md](HOOKS.md).

## How this differs from its siblings

- **rabbit-hole** (during, consolidate) — "You keep finding things — stop, sweep it all, sort it, then proceed." Cuts the drip mid-task.
- **loose-ends** (after, completeness) — "Is anything forgotten?" Runs once work exists, hunting what's *absent*.
- **ponytail** (always, minimalism) — "What's the laziest thing that works?" Rabbit-hole *uses* YAGNI as its cut criterion but is about batching and gating, not minimizing.
- **take-a-step-back** (before, framing) — "Am I solving the right problem?" Resets a decision, not a sprawling task.

## When to use

Use when:
- the user signals the AI is dripping work: "one more thing again", "stop nickel-and-diming", "this was a one-line change", "stop the rabbit holes", "just give me everything at once"
- a small, explicitly-scoped task has accumulated several mid-flight additions
- you (the agent) are about to raise a third unsolicited finding on a task the user explicitly framed as small ("quick", "simple", "one-line", "just") — fire on yourself instead of interrupting again

Do **not** fire when:
- the work is genuinely open-ended or exploratory and incremental discovery *is* the method
- you're mid-debug and each finding narrows the *same* bug — that's legitimate tracing, not drip (use debug-mantra). But if mid-debug you start surfacing *unrelated* issues, this still applies to those.
- the user explicitly wants the deep dive — "yes, find everything, take your time"
- the task really is large; consolidating doesn't shrink real scope, and pretending it does is its own failure (say so plainly)

## Output format

Open with one framing line in a colleague's voice — "let me stop and put it all on the table" — never a generic template opener. Then:

**Task (as scoped):** [The small thing actually asked for, one line, in the user's own words. This is the yardstick every bucket is measured against — stating it plainly lets the user catch a scope mismatch here ("fix the typo" vs "fix the footer") before it skews the whole triage.]

**Triage** — one consolidated sweep, sorted:

- **Blocking** *(do these or the task isn't done):*
  - [issue — one line, why it blocks]
- **In scope, optional** *(real, your call):*
  - [improvement — one line, the tradeoff]
- **Out of scope / dropped** *(named so it stops coming back):*
  - [tangent / gold-plating — one line, why it's out]

**Recommendation:** [The set worth doing — usually all blocking, plus at most one optional. One sentence.]

**Proposing to proceed on:** [Exactly the agreed set you'd execute next — then ask for the nod. On "go", execute only this set, no fresh interruptions.]

Drop any bucket that's empty. If everything lands in "blocking," the task was never simple — say that instead of faking a tidy list.

## Principles

**Consolidate, don't suppress.** The goal is one honest picture, not silence. Every real issue still appears — just together, once.

**Sort by the task, not by what's interesting.** A finding is blocking only against what was actually asked. "Technically true" is not "in scope." Gut-check every "blocking" item against the sunk-cost pull to justify the digging: *if you hadn't already stumbled on it, would you still flag it as blocking for the exact task the user asked for?* If no, it's optional or dropped.

**Drop out loud.** A dropped item is named and parked, not hidden. That's what stops it from returning as the next interruption.

**Default to the smallest agreed set.** Bias toward blocking-only. Optional items are offered, not smuggled in.

**One interruption budget.** After the triage, you've spent it. New findings go on the out-of-scope / dropped list silently — you don't re-open the drip.

**Don't fake simplicity.** If the sweep proves the task is genuinely big, the honest output is "this isn't small," not a triage that pretends it is. And if "bigger" turns out to be a real decision rather than just more work (migrate or not, rewrite or patch), name it and hand to take-a-step-back — that's a framing call, not a triage.

## Example 1 — a "quick copy fix" that grew

Input (abridged): "I just asked you to fix a typo in the footer and you've now flagged the footer markup, an a11y issue, an unused import, and 'the whole component could be refactored.' This was one word. Stop."

Output:

> *Fair — let me stop adding to it and just lay out everything I've spotted at once, sorted by what actually matters for your typo fix.*
>
> **Task (as scoped):** Fix the typo in the footer text.
>
> **Triage:**
> - **Blocking:**
>   - The typo itself — the only thing the task requires.
> - **In scope, optional:**
>   - Unused import two lines up — a one-line delete while the file's open, zero risk. Take it or leave it.
> - **Out of scope / dropped:**
>   - Footer markup cleanup — real but unrelated; parked.
>   - A11y label gap — worth a real ticket, not a drive-by in a copy fix.
>   - Component refactor — that's a project, not a typo. Dropped hard.
>
> **Recommendation:** Fix the typo. Delete the unused import only if you want the freebie.
>
> **Proposing to proceed on:** Just the typo — say go and I'll make only that change. The a11y item is worth its own issue if you want one; otherwise it stays parked.

## Example 2 — the sweep reveals the task wasn't actually small

Input (abridged): "Stop going down rabbit holes — I just wanted to bump the library version."

Output:

> *Let me do one pass and put it all on the table — but honest heads-up, this one doesn't shrink the way I'd like it to.*
>
> **Task (as scoped):** Bump the library from v2 to v3.
>
> **Triage:**
> - **Blocking:**
>   - v3 removed the `parse()` signature you call in four places — the build won't compile without updating them.
>   - The config format changed; the current config silently no-ops on v3.
> - **In scope, optional:**
>   - v3's new async API would simplify two call sites — nice, not required.
> - **Out of scope / dropped:**
>   - Migrating the *other* library that's also outdated — different task, parked.
>
> **Recommendation:** This isn't a one-line bump — it's a small migration. The two blocking items are mandatory; I'd skip the optional refactor to keep the change reviewable.
>
> **Proposing to proceed on:** The version bump plus the two blocking fixes, as one change — flagging the real scope up front, not dripping it out. Say go and I'll do exactly that set; or tell me to park it if a small migration isn't what you want right now.

## Example 3 — not just code: a one-fact edit to a document

Input (abridged): "I asked you to fix the wrong revenue number in the Q3 summary and you've come back with that plus passive voice, a weak intro, and 'this section should be restructured.' Just the number."

Output:

> *Got it — let me put everything I noticed in one place, ranked against the fix you actually asked for.*
>
> **Task (as scoped):** Correct the revenue figure in the Q3 summary.
>
> **Triage:**
> - **Blocking:** The wrong number itself — the only change the task requires.
> - **In scope, optional:** One sentence next to it restates the old figure, so it'll now contradict the fix — worth a matching tweak.
> - **Out of scope / dropped:** Passive voice, the intro, the restructure — all real style notes, none of them this edit. Parked.
>
> **Proposing to proceed on:** The number, plus the one contradicting sentence so the doc stays consistent. Say go. The style pass is a separate task if you want it later.

## Example 4 — simulated output with made-up project data

Input (simulated): "Please just hook up the Export CSV button on the orders page. This was supposed to be quick."

Output:

> *Let me stop the drip and put everything I found on the table once, against the quick button hookup you actually asked for.*
>
> **Task (as scoped):** Hook up the Export CSV button on the orders page.
>
> **Triage:**
> - **Blocking:**
>   - The button currently calls no handler, so clicking it does nothing.
>   - The export endpoint rejects requests without the `orders:export` permission check the page is supposed to send, so the feature would look broken for allowed users.
> - **In scope, optional:**
>   - Add a loading state on the button during export so repeated clicks do not queue duplicate downloads.
> - **Out of scope / dropped:**
>   - Reworking the whole orders toolbar layout — unrelated to wiring the action.
>   - Replacing CSV with XLSX export — different feature, parked.
>   - Cleaning up two nearby lint warnings — real, but not part of this button task.
>
> **Recommendation:** Do the two blocking items and skip the rest for now; the loading state is reasonable, but not required to make the button work.
>
> **Proposing to proceed on:** Wire the click handler and send the required permission-aware export request, as one small change. Say go and I'll stick to exactly that set.

## What success looks like

The user goes from "it keeps interrupting me" to "okay, I can see the whole thing and decide." There's exactly one list, sorted by what matters to the task they actually asked for, with the noise named and set aside — and then the agent gets back to work instead of finding a fourth thing.
