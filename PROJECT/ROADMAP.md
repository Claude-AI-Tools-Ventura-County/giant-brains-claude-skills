<!-- PDDA ROADMAP CONTRACT — this file is a POINTER/LEDGER, not a plan body.
     Allowed: queued intake / projects in progress / completed / attempted / deferred + links to PROJECT/** docs.
     NOT allowed: phase checklists, build steps, deep execution notes — put those in the project doc.
     Carve-out: a SHORT exception note is OK only when omitting it would hide an operationally critical fact.
     Coverage rule: every PROJECT/2-WORKING doc must be reflected here by a pointer (or opt out with roadmap_exempt: true).
     Enforced by `pdda.sh roadmap` + `pdda.sh roadmap-coverage` (deterministic) + utils/pdda/pdda-doc-ready.sh ROADMAP rubric (LLM).

     This is a PDDA/marathon-only artifact, deliberately separate from this repo's own root ROADMAP.md
     (a lightweight Backlog/Queued/Active GH-issue tracker with a different format marathon-plan.sh can't
     parse). This file is gitignored — see .gitignore's "PDDA + xyz marathon infra" section — so it never
     reaches GitHub; the root ROADMAP.md stays the only roadmap the public repo shows. Point marathon-plan.sh
     at this file via QUEUE_PLAN_ROADMAP=PROJECT/ROADMAP.md when running it in this repo. -->

# Roadmap (PDDA/marathon-internal)

> **Pointer/ledger only — not a plan body.** Execution detail (phase checklists, build steps, QA
> gates, deep notes) lives in the linked `PROJECT/**` docs; keep it there. See the contract banner above.

## Status

| What was just completed | What's next |
|---|---|
| Parked GH-7 (front-door) and GH-8 (shakedown) as queued intake (2026-07-22). | Run swarm-preflight + marathon-plan to build a marathon covering both. |

## Ledger

### Queue / parked intake

- **GH-7 — front-door: FRONTDOOR.md has no staleness/re-audit trigger or maturity-stage field**
  (2026-07-22) - `FRONTDOOR.md` has no field recording when a refresh is due, and no field recording
  the repo's maturity stage at audit time (alpha/beta/RC/stable), so a dashboard can silently go stale
  after a merge that changes onboarding-relevant surface. Issue
  [#7](https://github.com/Claude-AI-Tools-Ventura-County/giant-brains-claude-skills/issues/7). ->
  [PROJECT/1-INBOX/GH-7-FRONTDOOR-STALENESS-MATURITY-STAGE.md](PROJECT/1-INBOX/GH-7-FRONTDOOR-STALENESS-MATURITY-STAGE.md)
- **GH-8 — shakedown: no re-run trigger when the audited skill's own script layout changes**
  (2026-07-22) - companion to GH-7 but scoped separately: shakedown's right trigger is the skill's own
  file layout changing (script renamed, install location moved, vendored copy drift), not the
  product's maturity stage. Issue
  [#8](https://github.com/Claude-AI-Tools-Ventura-County/giant-brains-claude-skills/issues/8). ->
  [PROJECT/1-INBOX/GH-8-SHAKEDOWN-RERUN-TRIGGER-ON-LAYOUT-CHANGE.md](PROJECT/1-INBOX/GH-8-SHAKEDOWN-RERUN-TRIGGER-ON-LAYOUT-CHANGE.md)

### In progress

- No active `PROJECT/2-WORKING` docs.

### Completed

- No completed docs.

### Deferred

- No deferred docs.

---

*Add new work here only when a real `PROJECT/**` doc exists to own the execution detail.*
