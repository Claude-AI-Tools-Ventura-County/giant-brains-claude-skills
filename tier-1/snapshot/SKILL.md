---
name: snapshot
description: Save the most recent substantive response — plus session metadata, recent test findings, and phase status — to a persistent, additive snapshot.md file so the user can re-find and resume the session later (next morning, after a crash, or across chat tabs). Trigger whenever the user says "snapshot", "snapshot this", "save this session", "save our progress", "save before I go to bed / sign off / wrap up", "checkpoint this", or expresses worry about losing work, losing the chat, or VS Code crashing. Also offer it proactively when a long working session reaches a natural stopping point with unsaved findings. Use only to preserve session progress — not when the user wants to save or export a specific artifact (a file, PDF, image, code snippet, or document).
---

# Snapshot

Save a re-entry point for the current session. A snapshot has one job: make tomorrow-morning-you (or post-crash-you) able to find this work and resume it in under a minute, without hunting through chat tabs or recovery files.

A good snapshot therefore captures two things:
1. **The answer** — the most recent substantive response, verbatim.
2. **The context** — enough metadata that the snapshot is self-locating and self-resuming.

## File location and behavior

- File name: `snapshot.md`
- **Location** — write to the first of these that applies, so the snapshot lands where the user will look for it:
  1. **Git repository root** (`git rev-parse --show-toplevel`) — keeps the snapshot beside the code it describes.
  2. **Editor/workspace root**, if one is open and you're not in a repo.
  3. **Current working directory**, if writable and not `/` or a system temp dir.
  4. **Claude.ai with no project filesystem** → `/mnt/user-data/outputs/snapshot.md`, then present the file for download.
- **Keep it out of version control.** If you write `snapshot.md` into a git repo and it isn't already ignored, mention once that it's a personal recovery artifact (it can contain anything pasted into the chat) and offer to add it to `.gitignore`. Don't redact or trim the contents to make it commit-safe — keep it out of commits instead.
- **If the write fails** (read-only directory, unclear or unwritable cwd), fall back to the next location in the list above — ultimately the user-output dir — and state the *actual* path saved in the confirmation. Never report a project-root save that didn't happen: for crash recovery, a confidently-wrong path is worse than admitting the fallback.
- **Additive, newest-first.** Never overwrite. Prepend each new snapshot entry to the TOP of the file, above all previous entries. The morning use case means the most recent entry must be the first thing visible when the file opens.
- If `snapshot.md` doesn't exist yet, create it. If it exists, read it first, then prepend.

## Entry format

Every entry starts with a timestamp header and a metadata block, then the verbatim response, then a separator. Use the user's local time (check `user_time_v0` or system time — never guess).

```markdown
# 📸 Snapshot — 2026-06-09 22:47 (Tue)

**Session:** <short, searchable label for this chat/work session — e.g., "SKILL file refinement — snapshot skill build">
**Project / repo:** <project name or path, if known>
**Phase:** <current phase or milestone, if the work has phases — e.g., "Phase 2: eval iteration">
**Status:** <one line: where things stand right now>

## Git state
<Captured at snapshot time, if the working directory is a git repo. Run the commands in
 "Capturing git state" below and record:>
- **Branch:** <current branch>
- **HEAD:** <short hash — first line of commit message>
- **Working tree:** <clean | N modified, N staged, N untracked>
- **Changed files:** <output of `git status --short`, fenced as a code block; omit if clean>
- **Ahead/behind remote:** <e.g., "ahead 2" — omit if in sync or no upstream>
<If not a git repo, write "Not a git repository." and move on.>

## Recent findings
<Bullet list of test results, eval outcomes, decisions made, or discoveries from this session
 since the last snapshot. Pull these from the conversation — failed tests, passed tests,
 key tradeoffs decided, bugs found. If none: "No new test/phase findings since last snapshot.">

## Next steps
<1–3 bullets: what the immediate next action is when work resumes. This is what makes
 the snapshot resumable, not just archival.>

## Last response (verbatim)
<The full text of the most recent substantive assistant response, unedited.>

---
```

## What counts as "the most recent response"

The last substantive assistant answer before the snapshot request — not the snapshot confirmation itself, and not a trivial reply like "Sounds good." If the last few turns were short back-and-forth, use judgment and capture the last response with real content. If genuinely ambiguous (e.g., two large responses on different topics), ask which one — but default to the most recent rather than blocking.

## If the exact response is unavailable

If the verbatim most-recent response can't be recovered because the context was summarized, compacted, or truncated, save the closest available assistant response and label that section **`## Last response (best available — not guaranteed verbatim)`**. Do not silently reconstruct wording from memory and present it as exact. The skill's whole value is fidelity; a snapshot that *pretends* to be verbatim when it isn't is worse than one that names the gap honestly.

## Gathering the metadata

- **Findings**: scan the conversation since the previous snapshot (or session start) for test results, eval scores, phase completions, and decisions. When `snapshot.md` already exists, use the most recent entry's timestamp/header as the "since last snapshot" boundary so you don't repeat stale findings; otherwise summarize from the visible conversation. Compress to bullets — findings are metadata, not a transcript.
- **Session label**: write it for searchability. Derive it from the session's first real request or the current file/topic being worked — not from the snapshot act itself. The user will be scanning a file or a chat list at 7am; "Snapshot 14" or "Chat session" is useless, "fintech onboarding PRD — risk section rewrite" is findable.
- **Next steps**: if the conversation didn't state them explicitly, infer the obvious next action and mark it as inferred (e.g., "Next (inferred): run eval set against v2").

## Capturing git state

If a filesystem and shell are available, check whether the working directory is a git repo and capture state non-destructively (read-only commands only — never stage, commit, or stash as part of a snapshot):

```bash
git rev-parse --is-inside-work-tree   # gate: if this fails or prints false → "Not a git repository.", skip the rest
git branch --show-current             # current branch (empty on detached HEAD)
git log -1 --format='%h %s'           # HEAD: short hash + subject
git status --short                    # changed files (empty output = clean tree)
git status -sb | head -1              # ahead/behind upstream
```

Run each as its own read-only command rather than one `&&` chain — a single empty or non-zero step (clean tree, detached HEAD, a repo with no commits yet) shouldn't abort the rest. The block is bash; if only a different shell or a git API is available, capture at least **branch** and **HEAD** by whatever means you have. Never fail or skip the whole snapshot because git state couldn't be read — degrade gracefully: write "Git state unavailable." (or "Not a git repository.") and continue.

Why this matters for the crash-recovery use case: the verbatim response tells you what was *said*; the git tree tells you what was actually *on disk* at that moment. After a crash, "HEAD was at a3f91c2 with 4 modified files" instantly tells the user whether their code changes survived or whether they're recovering from the snapshot text.

## When to offer it proactively

Don't guess at an abstract "natural stopping point" — an LLM has no reliable sense of one, and over-offering is noise. Offer a snapshot only on a concrete, observable cue, and only when there's meaningful unsaved progress that would be costly to reconstruct:

- A test suite or eval run just went green after non-trivial work.
- The user signals satisfaction right after a hard fix lands ("that worked", "perfect", "nice").
- The user signals they're stepping away ("brb", "one sec", "heading to bed", "signing off").
- A long session has produced unsaved findings and no snapshot exists yet.

Offer at most once per stopping point, in one line. If the user declines, don't re-ask until the next distinct cue.

## Safety and scope

Snapshotting is read-mostly. The only write you may make is creating or prepending to `snapshot.md`.

Do **not**, as part of a snapshot: stage, commit, stash, reset, checkout, or otherwise mutate git; run tests, builds, formatters, installers, migrations, or cleanup commands; or rewrite/summarize older entries. Capturing state must never change state — a "helpful" extra action taken while snapshotting is a bug, not a courtesy.

## Behavior rules

- Confirm completion on screen with the file path **and a compact git-state line** so the user sees their disk state at a glance without opening the file. Format:

  > 📸 Snapshot saved to `./snapshot.md` (2026-06-09 22:47)
  > Git: `feature/onboarding-v2` @ `a3f91c2` — 4 modified, 1 untracked, ahead 2

  If not a git repo, the second line is simply omitted. Don't re-print the full snapshot content into the chat — the user just lived it.
- Never trim, summarize, or "clean up" the verbatim response section. Crash recovery only works if the saved copy is the real copy.
- If the most recent substantive response is the *same one* already captured in the previous snapshot (nothing new since), write a lightweight entry — metadata only, with "No new substantive response since the snapshot at <time>" in place of the verbatim block — rather than re-dumping an identical copy.
- After reading the existing file, check its length. If it exceeds ~2,000 lines, mention once in the confirmation that you can archive older entries to `snapshot-archive.md` — but only do it if asked. Additive means additive.
- Multiple snapshots in one session are fine and expected; each gets its own timestamped entry.