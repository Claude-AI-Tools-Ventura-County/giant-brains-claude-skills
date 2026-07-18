#!/usr/bin/env bash
# stay-focused — wire the session-anchor guard hooks into Claude Code's settings.json.
#
#   ./install.sh              install (or re-install; idempotent)
#   ./install.sh --uninstall  strip the hook entries back out
#
# Installing the hooks does NOT set an anchor. It stays opt-in: run
# `stay focused on <task>` inside Claude Code when you want it, `/stay-focused off`
# when you don't. With no anchor set the hooks emit nothing.
#
# settings.json keeps absolute paths into this repo, so `git pull` updates the
# hooks in place — same philosophy as the skill symlink loop in the README.
#
# Coexists with the rabbit-hole guard: both register on SessionStart /
# UserPromptSubmit, and each strips only its own script entries, so installing or
# uninstalling one leaves the other's hooks untouched.

set -uo pipefail

HOOK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
SETTINGS="$CLAUDE_DIR/settings.json"

MODE="install"
[[ "${1:-}" == "--uninstall" ]] && MODE="uninstall"

command -v node >/dev/null 2>&1 || { echo "error: node not found on PATH" >&2; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "error: python3 not found on PATH" >&2; exit 1; }

mkdir -p "$CLAUDE_DIR"
[ -f "$SETTINGS" ] || echo '{}' > "$SETTINGS"

# Back up before touching a file the user's whole Claude Code setup depends on.
cp "$SETTINGS" "$SETTINGS.stay-focused.bak"

python3 - "$SETTINGS" "$HOOK_DIR" "$MODE" <<'PY'
import json, sys, os

settings_path, hook_dir, mode = sys.argv[1], sys.argv[2], sys.argv[3]

try:
    with open(settings_path) as f:
        settings = json.load(f)
except json.JSONDecodeError as e:
    # Claude Code tolerates comments in settings.json; json.load does not.
    # Refuse rather than clobber a file we cannot faithfully round-trip.
    sys.exit(f"error: {settings_path} is not plain JSON ({e}).\n"
             f"Strip comments, or add the hooks by hand — see HOOKS.md.")

hooks = settings.setdefault("hooks", {})

def strip(event):
    """Drop our entries, keep everyone else's (including rabbit-hole's). Makes
    install idempotent and uninstall total."""
    groups = hooks.get(event, [])
    kept = []
    for group in groups:
        inner = [h for h in group.get("hooks", [])
                 if "focus-activate.js" not in h.get("command", "")
                 and "focus-tracker.js" not in h.get("command", "")]
        if inner:
            group["hooks"] = inner
            kept.append(group)
        elif not group.get("hooks"):
            kept.append(group)  # someone else's empty group; leave it alone
    if kept:
        hooks[event] = kept
    else:
        hooks.pop(event, None)

strip("SessionStart")
strip("UserPromptSubmit")

if mode == "install":
    for event, script in (("SessionStart", "focus-activate.js"),
                          ("UserPromptSubmit", "focus-tracker.js")):
        cmd = f'node "{os.path.join(hook_dir, script)}"'
        hooks.setdefault(event, []).append(
            {"hooks": [{"type": "command", "command": cmd}]}
        )

if not hooks:
    settings.pop("hooks", None)

with open(settings_path, "w") as f:
    json.dump(settings, f, indent=2)
    f.write("\n")
PY

rc=$?
if [ $rc -ne 0 ]; then
  echo "restoring $SETTINGS from backup" >&2
  mv "$SETTINGS.stay-focused.bak" "$SETTINGS"
  exit $rc
fi

rm -f "$SETTINGS.stay-focused.bak"

if [ "$MODE" = "install" ]; then
  echo "stay-focused hooks installed → $SETTINGS"
  echo "No anchor set (opt-in). Start a new Claude Code session, then: stay focused on <task>"
else
  # Leave no orphan state behind.
  rm -f "$CLAUDE_DIR/.stay-focused-anchor"
  echo "stay-focused hooks removed → $SETTINGS"
fi
