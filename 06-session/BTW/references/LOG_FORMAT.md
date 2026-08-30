# BTW Log and Helper Reference

Use this reference only when debugging the helper, inspecting the on-disk schema, or integrating the logger with another tool.

## Files created

Each BTW focus session creates one file in the project root:

```text
BTW/YYYY-MM-DDTHHMMSS-<repo>-<branch-at-start>-<session-hash>.md
```

A new file is created after the prior BTW session ends. Re-invoking `/btw` while a BTW session is active reuses the active file unless `start --new` is passed.

The helper stores a small active-session pointer outside the repository:

- `$BTW_STATE_HOME` when set;
- `%LOCALAPPDATA%/claude-btw/state` on Windows;
- `$XDG_STATE_HOME/claude-btw` when set;
- otherwise `~/.local/state/claude-btw`.

The pointer contains no parked findings or opening prompt. It only maps a Claude session and project root to the active log path.

## Human-readable layout

````markdown
# BTW Session — repo @ branch

## Context

- BTW session: `...`
- Claude session: `...`
- Started (local): `...`
- Started (UTC): `...`
- Repository: `...`
- Active branch at start: `...`
- Commit at start: `...`
- Focus at start: pending declaration

## Opening user prompt

```text
/verbatim invoking prompt, with recognized live credentials redacted/
```

## Timeline

- [timestamp] [START] ...
- [timestamp] [FOCUS] ...
- [timestamp] [ACTION] ...
- [timestamp] [CONTEXT] Active branch changed ...
- [timestamp] [END] ...
````

The timeline is append-only. Focus updates and branch changes are appended rather than rewriting the header.

## Embedded metadata

The file contains URL-safe base64 JSON in HTML comments:

- `BTW-SESSION` stores immutable session context.
- `BTW-META` stores one structured event per timeline entry.

The comments make recovery, counting, deduplication, and updates deterministic while leaving the Markdown readable. Do not hand-edit or remove these comments unless you accept that helper recovery may fail.

## Commands

Every command prints one compact JSON object. Operational errors print `ok:false` and exit nonzero.

### `start`

Reads the opening user prompt as raw text from stdin.

```bash
btw.py start --claude-session-id ID --project-dir PATH [--new]
```

Important result fields:

- `created`: whether a new file was created;
- `file`: repository-relative log path;
- `repo`, `branch_at_start`, `commit_at_start`;
- `git_ignored`: `true`, `false`, or `null` outside Git;
- `warning`: non-null only when the new log is not ignored;
- `redactions`: recognized credentials removed from the opening prompt.

### `focus`

Reads either a JSON array or an object from stdin:

```json
["task 1", "task 2"]
```

```json
{"items":["task 1","task 2"],"allow_git_writes":false}
```

The helper requires one to three distinct non-empty items.

### `park`

Reads a non-empty JSON array or `{ "entries": [...] }` from stdin. Each entry supports:

```json
{
  "category": "action | review | interesting",
  "finding": "required one-line observation",
  "why": "required impact, rationale, or context",
  "evidence": "optional test, command, or file evidence",
  "path": "optional repository-relative path"
}
```

Absolute paths are converted to repository-relative paths only when they resolve inside the project root. Paths outside the project root are rejected.

The result reports:

- `written`;
- `duplicates_skipped`;
- `updates_written`;
- current category counts.

An exact duplicate is skipped. A matching category/finding/path with changed rationale or evidence becomes a new update event referencing the earlier event ID.

### `status`

```bash
btw.py status --claude-session-id ID --project-dir PATH [--no-sync-context]
```

Returns the active focus, counts, current file, branch context, and Git-write flag. By default, a branch change is appended as a `CONTEXT` event.

### `show`

```bash
btw.py show --claude-session-id ID --project-dir PATH [--category action|review|interesting]
```

Returns structured parked entries. Use this only after the user explicitly asks to inspect parked content.

### `end`

Reads a JSON object:

```json
{"completed":["task 1"],"open":["task 2"]}
```

Appends the final event, marks the external pointer ended, and leaves the Markdown file immutable except for prior append operations.

### `guard-git-hook`

Reads a Claude Code `PreToolUse` hook payload from stdin. It emits no output when the command is allowed. When an active BTW session blocks a mutating or unrecognized Git command, it returns a structured deny decision. See `ENFORCEMENT.md`.

## Recovery behavior

If the external active-session pointer is missing or stale, the helper scans `BTW/*.md`, reads embedded session metadata, and recovers the newest unended file associated with the same Claude session ID.

## Secret handling

The helper redacts common private-key blocks and token formats before writing. This is defense in depth, not a complete secret scanner. The skill must still apply the safety override, tell the user about a live credential, revoke it at the provider first, and then scrub stored copies.
