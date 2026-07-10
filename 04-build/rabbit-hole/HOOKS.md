# rabbit-hole — always-on guard (optional)

The `rabbit-hole` skill works fine on its own: type `/rabbit-hole` when an agent
is dripping "one more thing" at you, and it sweeps the task once and triages.

The problem is that you have to *notice* the drip and *remember* the skill —
usually two or three interruptions after it started costing you. Skill
auto-invocation keys off the `description` field, which competes with every
other skill's description and loses badly mid-task.

These hooks close that gap. They put the trigger rule directly in the model's
context, on every turn, so the agent fires the skill **on itself** before the
third unsolicited finding — instead of waiting for you to get annoyed enough to
invoke it.

## What it is not

It does not force every reply into buckets. It injects a *trigger rule*, not a
response template. Ordinary replies stay ordinary. The triage format appears
only when scope is actually drifting — and the rule explicitly forbids inventing
findings to fill an empty bucket, which is the failure mode a
"always-use-the-format" instruction produces.

## Install

```bash
04-build/rabbit-hole/hooks/install.sh
```

This wires two hooks into `~/.claude/settings.json` (or `$CLAUDE_CONFIG_DIR`):

| Hook | Script | Job |
|---|---|---|
| `SessionStart` | `rabbit-activate.js` | Injects the full trigger ruleset once per session, as hidden system context. |
| `UserPromptSubmit` | `rabbit-tracker.js` | Toggles the guard; re-anchors a one-paragraph reminder each turn. |

settings.json stores absolute paths into this repo, so `git pull` updates the
hooks in place — the same idea as the skill symlink loop in the README.

Installing does **not** switch the guard on.

## Use

| Command | Effect |
|---|---|
| `/rabbit-hole on` | Guard on. Persists across sessions until turned off. |
| `/rabbit-hole off` | Guard off. Hooks stay installed and emit nothing. |
| `/rabbit-hole` | Unchanged — a one-shot triage, guard or no guard. |

Natural language works too: "turn on rabbit hole guard", "disable rabbit hole".

Note that `stop` is deliberately **not** an off-switch phrase. "Stop going down
rabbit holes" is one of the skill's own trigger phrases — someone saying it wants
a triage right now, not to uninstall the thing that produces one.

State lives in one file, `$CLAUDE_CONFIG_DIR/.rabbit-hole-active`. Absent means
off; no hook ever creates it implicitly. Corrupted, oversized, or symlinked flags
read as off rather than as a mode nobody asked for.

## Uninstall

```bash
04-build/rabbit-hole/hooks/install.sh --uninstall
```

Removes both hook entries (leaving any other hooks in `settings.json` alone) and
deletes the flag file. `settings.json` is backed up before either operation and
restored if the write fails.

If your `settings.json` contains comments, the installer refuses to touch it
rather than round-trip it lossily through a plain JSON parser. Add the two
entries by hand:

```jsonc
{
  "hooks": {
    "SessionStart": [
      { "hooks": [ { "type": "command", "command": "node \"/abs/path/to/04-build/rabbit-hole/hooks/rabbit-activate.js\"" } ] }
    ],
    "UserPromptSubmit": [
      { "hooks": [ { "type": "command", "command": "node \"/abs/path/to/04-build/rabbit-hole/hooks/rabbit-tracker.js\"" } ] }
    ]
  }
}
```

## Cost

`rabbit-ruleset.md` is 2,129 characters / 347 words; the per-turn reminder is 400
characters / 71 words. Estimating at 3.7 chars-per-token and 1.35 tokens-per-word,
that puts the SessionStart injection near **470–575 tokens once per session** and
the reminder near **95–110 tokens per turn**. These are heuristic bounds, not a
tokenizer count — measure with the real tokenizer before quoting them anywhere
that matters.

Both are exactly zero when the guard is off.

## Files

| File | Role |
|---|---|
| `rabbit-ruleset.md` | Single source of truth for the injected rules. Edit here. |
| `rabbit-config.js` | Flag helpers. Symlink-safe, size-capped, whitelist-validated. |
| `rabbit-activate.js` | SessionStart hook. |
| `rabbit-tracker.js` | UserPromptSubmit hook. |
| `package.json` | Pins the dir to CommonJS so `require()` survives an ancestor ESM `package.json`. |
| `install.sh` | Idempotent settings.json merge; `--uninstall` reverses it. |

Both hooks silent-fail on every filesystem error and exit 0 unconditionally — a
broken hook must never block session start.

## Attribution

The hook architecture (flag file + SessionStart injection + per-turn
reinforcement) and the symlink-hardened flag read/write in `rabbit-config.js` are
adapted from [caveman](https://github.com/JuliusBrussee/caveman) by Julius
Brussee, MIT licensed. The MIT notice is retained in `rabbit-config.js`; MIT
permits relicensing into this GPL v2 work.
