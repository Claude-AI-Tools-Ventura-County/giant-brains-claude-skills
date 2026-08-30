---
name: github-auth-debug
description: MOVED to giant-brains-swe-skills (04-toolbox/github-auth-debug) — invoke it from there. Original triggers follow. Diagnose and fix the "git push works but `gh` fails" auth split on macOS — where the GitHub CLI and git consult different credential stores and drift apart — non-destructively, without over-engineering. Trigger when the user says "git push works but gh fails", "gh auth is broken", "token in keyring is invalid", "gh auth status fails", "fix/unify gh and git auth", "re-auth GitHub CLI", "gh 403 SSO/SAML", or when a `gh` command fails mid-session with an auth/keyring/TLS error while `git` still works. Leads with two guardrails: (1) inside a sandboxed shell `gh` gives a FALSE "invalid token" — re-check unsandboxed before concluding anything; (2) one failure does not justify re-architecting credentials — `gh auth setup-git` is the recommended minimal fix, escalate to GCM/SSH/PAT only after a second reproducible failure. Do NOT use for first-time GitHub setup with no prior auth (that's just `gh auth login`), for SSH-key generation requests, or for non-GitHub credential issues.
---

# github-auth-debug — moved

This skill now lives in [giant-brains-swe-skills](https://github.com/Claude-AI-Tools-Ventura-County/giant-brains-swe-skills/tree/main/04-toolbox/github-auth-debug). Install it from there and invoke that copy; this stub exists for one release so existing symlinks keep resolving, and will be removed in the release after v1.1.0.

```bash
git clone https://github.com/Claude-AI-Tools-Ventura-County/giant-brains-swe-skills.git && cd giant-brains-swe-skills && ln -s "$PWD/04-toolbox/github-auth-debug" ~/.claude/skills/github-auth-debug
```
