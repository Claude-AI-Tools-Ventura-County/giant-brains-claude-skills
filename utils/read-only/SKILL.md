---
name: read-only
description: MOVED to giant-brains-swe-skills (04-toolbox/read-only) — invoke it from there. Original triggers follow. Add a curated set of read-only permission rules -- file reads, directory listings, content search (grep/glob), git inspection, and system checks -- to a Claude Code settings.json allowlist so safe reads stop triggering permission prompts. Local read-only by default; outbound reads (WebFetch, WebSearch, registry lookups) and secret-bearing reads (env dumps) are offered only as explicit opt-ins. Trigger when the user says "read-only", "/read-only", "pre-approve read operations", "allow all read-only commands", "stop asking me about ls/cat/grep", or asks to add safe read permissions to a settings file. Do not use for write or install permissions, or for mining transcripts to find which commands actually prompt most -- route those to a dedicated settings or transcript-analysis skill (e.g. update-config, fewer-permission-prompts) when one is installed.
---

# read-only — moved

This skill now lives in [giant-brains-swe-skills](https://github.com/Claude-AI-Tools-Ventura-County/giant-brains-swe-skills/tree/main/04-toolbox/read-only). Install it from there and invoke that copy; this stub exists for one release so existing symlinks keep resolving, and will be removed in the release after v1.1.0.

```bash
git clone https://github.com/Claude-AI-Tools-Ventura-County/giant-brains-swe-skills.git && cd giant-brains-swe-skills && ln -s "$PWD/04-toolbox/read-only" ~/.claude/skills/read-only
```
