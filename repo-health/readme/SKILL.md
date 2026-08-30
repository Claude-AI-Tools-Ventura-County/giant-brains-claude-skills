---
name: readme-audit
description: >
  MOVED to giant-brains-swe-skills (03-audit/readme) — invoke it from there. Original triggers follow.
  Audit a repo's root README as both the artifact under review and the map to
  everything else — checking accuracy, legibility, understandability, and operator
  UX, then following every pointer it makes to other docs as a litmus test for the
  whole repo's doc hygiene. Use when the user asks to "review/audit/check the
  README," "is the README accurate," "does the README still match the code," "find
  gaps in the README," "are our docs drifting," "do the README's links still work,"
  "is the README clear enough," or wants the README graded for an operator
  who has to actually use the repo. Fires before you sign off on a README as "good"
  or "up to date" — verify the document content and traverse the links first. Covers stale
  commands/flags/paths/counts, dead relative links and missing anchors, README ↔
  linked-doc contradictions, orphaned and unreachable docs, missing-but-needed
  sections, and overall scannability — then offers to apply the low-risk, mechanical
  fixes (dead links, stale counts, wrong commands) on confirmation. NOT the
  clone→working onboarding walk, secret-scanning, or install-script audit — that is
  front-door; this skill cross-references it instead of repeating it.
---

# readme — moved

This skill now lives in [giant-brains-swe-skills](https://github.com/Claude-AI-Tools-Ventura-County/giant-brains-swe-skills/tree/main/03-audit/readme). Install it from there and invoke that copy; this stub exists for one release so existing symlinks keep resolving, and will be removed in the release after v1.1.0.

```bash
git clone https://github.com/Claude-AI-Tools-Ventura-County/giant-brains-swe-skills.git && cd giant-brains-swe-skills && ln -s "$PWD/03-audit/readme" ~/.claude/skills/readme
```
