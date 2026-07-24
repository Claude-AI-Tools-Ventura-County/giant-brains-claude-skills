# BTW Focus Firewall for Claude Code

BTW keeps a Claude Code session on no more than three declared tasks. Assistant-initiated side findings are written to a new append-only Markdown file for each BTW focus session instead of being surfaced in the response.

Each log captures:

- the opening user prompt;
- repository name;
- branch and commit at session start;
- focus history;
- branch changes;
- Action, Review Later, and Interesting entries;
- final completion state and counts.

## Install

Personal installation:

```bash
mkdir -p ~/.claude/skills
cp -R btw ~/.claude/skills/btw
```

Project installation:

```bash
mkdir -p .claude/skills
cp -R btw .claude/skills/btw
```

The ZIP contains the top-level `btw/` directory, so extract or copy that directory into the chosen skills folder.

## Use

Start with explicit tasks:

```text
/btw Fix the auth regression; add regression tests; update the auth documentation
```

Start without tasks and let Claude elicit them:

```text
/btw
```

Re-anchor without reloading the Skill:

```text
btw check
```

End naturally by telling Claude the session is done. The final response includes the repository-relative log path.

## Runtime requirements

- Python 3.9 or newer;
- Git is optional, but repository and branch context require it;
- a Claude Code release that supports Skill substitutions such as `${CLAUDE_SESSION_ID}`, `${CLAUDE_SKILL_DIR}`, and `${CLAUDE_PROJECT_DIR}`.

## Test

From the `btw/` directory:

```bash
python3 -m unittest discover -s tests -v
```

See `references/LOG_FORMAT.md` for the helper interface and `references/ENFORCEMENT.md` for the optional Git guard.
