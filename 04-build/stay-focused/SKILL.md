---
name: stay-focused
description: Lock a whole working session to one anchor task so it can't be forgotten or side-tracked, and force every reply to lead with that task's live status in minimum-viable text. Type "stay focused on <task>" (or "stay on track for <task>") at the start of a session; every later reply then opens with the current state of that anchor — fixed? shipped? blocked on an unmerged branch? — followed by a horizontal rule and a tight rabbit-hole-style body (What's Shipped / What's Blocked / Recommended Next Steps / Optional Next Steps / Only Useful FYIs), each bucket one line, empty buckets dropped. Trigger when the user says "stay focused on X", "stay on track for X", "keep me focused on X", "/stay-focused", or asks you to stop wandering off the session's original task. If no anchor is named and none is set, ask what to lock onto rather than guessing. Turn it off with "/stay-focused off", "stop staying focused", or "drop the focus". Pairs with an always-on hook (see HOOKS.md) that re-injects the anchor every turn so it survives a long session. Do NOT let a user-requested tangent silently replace the anchor — serve it, then return to the anchor at the top of the next reply.
---

# Stay Focused

Pick one anchor task for the whole session. Lead every reply with its live status, then keep the rest short. Don't let the session wander off it.

Long working sessions drift. A task that started the session — *ship the CSV export*, *land the auth PR*, *fix the failing deploy* — gets buried under an hour of tangents, "while I'm here" detours, and follow-on questions, until nobody's tracking whether the original thing is actually done. This skill fixes the anchor at the top of the session and refuses to let it fall off the radar: **every reply reports the anchor's state first**, and the body underneath stays tight.

## Core idea

When invoked, do two things on **every** reply until turned off:

1. **Report the anchor first.** Open with one honest line on the current state of the anchor task — is it fixed, shipped, still in progress, blocked on an unmerged branch, not started, drifted, or unknown? Then a horizontal rule. The anchor status never sinks below the fold.
2. **Say only what's needed.** Minimum viable text. No preamble, no restating the question, no summary of what you're about to say, no padding a bucket that has nothing in it.

The anchor is captured once, from the user's own words — `stay focused on the auth refactor` sets the anchor to *the auth refactor*. It stays fixed for the session. A tangent the user explicitly asks for gets served, but it does **not** replace the anchor: the next reply still opens with the original task's status.

## Setting the anchor

- **Set:** `stay focused on <task>`, `stay on track for <task>`, `keep me focused on <task>`, or `/stay-focused <task>`.
- **No task given:** if the user types just `stay focused` and no anchor is set, ask in one line what to lock onto. Never guess the anchor.
- **Off:** `/stay-focused off`, `stop staying focused`, or `drop the focus`. Replies return to normal shape.

## Reply format

**Status of [anchor]:** one line — the true current state. Fixed / shipped / in progress / blocked on an unmerged branch / not started / drifted / unknown. This line is mandatory and always first.

---

Then only the buckets with real content, one line per item:

- **What's Shipped** — done and verified this session.
- **What's Blocked** — what's stuck, and on what.
- **Recommended Next Steps** — the moves you'd make next.
- **Optional Next Steps** — real but skippable.
- **Only Useful FYIs** — facts that change a decision. Nothing else earns a line.

Drop every empty bucket. Never invent an item to fill one — an empty section means there's nothing there, and faking it defeats the point. If everything is genuinely blocked, the status line and **What's Blocked** may be the whole reply. That's fine.

## Staying on track

- **Re-orient every turn.** Before answering, check the reply against the anchor. If the thread has drifted, name the drift in one line and pull back.
- **Tangents don't hijack the anchor.** Serve a user-requested detour, then reopen the next reply with the anchor's status. The anchor only changes when the user sets a new one.
- **Done means done.** If the anchor task is genuinely finished, say so plainly and ask whether to set a new one. Do not invent follow-on work to stay busy — that's the drift this skill exists to stop.
- **Never fake a status.** If you don't know the anchor's state, say "unknown — need to check" and name what you'd check.

## Always-on guard

The point of stay-focused is that it holds for a *whole* session — but plain skill instructions decay as context fills with tangents and other tools' output. An opt-in hook pair keeps the anchor and reply shape in the model's context on every turn, and re-injects them into a resumed session the next morning. See [HOOKS.md](HOOKS.md). Without the hooks, the skill still works — it just relies on the model remembering, which fades over a long session.

## How this differs from its siblings

- **stay-focused** (whole session, anchor) — "Here's the one task; report its status first every time and don't wander off it." A persistent frame over the session.
- **rabbit-hole** (during, consolidate) — "You keep finding things — stop, sweep once, triage, proceed." Cuts a mid-task drip. stay-focused *borrows its body format* but is about holding a session-long anchor, not batching findings.
- **linear** (on demand, sequence) — "The steps are scattered — put them in order." Shapes one response into a plan; stay-focused shapes *every* response around a fixed task.
- **bottom-line** (on demand, compress) — "Too much here — what's the call?" Distills overload once; stay-focused is a standing reply contract.
- **loose-ends** (after, completeness) — "Is anything forgotten?" Runs once at the end; stay-focused runs continuously so nothing gets forgotten in the first place.

## When to use

Use when:
- the user opens a session with `stay focused on X` / `stay on track for X` and wants that task held front-and-center for the duration
- a long session keeps sprouting tangents and the original goal is at risk of being forgotten
- the user wants every reply to lead with "is the thing I asked for done yet?" and stay terse

Do **not**:
- let a requested tangent silently become the new anchor — serve it and return
- invent buckets or next steps to fill the template — drop empty sections
- keep reporting a finished anchor as "in progress" to justify more work — say it's done and ask for the next one

## Example 1 — anchor set, then a tangent, then back

Input (session start): "stay focused on landing the rate-limiter PR."

Later input (a tangent): "wait, while you're in there, is the logging config still pointing at the old bucket?"

Output:

> **Status of landing the rate-limiter PR:** In progress — code complete, on branch `rate-limiter`, not yet merged (CI green, awaiting review).
>
> ---
>
> **Only Useful FYIs:** You asked about the logging config — yes, it's still pointing at the old bucket. That's a real issue but a separate one from the rate-limiter PR; flag it and I'll open a ticket, or say the word and I'll fix it as its own change. Either way the rate-limiter PR is the anchor and still needs a reviewer.

## Example 2 — the anchor is done

Input: "did the export finish?"  *(anchor: shipping the CSV export button)*

Output:

> **Status of shipping the CSV export button:** Shipped — handler wired, permission check sending, merged to `main`, verified with a live export.
>
> ---
>
> **What's Shipped:** Click handler, `orders:export` permission on the request, one end-to-end export confirmed.
>
> **Optional Next Steps:** A loading state on the button to stop double-clicks queuing duplicate downloads — nice, not required.
>
> The anchor is done. Want to set a new one, or keep this one open while you check the export in prod?

## Example 3 — no anchor named

Input: "stay focused"

Output:

> What should I stay focused on this session? Name the one task and I'll lead every reply with its status until it's done or you clear it.

## What success looks like

The user never loses the thread. Hours into a session full of detours, the top line of every reply still answers "is the thing I started with done, and if not, what's holding it up?" — in the fewest words that are actually useful.
