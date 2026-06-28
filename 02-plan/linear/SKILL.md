---
name: linear
description: >-
  Restructure multi-step output into a single linear, numbered, step-by-step
  plan with branches as indented sub-bullets — concise but detailed. Use this
  whenever a response (yours or another agent's) contains multiple steps,
  instructions, or actions scattered across verbose prose, split across
  sections, or buried in explanations. Trigger when the user says "linear",
  "linearize", "make this step-by-step", "give me a plan", "what do I
  actually do", "put this in order", or pastes a verbose response and asks
  for the actionable sequence — including completion/status messages whose
  remaining work is scattered across "what I didn't do", "open items", and
  "next steps" sections. Also self-trigger when about to give 3+ procedural
  actions the user must execute themselves — but not for option comparisons,
  conceptual explanations, or summaries with no remaining work to execute.
---

# Linear

LLM responses often scatter actionable steps across a verbose answer: one step in the intro, two in a paragraph, an implicit step inside a caveat, a final step in the closing. The reader is forced to reverse-engineer the plan. This skill converts that into one canonical, linear plan a person can execute top-to-bottom without re-reading.

## When this applies

- The user pastes or references prior output and wants the actionable sequence extracted.
- You are composing a response containing 3 or more procedural steps the user will execute themselves.
- Steps exist but are out of execution order, duplicated, or interleaved with explanation.

If a response has 0–2 trivial steps, or no one is executing anything (status summaries, option comparisons, conceptual explanations), plain prose is fine — don't force the format.

## Core rules

1. **One plan, one place.** All steps live in a single unified list — numbered in chat responses; GFM task checkboxes (`- [ ]`) when writing into a `.md` file (see Output format). Never repeat or continue steps elsewhere in the response. If prose is needed (context, rationale, warnings), it goes *before* the plan, kept to 1–3 sentences.
2. **Execution order.** Steps are numbered in the order a person would actually perform them, including prerequisites first. Reorder the source material if necessary — fidelity to execution order beats fidelity to the original sequence.
3. **Concise but detailed.** Each step is as short as possible while keeping every detail needed to execute it without going back to the source: exact commands, file paths, names, values, flags. Strip filler ("you'll want to", "go ahead and", "it's a good idea to") but never strip operative detail. Default to one action per step; combine actions into one step only when splitting would add noise and no decision point, branch, or verification check falls between them.
4. **Branches as sub-bullets.** Conditionals, alternatives, and platform/option variations nest under the step they branch from — they never spawn a second list or a "but if..." paragraph later:
   - `If X:` / `If Y:` for conditionals
   - `Option A:` / `Option B:` for alternatives (state the default or recommendation)
   - Sub-details (flags, gotchas, expected output) as plain sub-bullets
   Keep nesting to 2 levels max (step → sub-bullet → sub-sub-bullet only when unavoidable).
5. **Deduplicate.** If the source states the same step multiple ways, merge into one step. For repeated actions, write the steps once and reference them — "Repeat steps 2–4 for each remaining file" — never write the same steps out multiple times.
6. **Surface the implicit.** Promote steps hidden in caveats or asides ("note that you'll first need to...") into real numbered steps in their correct position.
7. **Mark verification and stop points consistently.** Success signals go inline with `→ expect [observable result]`. Failure handling goes in a sub-bullet as `If [failure signal]: [fix or "stop here"]`. Use these exact markers throughout so checks are visually scannable.
8. **No trailing steps.** Nothing *actionable* after the list. Non-actionable wrap-up is fine and often useful: a one-line result summary ("Done — X is now Y"), assumptions made, or constraints to be aware of. Context, rationale, and prerequisites-as-prose belong *before* the list (1–3 sentences); anything the user must *do* belongs *in* the list.
9. **Unmask disguised step lists.** In status/completion messages, sections like "What I didn't do", "Open items", "Known issues", "Tracked for later", and "Suggested next steps" are usually the same list — remaining work — split across different rhetorical frames. Merge them into one "What's left" list in dependency order. While merging, split "didn't do" items into two kinds: *deferred work* (belongs in the list, in sequence) and *permanent non-goals* (one line after the list: "Out of scope: ..."). Truly independent items that block nothing and are blocked by nothing go on a final "Independent:" line rather than receiving a fake sequence position.
10. **State where this sits in the journey.** When the source is a completion message, phase update, or continuation of prior work, use the pre-list prose to say what was just completed or analyzed and, if knowable, which phase or milestone the remaining list belongs to. Keep it to one sentence unless a second sentence is needed to distinguish "done" from "left to do."

## Output format

```markdown
[1–3 sentences of context, only if genuinely needed. For status/completion/phase-related material, the first sentence should anchor the reader: what was just done/analyzed and which phase or milestone this list belongs to.]

1. First action — exact command/value/path inline.
2. Second action.
   - If condition A: do this instead.
   - If condition B: skip to step 4.
3. Third action. → expect [observable success signal]
   - Option 1 (recommended): ...
   - Option 2: ...
   - If [failure signal]: [fix, or stop here].
```

When the plan is being written into a `.md` file (doc, spec, runbook) rather than a chat reply, use GitHub-flavored Markdown task checkboxes with the step number inside the checkbox text — `- [ ] 1. Step text` (hyphen prefix, never bare `[ ]`) — so completion tracking and explicit sequence coexist. Sub-bullet branch rules are unchanged.

## Example

**Input (scattered):**
> To get this working you'll first want to install the CLI, which you can do with npm. Then there's some configuration to think about — the config file lives at ~/.toolrc and needs your API key. Oh, and note that on Linux you may need sudo for the install. Once configured, run `tool sync` to pull data. If sync fails with a 401, your key is wrong. Finally you can run `tool build`, though if you're on the beta channel you'd use `tool build --beta` instead.

**Output (linear):**
1. Install the CLI: `npm install -g tool`
   - If on Linux: prefix with `sudo` if you get a permissions error.
2. Add your API key to `~/.toolrc`.
3. Run `tool sync` to pull data. → expect "Sync complete"
   - If 401 error: API key is wrong — fix step 2 before continuing.
4. Build:
   - Stable channel: `tool build`
   - Beta channel: `tool build --beta`

## Quality check before responding

- Could someone execute this top-to-bottom without reading anything else? If no, a detail is missing — add it to the step, not to surrounding prose.
- Is any step stated twice, or does any instruction appear outside the list? If yes, consolidate.
- Is every "if/unless/depending on" expressed as a sub-bullet under its parent step?
