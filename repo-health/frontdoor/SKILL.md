---
name: front-door
description: >
  MOVED to giant-brains-swe-skills (03-audit/frontdoor) — invoke it from there. Original triggers follow.
  Walk a repo's front door as a brand-new user would and report whether they can
  actually get from clone to working — not just whether the docs exist. Use whenever
  the user asks to audit, review, or critique a repo's onboarding, installation,
  setup, getting-started, or quickstart experience; asks "can a new user install
  this," "is the setup too hard," "why is onboarding so painful," "are there too
  many READMEs," "which doc is the source of truth," "did we leak an API key,"
  or wants install scripts and auth/login/credential
  paths checked for friction. Also fire automatically before you reassure someone
  that their setup is "easy" or sign off on a README — verify the path first.
  Covers competing/duplicate onboarding docs, install-script red flags, auth and
  access gates, prerequisites, first-run success, doc-vs-code drift, and
  accidentally committed secrets (API keys, tokens, private keys) in the tree or
  git history — honestly separating friction an AI agent can absorb from friction
  that needs a human. Can also save the audit as a persistent FRONTDOOR.md
  dashboard — a re-runnable health board whose every finding carries a
  deterministic check — and refresh that board on later runs.
---

# frontdoor — moved

This skill now lives in [giant-brains-swe-skills](https://github.com/Claude-AI-Tools-Ventura-County/giant-brains-swe-skills/tree/main/03-audit/frontdoor). Install it from there and invoke that copy; this stub exists for one release so existing symlinks keep resolving, and will be removed in the release after v1.1.0.

```bash
git clone https://github.com/Claude-AI-Tools-Ventura-County/giant-brains-swe-skills.git && cd giant-brains-swe-skills && ln -s "$PWD/03-audit/frontdoor" ~/.claude/skills/frontdoor
```
