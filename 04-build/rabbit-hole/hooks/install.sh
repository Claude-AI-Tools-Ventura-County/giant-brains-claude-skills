#!/usr/bin/env bash
# rabbit-hole — wire the scope-drip guard hooks into Claude Code's settings.json.
#
#   ./install.sh              install (or re-install; idempotent)
#   ./install.sh --uninstall  strip the hook entries back out
#
# Installing the hooks does NOT switch the guard on. It stays opt-in: run
# `/rabbit-hole on` inside Claude Code when you want it, `/rabbit-hole off` when
# you don't. With the guard off the hooks emit nothing.
#
# settings.json keeps absolute paths into this repo, so `git pull` updates the
# hooks in place — same philosophy as the skill symlink loop in the README.

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
cp "$SETTINGS" "$SETTINGS.rabbit-hole.bak"

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
    """Drop our entries, keep everyone else's. Makes install idempotent and
    uninstall total."""
    groups = hooks.get(event, [])
    kept = []
    for group in groups:
        inner = [h for h in group.get("hooks", [])
                 if "rabbit-activate.js" not in h.get("command", "")
                 and "rabbit-tracker.js" not in h.get("command", "")]
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
    for event, script in (("SessionStart", "rabbit-activate.js"),
                          ("UserPromptSubmit", "rabbit-tracker.js")):
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
  mv "$SETTINGS.rabbit-hole.bak" "$SETTINGS"
  exit $rc
fi

rm -f "$SETTINGS.rabbit-hole.bak"

if [ "$MODE" = "install" ]; then
  echo "rabbit-hole hooks installed → $SETTINGS"
  echo "Guard is OFF (opt-in). Start a new Claude Code session, then: /rabbit-hole on"
else
  # Leave no orphan state behind.
  rm -f "$CLAUDE_DIR/.rabbit-hole-active"
  echo "rabbit-hole hooks removed → $SETTINGS"
fi
