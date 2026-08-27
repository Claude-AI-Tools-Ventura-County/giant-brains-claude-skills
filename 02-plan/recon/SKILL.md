---
name: recon
description: >-
  Trace the current system end to end — entry points, call paths, every read
  and write of the state involved, the contracts crossed, the failure and
  rollback paths — and write it down as a Recon Map before any plan is drafted.
  Fires before authoring a build plan, spec, RFC, phased plan, refactor,
  migration, or "how would we add X" design, and whenever the user says
  "write a plan", "plan this out", "design this", "how should we build X",
  "refactor X", "migrate X", "what would it take to change X", or asks how far
  a change ripples. Also self-trigger before you write any plan step whose
  blast radius names code you have not actually read, and before answering
  "will this break anything?" Fans the trace out across 3-4 parallel subagents
  (entry paths, state, contracts, failure paths) and uses the codebase-memory
  knowledge graph when it is installed, falling back to grep. Produces a Recon
  Map file plus a short chat verdict, and never writes the plan itself. Do NOT
  fire for a single-file change with no external callers, a typo or copy edit,
  a question answerable from one file already in context, or when a current
  Recon Map for the same subsystem already exists.
---

# Recon

Read the system before you plan it. A plan written from the prompt plus three grepped files is fiction with headings.

The failure this skill exists to stop: an agent asked to "write a plan" produces a confident, well-structured document whose steps reference call paths nobody traced, state nobody inventoried, and contracts nobody knew were there. The plan looks complete. The blast radius section is invented. Recon makes the trace a **deliverable with named artifacts**, produced *before* the first plan heading, so the plan is grounded in edges that exist at `file:line`.

## The one rule

> No plan step may name a blast radius that includes code nobody read.

Everything below serves that rule. If a step touches a caller, the caller is in the map with a line number. If it cannot be found, it is in the Unknowns list — never silently assumed absent.

## When to run it

**Run recon when** the ask is to plan, design, spec, refactor, migrate, or size a change; when the change crosses more than one file; or when you are about to claim something is or is not affected.

**Skip recon when** — the calibration counter-example, and it matters as much as the trigger:

- The change is one file with no external callers (a string, a copy edit, a local helper's body).
- The question is answerable from a file already in context.
- A Recon Map for this subsystem exists and no relevant commit has landed since. Re-read it; do not re-run.
- The user has already traced it and hands you the edges.

In those cases say "recon skipped — [one-line reason]" and go straight to the work. A recon on a rename is ceremony, and ceremony is how a gate gets ignored when it counts.

## Step 1 — Scope the trace (one message, then go)

Name the **subject** in one line: the function, module, table, endpoint, or feature the change lands on. Name the **change class**: local edit, cross-module change, contract change, state/authority change, or replacement. If the class is state/authority, stop and run [spike-360](../spike-360/SKILL.md) first — recon maps a system; spike-360 decides whether a new source of truth should exist at all.

Do not ask more than one clarifying question. If the subject is ambiguous, pick the most likely reading, state it, and trace that.

## Step 2 — Seed from the knowledge graph if it is installed

If the `codebase-memory` MCP server is available, use it first — it answers "who touches this" in one call instead of twenty greps:

- `index_status` / `list_projects` — is this repo indexed? If not and the repo is large, offer `index_repository` once and say what it costs; if declined, fall through to grep and note the degraded mode in the map.
- `get_architecture` — the shape of the system before the details.
- `search_graph(name_pattern | label | qn_pattern)` — locate the subject's symbols.
- `trace_path(function_name, mode=calls | data_flow | cross_service)` — the edges. This is the tool that earns the skill its name.
- `get_code_snippet(qualified_name)` — exact source for anything load-bearing.
- `search_code(pattern)` — graph-augmented grep for the rest.

**The graph is a lead, not a citation.** It can be stale, and it does not see config, SQL strings, templates, shell scripts, cron, or dynamic dispatch. Every edge that a plan step will depend on gets confirmed by reading the actual file. An edge that exists only in the graph is marked `graph-only` in the map.

No graph installed? Say so in one line and trace with grep, glob, and reads. The output contract does not change.

## Step 3 — Fan out to 3-4 subagents, one lane each

Recon is wide, shallow, and parallel — the ideal subagent shape. Launch the lanes **in a single message so they run concurrently**, each read-only, each returning the fixed schema in Step 4. Use the `Explore` agent type where available, `general-purpose` otherwise.

| Lane | Question it answers | Must return |
| --- | --- | --- |
| **A. Entry & call paths** | How does control reach this code? | Every caller and entry point — routes, CLI commands, cron, hooks, event handlers, tests — with `file:line`, and the depth at which each was traced |
| **B. State & data** | What reads and writes the state involved? | Every read site and every *write* site, plus schema, migrations, caches, serialized formats, and the single write path (or the fact that there is more than one) |
| **C. Contracts & boundaries** | What crosses a line if this changes? | Public APIs, exported symbols with external consumers, events/queues, config keys, env vars, feature flags, cross-service calls, and anything a third party depends on |
| **D. Failure & operations** | How does this fail today, and who notices? | Error paths, retries, timeouts, existing tests that cover the subject, logs/metrics/traces, and the deploy or rollback path |

Lane D can be folded into the main context on a small trace; A, B, and C are never skipped. Cap each lane: **read-only, no edits, 8 minutes of exploration, report what you found and what you ran out of time on.** A lane that finds nothing says so — an empty lane is a finding, not a failure.

Give every lane the same instruction about honesty: *report `file:line` for everything claimed; anything inferred, unverified, or graph-only is listed separately as an unknown, never smoothed into the findings.*

If the Agent tool is unavailable, run the four lanes sequentially in the main context, in the order A, B, C, D, and say in the chat verdict that the trace was serial and shallower.

## Step 4 — Each lane returns this, verbatim

```
LANE: <A|B|C|D>
EDGES:
  - <file:line> — <what it is> — <why it matters to the change> — [confirmed | graph-only]
STATE TOUCHED: <tables/files/keys, with read or write marked>
CONTRACTS CROSSED: <name — consumer — breaking-if>
UNKNOWNS: <what could not be verified, and the one command or file that would settle it>
RAN OUT OF TIME ON: <anything the cap cut off>
```

## Step 5 — Reconcile into the Recon Map

Merge the lanes yourself; do not paste them. Dedupe by `file:line`, resolve contradictions between lanes by reading the file, and write the map to a file — default `recon-<subject-slug>.md` beside where the plan will live. Long output belongs in the file, never in chat.

```markdown
# Recon Map — <subject>
Traced: <YYYY-MM-DD, UTC> · Commit: <sha> · Mode: <graph+read | grep-only> · Lanes: <A,B,C,D>

## Subject and change class
<one line each>

## The seams — where a change here escapes this file
| Seam | Location | Crosses | Breaks if |
| --- | --- | --- | --- |

## Call paths in
<entry point -> ... -> subject, one line per path, with file:line>

## State
<read sites / write sites; the single write path, or the fact that there is not one>

## Contracts
<name — consumer — breaking-if — where it is declared>

## Failure and rollback today
<error paths, retries, tests that cover this, signals that fire, how a bad deploy is undone>

## Unknowns — what I could not verify
| Unknown | Why it matters | What would settle it |
| --- | --- | --- |

## Blast radius, one line
<the systems, data, and people that break if this goes wrong — named, not "various downstream">
```

The Unknowns table is the load-bearing section. A map with no unknowns is either a trivial subject or a dishonest trace; say which.

## Step 6 — Hand off, do not plan

Recon stops at the map. In chat, give only:

- The verdict line: `Recon complete — N seams, M unknowns, blast radius: <one line>.`
- The map's file path.
- The one or two unknowns that would change the plan if they resolve the other way.
- The next step: write the plan against the map, via [swe](../swe/SKILL.md).

Then stop and let the plan be asked for. If the user asked for a plan in the same breath, proceed to it immediately — but the plan's steps now cite the map, and its blast radius section is copied from the map rather than invented.

## Escalation

- **State or authority is moving** -> [spike-360](../spike-360/SKILL.md) first; recon does not decide whether a source of truth should exist.
- **Refactor is approved and needs a real seam map with contract owners and rollout invariants** -> the `phase-0-spike` workflow (`~/.claude/workflows/phase-0-spike.js`), which goes deeper than recon on a committed refactor. Recon is the cheap universal pass; phase-0-spike is the expensive committed one.
- **The map shows a one-way door** -> [blast-radius](../../01-decide/blast-radius/SKILL.md) prices it before anyone plans around it.

## How this differs from its neighbors

- **recon** — "What is actually there?" Read-only reconnaissance of the *current* system, before a plan exists.
- **swe** — "Does the plan embody our engineering standards?" Grades a document. Recon supplies the ground truth that document's Blast and Proof pillars depend on.
- **spike-360** — "Should this authority exist?" Interrogates the premise; runs upstream of recon when state is moving.
- **phase-qa** — appends checks to a plan that already exists.
- **debug-mantra** — traces a fail path for a bug that is happening now. Recon traces edges for a change that has not happened yet.

## What success looks like

The plan's blast radius section is copied out of the map, not composed. Someone who did not do the trace can click every claim. And the one thing nobody knew — the second write path, the caller in a cron job, the consumer in another repo — is on the page before the first line of code is written, or is named as an unknown with the command that would find it.
