# Changelog — `biggie-small.md`

Every change to the Biggie-Small output style, with the observed behavior that
prompted it and the mechanism that was supposed to fix it. The point of this file
is recalibration: when a rule stops working, or starts over-firing, you should be
able to read why it exists before you delete it.

Format for each entry:

- **Observed** — the actual bad (or missing) behavior in the wild.
- **Diagnosis** — why the style as written produced it.
- **Change** — what text moved, and where.
- **Watch for** — the over-correction this could cause, so a future regression is recognizable.

---

## 2026-09-01 — Budget applies to prose, not to next steps

**Observed.** A completion reply opened correctly ("Gate is running — standing by
for it before committing"), then spent the entire budget on three paragraphs of
findings narrative: which two recommendations were dropped and why, a normalizer
rewrite, a profile-validation suite, a miscounted "8 gateways" figure, and a
self-demonstrating checkbox bug. The numbered steps that followed had been
squeezed to two stubs — "Gate result, then commit + push + PR" — with the gating
condition ("do not commit while the gate is running") stated only up in the prose.
Read top-down under time pressure, the steps were actionable but wrong.

**Diagnosis.** Two rules were fighting, and the wrong one won.

1. `## Hard budget` counted a numbered step as a line. The steps were therefore
   the cheapest thing to cut, and they sat last, so they were cut last-in and
   hardest. The model satisfied the letter of the budget by compressing the
   payload rather than the story.
2. "Cut the lowest-value lines" was undirected. Nothing said narrative goes first.
   Findings feel high-value to the writer at the moment of writing, so they
   survived; the steps, being terse already, looked compressible.

The result is a specific failure mode worth naming: **budget gaming** — the reply
stays long where the model wants to be long and gets short exactly where the user
needs detail. The compression is backwards.

**Change.** Three edits, all aimed at making the budget bite where the gaming
happens rather than at the end of the reply.

1. `## Hard budget`, bullet 1 — removed "A numbered step counts as a line."
2. `## Hard budget`, new bullet 2 — the budget governs the prose above the steps;
   the numbered list is exempt, like the thread anchor.
3. `## Hard budget`, "Before sending, count" bullet — cut order is now explicit
   and ranked: narrative first (what was done → what was found → what was
   considered). Actions are never cut, and neither is the condition gating one.
4. `## Next steps are the payload` — three new paragraphs: the exemption and why
   it exists; a requirement that **every step carries its gating condition inline**
   ("a step whose precondition lives only in a sentence further up is not a step;
   it is a trap"), with the gate example written out both ways; and a note that
   "short" means no wasted words, not dropped conditions — two lines for a gated
   step beats one line the user can misfire on.
5. `## Shape of a normal response`, item 4 — annotated as budget-exempt and
   carrying per-step gating conditions, so the shape list agrees with the rules.

**Rejected alternative.** Moving the next-steps list to the *top* of the reply was
considered and turned down. It collides with the standing "Line 1 answers the
user's previous message" rule, and it misdiagnoses the sample: the ordering was
fine, the middle was the problem. Revisit only if steps keep arriving thin *after*
this change — that would mean the exemption isn't the binding constraint.

**Watch for.** The exemption is a licence to pad. If replies start carrying
six-step lists where two steps and a sentence would do, the fix is not to
re-impose the budget on steps — it is to tighten "Steps the user must take,"
i.e. steps the *user* takes, not a log of what the model plans to do. Also watch
for gating conditions bloating into rationale; the condition is *when not to run
the step*, not *why the step exists*.

---

## 2026-08-24 — `Other Next Steps from PRS` block (commit `c4acfa5`)

**Observed.** Replies closed cleanly on the current task but left the operator
with no line of sight to the rest of the release plan; the next unshipped
release's open manifest and the roadmap queue went unread for whole sessions.

**Change.** Added the `## Other Next Steps from PRS (occasional)` section: on
roughly one substantive task-completion reply in four, in a repo carrying a
`releases.db` plus `ROADMAP.md`, append exactly three short items (issue number
plus a few words) drawn from the next unshipped release's open manifest and the
roadmap's active/queued entries — items not already part of the current task.
Read via whatever copy of the PRS CLI the repo ships (`utils/py/releases_app.py`
canonical, `.xyz/utils/py/releases_app.py` vendored), falling back to reading the
files directly. Exempt from the line budget. Skipped when the repo has no
`releases.db`, when the reply contains a blocker, or when it fired in the
previous reply.

**Watch for.** It is a nudge, not a fixture. If it appears on consecutive replies
or on simple Q&A turns, the frequency guard is being ignored and should be
restated rather than the section deleted.

---

## 2026-08-21 — Blocker exception, emergency hatch, and park-what-you-drop (commits `89db548`, `4704004`)

**Observed.** The original "One pass, not a drip" rule was too absolute: once the
sweep closed, genuinely unshippable findings had nowhere to go, and dropped items
vanished instead of being filed.

**Change.** Three additions.

1. `### The blocker exception` — a newly discovered fact that makes delivered work
   wrong, unsafe, or unshippable may interrupt a closed sweep. **Consequence
   decides, not category**: wrong result, data loss, security hole, cannot
   ship/build/deploy, or acting later costs materially more. Blockers arrive
   together, worst first, never drip-fed. The line budget governs presentation,
   not qualification — a blocker that will not compress still leads with
   `Blocker:` above the numbered steps.
2. `## Emergency escape hatch` — `[EMERGENCY]` prefix suspends every rule for
   active incidents only, with a hard test: the second sentence must justify the
   tag in one line, or the tag does not apply.
3. `## Park what you drop` — dropped items are filed to a `PARKED/` folder at the
   repo root, appearing in chat only as a count, never itemized.

**Watch for.** The blocker exception is the most abusable rule in the file. If
"important-sounding" findings start getting promoted to blockers, re-read the
consequence test — improvements, taste, hypotheticals and "while I was in there"
are explicitly excluded.

---

## 2026-08-21 — Initial version (commit `c32f1df`)

**Observed.** Default replies read as narration: what was inspected, what was run,
what was traced, what was considered. The operator was mid-task and short on time
and had to mine the reply for the next move.

**Change.** Created the style. Core mechanisms, in the order they do the work:

- **Hard budget** — 8 lines default, line 1 answers the previous ask, no headers
  or tables or emoji or bold labels. "Vague compliance is not compliance."
- **The one rule** — every line must help the user decide or act.
- **Answer the ask, then summarize at altitude** — 2–3 manager-level sentences
  maximum; file and line references always allowed, narration around them banned;
  banned openers ("Traced," "Investigated," "Confirmed that," …).
- **Long reports go to files** — findings, audits, adjudications and verification
  detail leave the chat window; chat gets verdict + path + next steps. Applies
  hardest when relaying another agent's output.
- **Recommend, do not survey** — one recommendation and the one reason driving it.
- **One pass, not a drip** — hold findings, sweep once, sort blocking / optional /
  dropped.
- **Stay in the current phase** — "interesting" is not "relevant."
- **Circle back** — anchor to the previous ask and to the original session goal.
- **Thread anchor** — two lines, only on drift or on request.
- **Next steps are the payload** — one numbered list, execution order, last.
- **When to break the budget** — security/destructive warnings, multi-step
  instructions where compression misleads, direct "how does X work" questions,
  and content that leaves the chat (code, commits, docs, issue and PR bodies).
- **Full detail on request** — verbose is the deliverable when asked for; covers
  that turn only.
