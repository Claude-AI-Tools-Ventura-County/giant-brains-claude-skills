# stay-focused — always-on guard (recommended)

The `stay-focused` skill can run on its own: say `stay focused on <task>` and the
model adopts the anchor-first reply shape.

The problem is that a *whole-session* contract is exactly the kind of instruction
that decays. Skill auto-invocation keys off the `description` field, which competes
with every other skill's description; and even once adopted, the anchor and format
fade from attention as context fills with tangents, tool output, and compaction.
The one behavior stay-focused promises — *never lose the original task* — is the
one plain instructions are worst at keeping.

These hooks close that gap. They store the anchor in a flag file and re-inject it
— plus the reply shape — on every turn, and re-inject it into a session resumed the
next morning. The model leads with the anchor's status because the anchor is in
front of it every single turn, not because it happened to remember.

## What it is not

It does not force ordinary chit-chat into buckets. When no anchor is set the hooks
emit **nothing** and the session is identical to a stock one. The format applies
only while an anchor is set, and the rule explicitly forbids inventing items to
fill an empty bucket — empty sections are dropped, not faked.

## Install

```bash
04-build/stay-focused/hooks/install.sh              # wire the hooks in (no anchor set)
04-build/stay-focused/hooks/install.sh --uninstall  # take them back out
```

This wires two hooks into `~/.claude/settings.json` (or `$CLAUDE_CONFIG_DIR`):

| Hook | Script | Job |
|---|---|---|
| `SessionStart` | `focus-activate.js` | If an anchor is set, injects the full ruleset (anchor spliced in) once per session, as hidden system context. |
| `UserPromptSubmit` | `focus-tracker.js` | Sets the anchor from "stay focused on X", clears it on an explicit off, and re-anchors a short reminder each turn while one is set. |

settings.json stores absolute paths into this repo, so `git pull` updates the
hooks in place — the same idea as the skill symlink loop in the README.

Installing does **not** set an anchor. It stays opt-in.

## Use

| Command | Effect |
|---|---|
| `stay focused on <task>` | Set the anchor. Persists across sessions until cleared. |
| `stay on track for <task>` | Same — an alternate phrasing. |
| `/stay-focused <task>` | Same, as a slash command. |
| `/stay-focused off` | Clear the anchor. Hooks stay installed and emit nothing. |
| `stay focused` *(no task)* | If nothing is set, the model asks what to lock onto. |

Natural language works throughout: "keep me focused on the migration", "drop the
focus", "stop staying focused".

Note that a bare `stop` is deliberately **not** an off-switch — it only clears the
anchor when bound to focus/track ("stop staying focused"). A bare "stop" mid-task
means stop *the task*, not uninstall the thing tracking it.

## Coexistence with rabbit-hole

Both guards register on `SessionStart` and `UserPromptSubmit`. Each installer
strips only its own script entries, so installing or uninstalling one leaves the
other's hooks untouched. Run both at once if you like — a session can have a
stay-focused anchor *and* the rabbit-hole drip guard active together.

## State

State lives in one file, `$CLAUDE_CONFIG_DIR/.stay-focused-anchor`, holding the
anchor text. Absent or empty means off; no hook ever creates it implicitly. The
anchor is sanitized to a single printable line and capped at 512 bytes; a
corrupted, oversized, or symlinked flag reads as "no anchor" rather than as a mode
nobody asked for. Both hooks silent-fail on every filesystem error and exit 0 — a
broken hook must never block session start.

## Uninstall

```bash
04-build/stay-focused/hooks/install.sh --uninstall
```

Removes both hook entries (leaving any other hooks in `settings.json`, including
rabbit-hole's, alone) and deletes the flag file. `settings.json` is backed up
before either operation and restored if the write fails.

If your `settings.json` contains comments, the installer refuses to touch it
rather than round-trip it lossily through a plain JSON parser. Add the two entries
by hand:

```jsonc
{
  "hooks": {
    "SessionStart": [
      { "hooks": [ { "type": "command", "command": "node \"/abs/path/to/04-build/stay-focused/hooks/focus-activate.js\"" } ] }
    ],
    "UserPromptSubmit": [
      { "hooks": [ { "type": "command", "command": "node \"/abs/path/to/04-build/stay-focused/hooks/focus-tracker.js\"" } ] }
    ]
  }
}
```

## Cost

`focus-ruleset.md` builds to roughly 1,970 characters / 360 words with a typical
anchor; the per-turn reminder is roughly 750 characters / 136 words. Estimating at
3.7 chars-per-token and 1.35 tokens-per-word, that puts the SessionStart injection
near **485–535 tokens once per session** and the reminder near **185–205 tokens
per turn**. These are heuristic bounds, not a tokenizer count — measure with the
real tokenizer before quoting them anywhere that matters.

Both are exactly zero when no anchor is set.

## Files

| File | Role |
|---|---|
| `focus-ruleset.md` | Single source of truth for the injected rules. `{{ANCHOR}}` is replaced with the live anchor. Edit here. |
| `focus-config.js` | Flag helpers. Symlink-safe, size-capped, sanitizing read/write. |
| `focus-activate.js` | SessionStart hook. |
| `focus-tracker.js` | UserPromptSubmit hook. |
| `package.json` | Pins the dir to CommonJS so `require()` survives an ancestor ESM `package.json`. |
| `install.sh` | Idempotent settings.json merge; `--uninstall` reverses it. |

Both hooks silent-fail on every filesystem error and exit 0 unconditionally — a
broken hook must never block session start.

## Attribution

The hook architecture (flag file + SessionStart injection + per-turn
reinforcement) and the symlink-hardened flag read/write in `focus-config.js` are
adapted from [caveman](https://github.com/JuliusBrussee/caveman) by Julius
Brussee, MIT licensed. The MIT notice is retained in `focus-config.js`; MIT
permits relicensing into this GPL v2 work.
