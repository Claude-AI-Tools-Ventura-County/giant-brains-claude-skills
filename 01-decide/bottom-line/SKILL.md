---
name: bottom-line
description: |
  Distill long, verbose, or repetitive output—especially from Claude or other AI agents comparing options, tradeoffs, and recommendations—into a short, deduplicated bottom-line summary. Surface the real decision, a clear recommendation, and any choice that would be hard to reverse later. 

  Trigger when content is decision- or tradeoff-oriented and the user asks for the bottom line, TLDR, gist, takeaway, to cut to the chase, summarize cleanly, says it is too long/verbose/repetitive, or asks what they actually need to decide or might regret. Also self-trigger when prior agent output is long-winded, hedged, or repetitive and a decision needs to be pulled out clearly, even without those exact words. 

  Do not trigger when the user wants procedural steps, commands, or an execution sequence; that is /linear's job, not this skill's. 
---

# Bottom Line

Turn a long, hedged, repetitive block of decision-making output into the shortest summary that still lets the reader decide and act. The source is usually a previous Claude or agent response full of restated context, duplicated points, and excessive structure. **The summary must be dramatically shorter than the input — if it isn't, the skill has failed.**

## Core idea

You are compressing, not re-deciding. Pull out the decision and the recommendation that are *already in the text*; do not invent new options or fresh analysis. The one sanctioned judgment you add is the **regret check** (below) — a reversibility read on the choices already on the table, never a new option. The reader wants to stop reading the long version and move.

## Output format

Default to this shape. Drop any block that doesn't apply — never pad to fill the template.

**Bottom line:** [1–2 sentences: the recommendation, or the single thing that matters most. Lead with the answer, not the setup.]

**Context:** [1 line: what was just done, completed, or analyzed, and if relevant which phase/milestone this belongs to. Use when the source is a status update, phase check-in, completion message, or continuation of ongoing work.]

**You're deciding:** [the real choice, as one crisp question. Omit if there's no decision — just information.]

**Options:**
- **[Option A]** — [the one-line case for it]. *Best if [condition].*
- **[Option B]** — [one-line case]. *Best if [condition].*

**Regret check:** [the one decision here that's hard or costly to undo, and why — plus the cheapest way to keep it reversible if there is one. "All reversible" if nothing qualifies. One line.]

**Do next:** [the single most important action, one line. If the next action expands to multiple steps, write "Do next: run /linear for the execution sequence" — do not list steps here.]

### Scaling

- **One option / no real choice** → drop the Options block; Bottom line + Do next, plus Regret check if committing to that single path is hard to undo.
- **No decision at all, just a long explanation** → replace "You're deciding", "Options", and "Regret check" with **Key points:** (3 bullets max); keep Bottom line and Do next.
- **2–4 genuine alternatives** → the bullet list above.
- **Status / completion / phase-related source** → include `Context:` unless the just-completed work and phase are already obvious from the Bottom line itself.
- **Regret check** appears whenever a commitment is being made — it's the answer to "is there a decision in here I might regret later?". Omit it only in the no-decision "Key points" mode, where nothing is being chosen.
- **Use a table only** when options trade off across the same 2–3 named dimensions and a table is genuinely denser than bullets. Otherwise bullets win, especially on mobile.
- **Several independent decisions bundled together** → split into separate mini-blocks, each with its own one-line bottom line. Don't blur them into one mushy summary.

## Principles

**Lead with the answer.** The first line is the recommendation. No "Great question", no recap of what the long version was about, no throat-clearing.

**Anchor the reader in the workstream.** When the source is part of an ongoing project, status update, or phase boundary, include a one-line `Context:` immediately after the Bottom line that says what just happened and, if knowable from the source, which phase or milestone it belongs to. This is not a second summary — it is a location marker so the reader knows where they are in the journey.

**Deduplicate ruthlessly.** Agent output states the same point three ways — once in the intro, once in the body, once in a closing "to summarize". Collapse all restatements into one. If two "options" differ only in wording, they are one option.

**Strip the noise.** Cut hedging ("it depends", "there are many factors"), context the reader already has, meta-commentary about the analysis itself, and pros/cons that don't change the decision. Keep only what moves a choice.

**Frame decisions as choices, not prose.** "You're deciding between X and Y" beats three paragraphs circling the same fork.

**Keep real tradeoffs, kill fake ones.** A tradeoff earns a line only if it would actually flip someone's pick. Points that are identical on both sides are deletions.

**Be honest about complexity.** If the source has no clear winner, say so in the bottom line ("No clean winner — comes down to [factor]") and name the deciding factor. Don't fake confidence to sound tidy.

**Surface the one-way door.** Answer "is there a decision here I might regret later?" Most choices are two-way doors — cheap to reverse — and you should *not* flag those. Single out only a decision that's genuinely hard or costly to undo: heavy migration or rewrite to back out, lock-in (long contracts, vendor commitments, public or customer-facing promises, things others will build on), foreclosed future options, or a large blast radius if it's wrong (data loss, money, security, reputation). Name it in one line with the reason, and if it fits, the cheapest way to keep it reversible — pilot first, hide it behind an abstraction, delay the lock-in. If nothing qualifies, say "all reversible" plainly so the reassurance is explicit. This is the one place the summary adds judgment beyond the source; keep it to a single line.

**Flag missing inputs, briefly.** If the text can't actually support a decision because something's absent, add one line: `Missing: [what you'd need to decide]`. Don't fill the gap with a guess.

## Length discipline

Aim for the summary to be roughly a fifth of the source or less, and under ~10 lines for a typical case. The bottom line itself is 1–2 sentences. If the user says "shorter", collapse to the bottom-line sentence plus Do next.

## Formatting

Use GitHub-flavored Markdown. If Do next is genuinely a few discrete steps rather than one action, a tiny checklist is fine — use hyphen-prefixed boxes (`- [ ]`), never bare `[ ]`. Otherwise keep Do next to a single line.

## Examples

**Example 1 — verbose options dump → clean decision**

Input (abridged): ~12 paragraphs weighing keeping a managed DB vs. self-hosting, restating the same timeout concern three times, full of "on the one hand / on the other hand".

Output:
> **Bottom line:** Move to self-hosted Postgres on GCP. The managed tier's function timeouts already broke the pipeline once, and volume only grows from here.
>
> **You're deciding:** Stay on the managed DB, or run your own Postgres for the pipeline.
>
> **Options:**
> - **Managed DB** — zero migration, fastest to keep. *Best if volume stays small and timeouts are tolerable.*
> - **Self-hosted Postgres (GCP)** — no timeout ceiling, full control, more ops work. *Best if you're ingesting large batches or running long queries.*
>
> **Regret check:** Self-hosting puts backups, patching, and uptime on you — reversible, but migrating back out is real work. Keep the schema portable so the door stays two-way.
>
> **Do next:** Stand up the GCE Postgres instance and repoint the ETL at it.

**Example 2 — long explanation, no decision → key points**

Input (abridged): a long write-up of why a build takes 28 minutes, repeating that the parser is the bottleneck several times.

Output:
> **Bottom line:** The 28-minute run is almost entirely one parser bottleneck; PyPy plus selective decode is the highest-leverage fix.
>
> **Key points:**
> - ~90% of the time is in the streaming parser, not I/O.
> - PyPy alone is expected to cut the most.
> - Selective decode skips fields you never read.
>
> **Do next:** Benchmark PyPy on the full dump before changing anything else.

## What success looks like

The reader can decide in about 15 seconds without opening the long version, and nothing load-bearing was lost. Shorter is the goal; clarity is the constraint.

## Review History

<!-- Append-only: one row per review/audit pass. Never edit or delete a past row. -->

| Date | Reviewer | Outcome | Notes |
|---|---|---|---|
| 2026-06-28 | noelsaw1 | Seeded | Baseline row from git history (last content change); no formal review conducted yet. |
