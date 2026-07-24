# Optional Deterministic Git Enforcement

The main Skill instructions are behavioral. They cannot mechanically prove whether every file edit is semantically in scope. Use Claude Code permission rules, worktrees, or repository-specific hooks when stronger boundaries are required.

The bundled helper provides one narrow optional guard: while a BTW session is active, block mutating or unrecognized Git commands unless the current focus explicitly sets `allow_git_writes:true`.

## Project-scoped hook

For a project installation at `.claude/skills/btw/`, add this to `.claude/settings.json` and merge it with any existing hook configuration:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"$CLAUDE_PROJECT_DIR/.claude/skills/btw/scripts/btw.py\" guard-git-hook"
          }
        ]
      }
    ]
  }
}
```

## Personal-skill hook

For a personal installation at `~/.claude/skills/btw/`, use a user-level hook in `~/.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"$HOME/.claude/skills/btw/scripts/btw.py\" guard-git-hook"
          }
        ]
      }
    ]
  }
}
```

On systems where the interpreter is named `python`, replace `python3` accordingly.

## Guard behavior

The guard:

- reads the hook payload from stdin;
- identifies the active BTW log using `session_id` and `cwd`;
- allows commands when no BTW session is active;
- allows read-only Git inspection commands;
- denies mutating or unrecognized Git commands when `allow_git_writes` is false;
- allows Git writes after the focus is explicitly updated with `allow_git_writes:true`.

The parser is intentionally conservative. Complex or unfamiliar Git commands may be blocked even when they are read-only. Update the focus flag or temporarily disable the hook only after reviewing the exact command.

## What this does not enforce

The guard does not determine whether a normal file edit belongs to a focus task. Natural-language task boundaries are not a reliable filesystem policy. For stricter isolation, combine BTW with one of these controls:

- a dedicated Git worktree for the focus session;
- Claude Code deny rules for sensitive paths;
- repository-specific `PreToolUse` hooks that allow writes only under declared directories;
- operating-system permissions or a disposable container.
