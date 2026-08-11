---
title: front-door — FRONTDOOR.md has no staleness/re-audit trigger, and doesn't record repo maturity stage
status: Proposed (1-INBOX — not yet active)
created: 2026-07-22
owner: noel
gh_issue: 7
source: https://github.com/Claude-AI-Tools-Ventura-County/giant-brains-claude-skills/issues/7
doc_type: project
related: GH-8-SHAKEDOWN-RERUN-TRIGGER-ON-LAYOUT-CHANGE.md
effort: 3
complexity: 2
risk: 1
phases: 1
---

## Ask

`FRONTDOOR.md`'s own charter line says "Refresh this board whenever an onboarding-facing doc ... or
the repo structure changes" — but that's an instruction for a human/agent to *remember*, not something
the artifact itself tracks. Two gaps:

1. No field recording **when a refresh is actually due** — the dashboard can silently go stale.
2. No field recording **what maturity stage the audited repo was at** when last audited
   (alpha/beta/RC/stable) — the bar for "first success" and what counts as a blocking hoop legitimately
   differs by stage, so a verdict from an early-stage pass reads as more final than it is.

## Real case that surfaced this

In `hyper-pandas-python-stack`, `FRONTDOOR.md` was generated early in a build, when the repo only had a
Phase 0 database-compatibility spike (no app code, no auth, no way to actually run the product yet). Its
checks and verdict ("✅ Smooth") only ever covered that database-bootstrap layer. The project's own plan
doc had to hand-write an explicit reminder ("ALPHA GATE — re-edit README.md + run onboarding audits
here, not before... run `/front-door` ... to verify the fresh-clone → running-state path holds up for a
cold newcomer") — correct, but bespoke. Every repo using this skill has to independently invent the same
reminder by hand, or the dashboard silently goes stale. In this case it did: a full application layer
(Reflex app, auth, admin bootstrap) merged to `main` while `FRONTDOOR.md` kept reporting "Smooth" based
on checks that never touched any of it.

## Acceptance criteria

- `FRONTDOOR.md`'s generated header records a **maturity stage** at time of audit (alpha/beta/RC/stable,
  or equivalent) — not just the pass/fail verdict, so a reader can see the bar the verdict was measured
  against.
- `FRONTDOOR.md` records (or the `/front-door` skill checks for) a **staleness signal**: something a cold
  agent or human can cheaply evaluate to answer "has anything onboarding-relevant changed since this
  board was last generated" — e.g. a tracked-file mtime/hash snapshot of the onboarding-facing surface
  (README, install scripts, entry points) at audit time, comparable against current state.
- The skill's own charter line ("refresh whenever X changes") becomes something the artifact can
  self-report against, not just a comment a human has to remember.

## Explicitly out of scope

- **Not** a generic "codebase health score" — scope stays to onboarding/first-success auditing.
- Does not prescribe *when* a maturity-stage transition happens (alpha→beta, etc.) — that's the
  project's own call; `FRONTDOOR.md` just records what stage was declared at audit time.

## Companion issue

Filed together with [#8](https://github.com/Claude-AI-Tools-Ventura-County/giant-brains-claude-skills/issues/8)
(same operator prompt, same underlying "reports go stale silently" problem) — but scoped separately:
`shakedown`'s right re-run trigger is the *skill's own file layout changing*, not the *product's maturity
stage*. Don't generalize this issue's maturity-stage field onto shakedown; see GH-8's doc for why.

## Swarm Preflight Contract
```json
{
  "target": { "repo": ".", "ref": "main" },
  "gate": "true",
  "fix_probes": [
    { "type": "grep_absent", "path": "repo-health/frontdoor/SKILL.md", "pattern": "maturity_stage" },
    { "type": "grep_absent", "path": "repo-health/frontdoor/SKILL.md", "pattern": "staleness" }
  ],
  "artifacts": [ "repo-health/frontdoor/SKILL.md", "repo-health/frontdoor/FRONTDOOR.md" ],
  "remediation": {
    "source": "issue#7",
    "criteria": "FRONTDOOR.md's generated header records a maturity stage (alpha/beta/RC/stable) at time of audit, and a staleness signal (an mtime/hash snapshot of the onboarding-facing surface) a later session can cheaply compare against current state. SKILL.md documents both fields so /front-door reliably produces them on every run. No automated test suite exists in this repo (skills-only, no CI) -- verify by generating a fresh FRONTDOOR.md via /front-door and confirming both fields are present and populated."
  },
  "lanes": {
    "agy_safe": [ "repo-health/frontdoor/SKILL.md", "repo-health/frontdoor/FRONTDOOR.md" ],
    "orchestrator_only": []
  }
}
```

Full discussion: [#7](https://github.com/Claude-AI-Tools-Ventura-County/giant-brains-claude-skills/issues/7)
