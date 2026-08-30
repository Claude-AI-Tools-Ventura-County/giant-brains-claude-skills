---
name: install-improve-audit
description: MOVED to giant-brains-swe-skills (04-toolbox/install-improve-audit) — invoke it from there. Original triggers follow. Get an unfamiliar repo installing and building locally, fix only what blocks it, and open a PR carrying the fixes plus an append-only change log. The deliverable is a working build and a PR — never a findings report. Trigger when the user says "install this repo", "get this building", "clone and set this up", "make this run locally", "why won't this build", "docker compose build fails", "/install-improve-audit", or hands over a repo path or URL and asks for it working. Container-native repos are first-class: the container build is a real install path, not a disqualification, and a repo that builds in its own image reaches INSTALLED. Improvements are a bounded bonus tier that opens only after the build passes, is capped at 3 items, and is always droppable. Do NOT use for repo analysis, architecture review, code-quality assessment, deliberate security scanning, or dependency-hygiene audits — this skill refuses those and names the right tool instead.
---

# install-improve-audit — moved

This skill now lives in [giant-brains-swe-skills](https://github.com/Claude-AI-Tools-Ventura-County/giant-brains-swe-skills/tree/main/04-toolbox/install-improve-audit). Install it from there and invoke that copy; this stub exists for one release so existing symlinks keep resolving, and will be removed in the release after v1.1.0.

```bash
git clone https://github.com/Claude-AI-Tools-Ventura-County/giant-brains-swe-skills.git && cd giant-brains-swe-skills && ln -s "$PWD/04-toolbox/install-improve-audit" ~/.claude/skills/install-improve-audit
```
