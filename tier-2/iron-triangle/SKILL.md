---
name: iron-triangle
description: Force an explicit speed-versus-cost-versus-quality tradeoff when an operator is under pressure to ship something faster, cheaper, or better than the constraints actually allow. Use this when the user is weighing "do it right" versus "just ship it," is tempted by an ambitious rework before doing the real work, is handed a fixed date without more resources, or says things like "we don't have time to do this properly," "fast, cheap, or good," "is it worth doing the right way," "should we cut scope," or "we can't afford to slow down." It names which corner of the triangle is being sacrificed, checks whether that sacrifice stays contained or compounds, and points to scope as the release valve.
---

# Iron Triangle

Name the corner you are sacrificing before the project names it for you.

A compact mini-workshop for the classic balancing act — **Speed**, **Cost**, and **Quality**, the famous *fast / cheap / good*. You can usually protect two, not all three. The trade is almost always being made *implicitly*; this skill makes it explicit, checks whether the sacrificed corner is one the operator can afford to lose, and reminds them that **scope** is the lever that can dissolve the tension entirely.

## The triangle

- **Speed** — how fast it ships.
- **Cost** — budget, time, people, and effort spent (the "cheap" corner: limited resources).
- **Quality** — how well it is built, and how little it will hurt later.

Pick two; optimizing for two corners spends the third:
- **Speed + Cost** (fast and cheap) → **Quality** gives. Fine for a throwaway; debt if it is a foundation.
- **Speed + Quality** (fast and good) → **Cost** gives. You pay with money, people, or overtime.
- **Cost + Quality** (cheap and good) → **Speed** gives. It will take longer than you want.

**Scope is the hidden fourth lever.** If all three corners are genuinely fixed, the only honest move left is to cut scope. "Do less, well" usually beats picking a corner to break.

## How this differs from the sibling skills

- **take-a-step-back** — "Am I making the best decision possible?" Questions the problem and the frame; it *surfaces* an ambitious option.
- **iron-triangle** — "Given I am doing this, which of speed, cost, or quality am I trading, and can I afford to?" It *prices* the option in the only three currencies that matter.
- **blast-radius** — "How big is the path I chose, and what breaks?"
- **bottom-line** — "Too much analysis — what's the call?"

Reach for this one the moment a decision creates tension between shipping fast, spending little, and doing it well — especially when someone is quietly sacrificing a corner without saying so.

## Output format

Lead with the trade in one line — the sacrificed corner must be impossible to miss. Then add only what changes the call. Keep it tight; if the trade is obvious, two lines is enough.

**The trade:** [You're optimizing for X and Y, which means Z is the corner giving way. One sentence.]

**Triangle check** — core:
- **Fixed (won't move):** [The corner(s) treated as non-negotiable right now, and by whom.]
- **Flexing (what gives):** [The sacrificed corner, named out loud — usually the one no one admitted to trading.]
- **Can you afford it?:** [Does losing that corner stay contained, or compound? Quality debt on a foundation compounds; on a throwaway it does not.]

Add from the menu only when it changes the call:
- **Scope lever:** [Can cutting or deferring scope relieve the tension instead of breaking a corner?]
- **False trilemma:** [Is there a cheap way to buy back the sacrificed corner — reuse, tooling, a smaller bet — so it is not really pick-two?]
- **Priority mismatch:** [If the chosen sacrifice contradicts the operator's stated priority, that mismatch is the headline.]

**Do next:** [Make the trade explicit and right-size it — time-box the quality cut, cap the spend, or cut the scope. One concrete move.]

**Missing:** [Only if you cannot tell which corner is actually fixed without a fact you do not have.]

## Principles

**Name the sacrificed corner out loud.** The trade is usually happening implicitly. The whole value is making it explicit and owned.

**Match the trade to the stated priority.** If the operator says speed matters most but the plan quietly sacrifices speed, that mismatch is the finding.

**Quality debt is only cheap while it stays contained.** A shortcut on a leaf is fine; a shortcut on a foundation compounds into the thing you cannot outrun. Say which one this is.

**Reach for scope first.** Cutting scope relieves the triangle without breaking a corner. Suggest it before telling someone to sacrifice quality or blow the budget.

**Two is the most you get.** Do not pretend all three are achievable. If someone is demanding fast, cheap, and good at once, that demand is itself the finding.

**Don't turn a clear call into a workshop.** If the right trade is obvious, state it in two lines and stop.

## Example 1 — restructure first, or just apply the change?

Input (abridged): "Before I make these changes, should I refactor the architecture to be modular and plugin-like, then re-apply the changes cleanly through that?"

Output:

> **The trade:** Restructuring first buys long-term **Quality** — a clean seam for this change and future ones — at a steep cost in **Speed** and **Cost** now; you would spend the budget on the foundation, not the feature.
>
> **Triangle check:**
> - **Fixed (won't move):** The changes themselves need to land.
> - **Flexing (what gives):** Speed-to-implementation — the refactor is a detour before any of the actual changes ship.
> - **Can you afford it?:** Only if several more changes will ride that seam. For a one-off, the modular rework is quality you never cash in.
>
> **Scope lever:** Extract only the one seam these changes actually need, not a full plugin architecture.
>
> **Do next:** Decide how many changes will ride this seam. One or two → apply directly and skip the rework. Many → extract just the shared seam, then apply through it.

## Example 2 — "do it right" vs "just ship it"

Input (abridged): "We're told to hit Friday's date, the code has to be production-grade, and we can't add people."

Output:

> **The trade:** You're being handed all three corners at once — fast (Friday), cheap (no new people), and good (production-grade). That is the impossible ask; something gives whether or not anyone names it.
>
> **Triangle check:**
> - **Fixed (won't move):** Date and headcount are both being held.
> - **Flexing (what gives):** With speed and cost pinned, **Quality** is what silently slips — corners get cut under deadline and no one decided to cut them.
> - **Can you afford it?:** Depends entirely on scope. Unmanaged, the quality loss lands wherever the deadline bites hardest, which is rarely where it is safe.
>
> **Scope lever:** Ship a smaller, genuinely production-grade slice by Friday and defer the rest — shrinking what "it" means is the only way to honor all three constraints.
>
> **Do next:** Take the trade back to whoever set it — name that fast + cheap + full-scope forces a quality cut, and propose the scope cut that protects both the date and the bar.

## What success looks like

The operator sees, in one glance, which corner they are about to sacrifice and whether they meant to. The best result is often the realization that the real lever is scope, not heroics — that "do less, well" beats "do it all, badly."
