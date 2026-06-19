# Skill Sync Plan

Bidirectional, last-write-wins sync of `swe/SKILL.md` across two repos on this Mac.

---

## Problem

A skill file lives in two different git repos. Both repos evolve independently. Manually keeping them in sync is fragile. We want the newest version to automatically propagate to the other repo without human intervention.

---

## Terminology

This is **last-write-wins (LWW) bidirectional file sync**: when the same logical file exists in two locations, the copy with the newer modification time (`mtime`) is the source of truth and overwrites the older copy.

---

## Key Catch: Git Resets mtime

Git does **not** preserve file modification times. When you `git checkout`, `git pull`, or `git merge`, any touched file gets the current system timestamp — even if the file content didn't change. This means a freshly-pulled file would always look "newest" and clobber the actual latest edits.

**Fix:** Always check content first. Only sync if the files differ in content (MD5/SHA hash). If they're identical, do nothing regardless of timestamps. Only when content differs does the mtime comparison decide the winner.

---

## Sync Logic (per run)

```
1. Hash both files.
2. If hashes match → done. No sync needed.
3. If hashes differ → compare mtime of both files.
4. Copy the newer file over the older file (preserving mtime with cp -p).
5. Log the action: which file won, timestamp, size.
```

---

## Components

### 1. Shell Script: `skill-sync.sh`

Location: `utils/skill-sync/skill-sync.sh`

Responsibilities:
- Read file pairs from a config file
- Implement the hash-then-mtime logic above
- Write a log entry to `utils/skill-sync/skill-sync.log`
- Exit 0 on success, non-zero on any error (missing file, permission issue)

### 2. Config File: `skill-sync.conf`

Location: `utils/skill-sync/skill-sync.conf`

Format (one pair per line, tab-separated):
```
/path/to/repo-a/swe/SKILL.md	/path/to/repo-b/swe/SKILL.md
```

This makes the script reusable for other file pairs across other repos without editing the script itself.

### 3. launchd Plist: `com.local.skill-sync.plist`

Location: `~/Library/LaunchAgents/com.local.skill-sync.plist`

- Runs `skill-sync.sh` every **2 minutes**
- Starts on login, survives reboots
- Stdout/stderr redirected to the log file
- No third-party dependencies (no fswatch, no Homebrew packages)

Why launchd over cron:
- macOS native
- Runs as the current user, so it has the same file permissions as your shell
- Survives sleep/wake cycles more reliably than cron on macOS

### 4. Log File: `skill-sync.log`

Location: `utils/skill-sync/skill-sync.log`

Each line: `[ISO timestamp] [direction: A→B or B→A or NO-OP] [reason]`

Gitignored — runtime output, not tracked state.

---

## Failure Modes to Handle

| Scenario | Handling |
|---|---|
| One file doesn't exist yet | Copy the existing one to the missing location; log as "seeded" |
| Both files missing | Log error, exit non-zero |
| Permission denied | Log error, exit non-zero |
| Git resets mtime after pull | Hash check catches this — identical content = no-op |
| File open/being actively edited | `cp -p` on macOS is atomic enough for a text file; acceptable risk |
| Disk full | `cp` will fail; log error, exit non-zero |

---

## What's Not in Scope

- **Three-way merge:** If both files differ in content AND were both edited since the last sync, LWW simply overwrites the older one. The newer edit wins; the older edit is lost. This is acceptable for a skill file where one person is the primary editor.
- **Git commit/push:** The script only syncs the working tree. Committing the synced file to git is a manual step.
- **Remote/cloud sync:** Mac-local only, between two paths on the same filesystem.

---

## Rollout Steps

1. Write `skill-sync.sh` with hash+mtime logic and config-file support
2. Write `skill-sync.conf` with the actual repo paths
3. Dry-run manually: `bash skill-sync.sh --dry-run`
4. Confirm correct winner is selected on a test edit
5. Install launchd plist: `launchctl load ~/Library/LaunchAgents/com.local.skill-sync.plist`
6. Verify first automated run via log file
7. Add `skill-sync.log` to `.gitignore`

---

## Open Questions Before Building

1. **What are the two full repo paths?** The script needs them in `skill-sync.conf`.
2. **Is `swe/SKILL.md` the only file to sync, or are there others now or soon?** Affects whether the config-file abstraction is worth it.
3. **Should the script handle a missing `swe/` directory in the destination?** (`mkdir -p` before copying)
