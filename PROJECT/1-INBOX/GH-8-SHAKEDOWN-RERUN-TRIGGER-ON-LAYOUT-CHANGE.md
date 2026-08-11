---
title: shakedown — no re-run trigger when the audited skill's own script layout changes
status: Proposed (1-INBOX — not yet active)
created: 2026-07-22
owner: noel
gh_issue: 8
source: https://github.com/Claude-AI-Tools-Ventura-County/giant-brains-claude-skills/issues/8
doc_type: project
related: GH-7-FRONTDOOR-STALENESS-MATURITY-STAGE.md
effort: 3
complexity: 3
risk: 1
phases: 1
---

## Ask

A `shakedown` report is a point-in-time read of a target skill's path-resolution behavior (static audit
+ live harness matrix). Nothing about it records *when a re-run is actually warranted* — so a report can
silently go stale the same way a `FRONTDOOR.md` dashboard can (see companion issue
[#7](https://github.com/Claude-AI-Tools-Ventura-County/giant-brains-claude-skills/issues/7)). The two
skills were flagged together by the same operator prompt, but the right trigger for each is different,
not the same thing:

- `front-door` cares about the **product's maturity stage** — an alpha's onboarding bar differs from a
  1.0's.
- `shakedown` doesn't care about the product's stage at all. A CWD-relative path bug in a bundled script
  is exactly as broken pre-alpha as post-1.0. What actually invalidates a shakedown report is the
  **skill's own file layout changing** — a script renamed, an install location moved, a vendored copy
  drifting from its source (this repo's own `relay-xyz` skill has exactly this failure mode documented:
  `find-harness.sh --check` explicitly warns when a vendored `.xyz/` copy is behind the live harness).

So this is deliberately **not** "generalize GH-7's maturity-stage field onto shakedown too" — that would
be a mismatched fit. The right question for shakedown is closer to "has anything under the target
skill's own directory (or its vendored copies) changed since the last report?"

## Proposed improvement

1. When writing a dated report to `SHAKEDOWN/<date>/<target>-<time>.md`, record the **git blob hash or
   mtime** of the target skill's `SKILL.md` and each bundled script, so a later session can cheaply check
   "has anything actually changed since this report" before deciding whether to trust it or re-run.
2. In `SHAKEDOWN/INDEX.md`, add a one-line **staleness check** convention next to each entry — e.g. a
   `git diff --stat <report-commit> -- <skill-dir>` an agent can run to see at a glance whether the
   audited files have moved since the last shakedown pass.
3. If the target skill has vendored copies (the `relay-xyz`/`.xyz` pattern this repo already handles
   elsewhere), explicitly note in the report when a vendored copy is checked vs. the canonical source,
   since drift between them is itself a class of the exact bug shakedown exists to catch.

## Acceptance criteria

- A shakedown report captures enough (hash/mtime per audited file) that a later session can answer
  "is this report still trustworthy" without re-running the full audit.
- `SHAKEDOWN/INDEX.md` gains a documented, repeatable staleness-check convention per entry.
- Vendored-copy-vs-canonical-source drift is explicitly surfaced when the target skill has one.

## Explicitly out of scope

- No "codebase stage" question, no `ROADMAP.md` entry — deliberately narrower than the front-door ask
  (GH-7), because neither fits what this skill actually audits.

## Companion issue

Filed together with [#7](https://github.com/Claude-AI-Tools-Ventura-County/giant-brains-claude-skills/issues/7)
(same operator prompt, same underlying "reports go stale silently" problem) — scoped separately per the
reasoning above.

## Swarm Preflight Contract
```json
{
  "target": { "repo": ".", "ref": "main" },
  "gate": "bash -n utils/shakedown/scripts/audit.sh && bash -n utils/shakedown/scripts/harness.sh && bash -n utils/shakedown/scripts/lib.sh",
  "fix_probes": [
    { "type": "grep_absent", "path": "utils/shakedown/scripts/audit.sh", "pattern": "blob" },
    { "type": "grep_absent", "path": "utils/shakedown/SKILL.md", "pattern": "staleness" }
  ],
  "artifacts": [ "utils/shakedown/SKILL.md", "utils/shakedown/scripts/audit.sh", "utils/shakedown/scripts/harness.sh", "SHAKEDOWN/INDEX.md" ],
  "remediation": {
    "source": "issue#8",
    "criteria": "A shakedown report records a git blob hash or mtime per audited file (SKILL.md + each bundled script) so a later session can cheaply check whether a report is still trustworthy. SHAKEDOWN/INDEX.md documents a repeatable staleness-check convention per entry. When the target skill has a vendored copy, the report explicitly notes vendored-vs-canonical drift. Gate is a syntax check only (bash -n) -- no broader automated suite exists in this repo; verify the new fields by running /shakedown against a real target and inspecting the written report."
  },
  "lanes": {
    "agy_safe": [ "utils/shakedown/SKILL.md", "SHAKEDOWN/INDEX.md" ],
    "orchestrator_only": [ "utils/shakedown/scripts/audit.sh", "utils/shakedown/scripts/harness.sh" ]
  }
}
```

Full discussion: [#8](https://github.com/Claude-AI-Tools-Ventura-County/giant-brains-claude-skills/issues/8)
