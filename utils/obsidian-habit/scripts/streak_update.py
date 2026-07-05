#!/usr/bin/env python3
"""
streak_update.py — Tactic 5: visible streak so breaking it feels worse than
the friction of opening the app.

Marks today as "touched" if any .md file in the vault (outside excluded dirs)
has an mtime of today (UTC), OR if called with --mark to force-mark today
regardless of file scan (e.g. right after the daily habit run itself).

Writes a single ledger file: _meta/obsidian-habit/streak.json
  { "days": ["2026-07-01", "2026-07-02", ...], "current_streak": N }

Usage:
  streak_update.py --vault PATH            # scan-based check
  streak_update.py --vault PATH --mark     # force-mark today touched
"""
import argparse
import json
import os
import time
from pathlib import Path

EXCLUDE_DIRS = {"_meta", "_archive", ".obsidian", ".git", ".trash"}
MAX_SCAN = 2000  # bounded query


def today_utc():
    return time.strftime("%Y-%m-%d", time.gmtime())


def touched_today(vault):
    today = today_utc()
    scanned = 0
    for root, dirs, files in os.walk(vault):
        rel_root = Path(root).relative_to(vault)
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        if any(p in EXCLUDE_DIRS for p in rel_root.parts):
            continue
        for name in files:
            if not name.endswith(".md"):
                continue
            scanned += 1
            if scanned > MAX_SCAN:
                return False
            full = Path(root) / name
            try:
                mtime_day = time.strftime("%Y-%m-%d", time.gmtime(full.stat().st_mtime))
            except OSError:
                continue
            if mtime_day == today:
                return True
    return False


def load_ledger(path):
    if path.exists():
        return json.loads(path.read_text())
    return {"days": [], "current_streak": 0}


def compute_streak(days):
    if not days:
        return 0
    days_sorted = sorted(days)
    streak = 1
    for i in range(len(days_sorted) - 1, 0, -1):
        d1 = time.strptime(days_sorted[i - 1], "%Y-%m-%d")
        d2 = time.strptime(days_sorted[i], "%Y-%m-%d")
        delta = (time.mktime(d2) - time.mktime(d1)) / 86400
        if delta == 1:
            streak += 1
        else:
            break
    return streak


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--vault")
    p.add_argument("--mark", action="store_true", help="force-mark today as touched")
    args = p.parse_args()

    vault = Path(args.vault or os.environ.get("OBSIDIAN_VAULT_PATH", "")).expanduser()
    if not vault.is_dir():
        raise SystemExit("Valid --vault PATH required (or set OBSIDIAN_VAULT_PATH).")

    ledger_path = vault / "_meta" / "obsidian-habit" / "streak.json"
    ledger = load_ledger(ledger_path)
    today = today_utc()

    was_touched = args.mark or touched_today(vault)
    if was_touched and today not in ledger["days"]:
        ledger["days"].append(today)
        ledger["days"] = sorted(set(ledger["days"]))

    ledger["current_streak"] = compute_streak(ledger["days"])

    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = ledger_path.with_suffix(".tmp")
    tmp.write_text(json.dumps(ledger, indent=2, sort_keys=True))
    os.replace(tmp, ledger_path)  # atomic, single write path

    print(f"Touched today: {was_touched}")
    print(f"Current streak: {ledger['current_streak']} day(s)")


if __name__ == "__main__":
    main()
