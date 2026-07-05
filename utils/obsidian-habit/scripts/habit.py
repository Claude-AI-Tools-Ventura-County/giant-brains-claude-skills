#!/usr/bin/env python3
"""
habit.py — Obsidian Habit Builder state machine.

Single write path for state.json (atomic tmp+rename). Append-only events.jsonl.
UTC timestamps only. No external dependencies (stdlib only).

Usage:
  habit.py init     --vault PATH
  habit.py status   --vault PATH
  habit.py respond  <adopt|decline|defer>
  habit.py jump     <tactic>
  habit.py reorder  <csv-of-tactics>
  habit.py decline-permanently <tactic>
  habit.py pause
  habit.py resume
  habit.py show-log [-n N]
"""
import argparse
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_ORDER = ["homepage", "archive", "capture", "pull", "streak"]
STATE_DIRNAME = "_meta/obsidian-habit"
STATE_FILE = "state.json"
LOG_FILE = "events.jsonl"


def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def today_utc():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def resolve_vault(args_vault):
    vault = args_vault or os.environ.get("OBSIDIAN_VAULT_PATH")
    if not vault:
        sys.exit("No vault path. Pass --vault PATH or set OBSIDIAN_VAULT_PATH.")
    p = Path(vault).expanduser().resolve()
    if not p.is_dir():
        sys.exit(f"Vault path does not exist or is not a directory: {p}")
    return p


def state_dir(vault):
    return vault / STATE_DIRNAME


def state_path(vault):
    return state_dir(vault) / STATE_FILE


def log_path(vault):
    return state_dir(vault) / LOG_FILE


def atomic_write_json(path, data):
    """Single write path: write to temp file in same dir, then atomic rename."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".tmp-state-")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, indent=2, sort_keys=True)
            f.write("\n")
        os.replace(tmp, path)  # atomic on same filesystem
    except Exception:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise


def append_event(vault, event):
    event = {"ts": now_iso(), **event}
    p = log_path(vault)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a") as f:
        f.write(json.dumps(event, sort_keys=True) + "\n")


def load_state(vault):
    sp = state_path(vault)
    if not sp.exists():
        sys.exit("Not initialized. Run: habit.py init --vault PATH")
    with open(sp) as f:
        return json.load(f)


def new_state(vault):
    return {
        "version": 1,
        "vault_path": str(vault),
        "created_utc": now_iso(),
        "tactic_order": list(DEFAULT_ORDER),
        "current_index": 0,
        "status": {t: "pending" for t in DEFAULT_ORDER},
        "last_run_date": None,
        "paused": False,
        "streak_count": 0,
        "phase": "ONBOARDING",  # ONBOARDING | MAINTENANCE
    }


def current_tactic(state):
    order = state["tactic_order"]
    idx = state["current_index"]
    if state["phase"] == "MAINTENANCE" or idx >= len(order):
        return None
    return order[idx]


def cmd_init(args):
    vault = resolve_vault(args.vault)
    sp = state_path(vault)
    if sp.exists():
        print(f"Already initialized at {sp}")
        return
    state = new_state(vault)
    atomic_write_json(sp, state)
    append_event(vault, {"event": "init", "vault": str(vault)})
    print(f"Initialized. First tactic: {current_tactic(state)}")


def cmd_status(args):
    vault = resolve_vault(args.vault)
    state = load_state(vault)
    tactic = current_tactic(state)
    print(f"Phase: {state['phase']}")
    print(f"Today (UTC): {today_utc()}  Last run: {state['last_run_date']}")
    print(f"Paused: {state['paused']}")
    if tactic:
        print(f"Current tactic ({state['current_index']+1}/{len(state['tactic_order'])}): {tactic}")
    else:
        print("Current tactic: none (all tactics decided)")
    print(f"Streak: {state['streak_count']} day(s)")
    print("Status per tactic:")
    for t in state["tactic_order"]:
        print(f"  - {t}: {state['status'].get(t, 'pending')}")
    already_ran_today = state["last_run_date"] == today_utc()
    print(f"already_run_today: {already_ran_today}")


def _advance(state):
    state["current_index"] += 1
    if state["current_index"] >= len(state["tactic_order"]):
        state["phase"] = "MAINTENANCE"


def cmd_respond(args):
    vault = resolve_vault(args.vault)
    state = load_state(vault)
    tactic = current_tactic(state)
    if tactic is None:
        print("No active tactic (already in MAINTENANCE).")
        return
    decision = args.decision
    if decision in ("adopt", "decline"):
        state["status"][tactic] = "adopted" if decision == "adopt" else "declined"
        _advance(state)
    elif decision == "defer":
        state["status"][tactic] = "deferred"
        # no advance — same tactic queued for tomorrow
    else:
        sys.exit("decision must be adopt, decline, or defer")
    state["last_run_date"] = today_utc()
    if decision != "decline":
        state["streak_count"] = state.get("streak_count", 0) + 1
    atomic_write_json(state_path(vault), state)
    append_event(vault, {"event": "respond", "tactic": tactic, "decision": decision})
    nxt = current_tactic(state)
    print(f"Recorded '{decision}' for {tactic}. Next up: {nxt or 'MAINTENANCE'}")


def cmd_jump(args):
    vault = resolve_vault(args.vault)
    state = load_state(vault)
    if args.tactic not in state["tactic_order"]:
        sys.exit(f"Unknown tactic '{args.tactic}'. Options: {state['tactic_order']}")
    state["current_index"] = state["tactic_order"].index(args.tactic)
    state["phase"] = "ONBOARDING"
    atomic_write_json(state_path(vault), state)
    append_event(vault, {"event": "jump", "tactic": args.tactic})
    print(f"Jumped to: {args.tactic}")


def cmd_reorder(args):
    vault = resolve_vault(args.vault)
    state = load_state(vault)
    new_order = [t.strip() for t in args.csv.split(",") if t.strip()]
    if sorted(new_order) != sorted(state["tactic_order"]):
        sys.exit(f"Reorder list must contain exactly these tactics: {state['tactic_order']}")
    current = current_tactic(state)
    state["tactic_order"] = new_order
    state["current_index"] = new_order.index(current) if current in new_order else 0
    atomic_write_json(state_path(vault), state)
    append_event(vault, {"event": "reorder", "new_order": new_order})
    print(f"Reordered: {new_order}")


def cmd_decline_permanently(args):
    vault = resolve_vault(args.vault)
    state = load_state(vault)
    if args.tactic not in state["status"]:
        sys.exit(f"Unknown tactic '{args.tactic}'")
    state["status"][args.tactic] = "declined"
    if current_tactic(state) == args.tactic:
        _advance(state)
    atomic_write_json(state_path(vault), state)
    append_event(vault, {"event": "decline_permanently", "tactic": args.tactic})
    print(f"Permanently declined: {args.tactic}")


def cmd_pause(args):
    vault = resolve_vault(args.vault)
    state = load_state(vault)
    state["paused"] = True
    atomic_write_json(state_path(vault), state)
    append_event(vault, {"event": "pause"})
    print("Paused. Daily counter frozen until resume.")


def cmd_resume(args):
    vault = resolve_vault(args.vault)
    state = load_state(vault)
    state["paused"] = False
    atomic_write_json(state_path(vault), state)
    append_event(vault, {"event": "resume"})
    print("Resumed.")


def cmd_show_log(args):
    vault = resolve_vault(args.vault)
    lp = log_path(vault)
    if not lp.exists():
        print("No log yet.")
        return
    lines = lp.read_text().splitlines()
    for line in lines[-args.n :]:
        print(line)


def build_parser():
    p = argparse.ArgumentParser(description="Obsidian Habit Builder FSM")
    p.add_argument("--vault", help="Path to Obsidian vault (or set OBSIDIAN_VAULT_PATH)")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init").set_defaults(func=cmd_init)
    sub.add_parser("status").set_defaults(func=cmd_status)

    r = sub.add_parser("respond")
    r.add_argument("decision", choices=["adopt", "decline", "defer"])
    r.set_defaults(func=cmd_respond)

    j = sub.add_parser("jump")
    j.add_argument("tactic")
    j.set_defaults(func=cmd_jump)

    ro = sub.add_parser("reorder")
    ro.add_argument("csv")
    ro.set_defaults(func=cmd_reorder)

    dp = sub.add_parser("decline-permanently")
    dp.add_argument("tactic")
    dp.set_defaults(func=cmd_decline_permanently)

    sub.add_parser("pause").set_defaults(func=cmd_pause)
    sub.add_parser("resume").set_defaults(func=cmd_resume)

    sl = sub.add_parser("show-log")
    sl.add_argument("-n", type=int, default=10)
    sl.set_defaults(func=cmd_show_log)

    return p


def main():
    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
