#!/usr/bin/env python3
"""
archive_stale_notes.py — Tactic 3: hide untouched notes into a flat
"Older than N days" archive folder so the vault root only shows what's "alive."

Safety rules (non-negotiable, see SKILL.md):
  - Dry-run by default. Nothing moves unless --apply is passed.
  - Bounded scan: --max-files caps how many candidates are even considered.
  - Every --apply writes a manifest (old_path -> new_path) so it's reversible
    with --undo.
  - rebalance-OS indexes the whole vault path already, so archiving a note
    does not remove it from RAG/search — it only leaves the visible tree.
  - Files listed in <vault>/_meta/obsidian-habit/archive-whitelist.txt are
    never moved, regardless of last-edit date. Auto-created on first run.

Usage:
  archive_stale_notes.py --vault PATH [--days 21] [--max-files 500]
  archive_stale_notes.py --vault PATH --apply [--days 21] [--max-files 500]
  archive_stale_notes.py --vault PATH --undo MANIFEST.json
"""
import argparse
import json
import os
import shutil
import sys
import time
from pathlib import Path

EXCLUDE_DIRS = {"_meta", "_archive", ".obsidian", ".git", ".trash"}

WHITELIST_HEADER = """\
# archive-whitelist.txt
# One entry per line: a bare filename (e.g. README.md) matches that name
# anywhere in the vault; a relative path (e.g. Projects/README.md) matches
# only that exact file. Lines starting with # and blank lines are ignored.
# Whitelisted files are never moved by archive_stale_notes.py, regardless
# of last-edit date.
"""


def archive_dir_name(days):
    return f"Older than {days} days"


def whitelist_path(vault):
    return vault / "_meta" / "obsidian-habit" / "archive-whitelist.txt"


def load_whitelist(vault):
    path = whitelist_path(vault)
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(WHITELIST_HEADER)
        return set()
    entries = set()
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        entries.add(line)
    return entries


def is_whitelisted(full, vault, whitelist):
    return full.name in whitelist or full.relative_to(vault).as_posix() in whitelist


def is_excluded(rel_parts, extra_exclude):
    exclude = EXCLUDE_DIRS | {extra_exclude}
    return any(part in exclude for part in rel_parts)


def find_stale_notes(vault, days, max_files):
    cutoff = time.time() - (days * 86400)
    extra_exclude = archive_dir_name(days)
    whitelist = load_whitelist(vault)
    candidates = []
    for root, dirs, files in os.walk(vault):
        rel_root = Path(root).relative_to(vault)
        dirs[:] = [d for d in dirs if not is_excluded(rel_root.parts + (d,), extra_exclude)]
        if is_excluded(rel_root.parts, extra_exclude):
            continue
        for name in files:
            if not name.endswith(".md"):
                continue
            full = Path(root) / name
            if is_whitelisted(full, vault, whitelist):
                continue
            try:
                mtime = full.stat().st_mtime
            except OSError:
                continue
            if mtime < cutoff:
                candidates.append(full)
            if len(candidates) >= max_files:  # bounded query
                return candidates
    return candidates


def do_dry_run(vault, days, max_files):
    stale = find_stale_notes(vault, days, max_files)
    print(f"Dry run: {len(stale)} note(s) older than {days} days untouched (max scan {max_files}).")
    for f in stale[:20]:
        print(f"  {f.relative_to(vault)}")
    if len(stale) > 20:
        print(f"  ... and {len(stale) - 20} more")
    print("\nNothing moved. Re-run with --apply to archive these.")
    return stale


def do_apply(vault, days, max_files):
    stale = find_stale_notes(vault, days, max_files)
    if not stale:
        print("Nothing to archive.")
        return
    archive_dir = vault / archive_dir_name(days)
    archive_dir.mkdir(parents=True, exist_ok=True)
    manifest = {"created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "moves": []}
    for f in stale:
        dest = archive_dir / f.name
        # avoid clobbering same-named files from different folders
        i = 1
        while dest.exists():
            dest = archive_dir / f"{f.stem}-{i}{f.suffix}"
            i += 1
        shutil.move(str(f), str(dest))
        manifest["moves"].append({"old_path": str(f), "new_path": str(dest)})
    manifest_path = vault / "_meta" / "obsidian-habit" / f"archive-manifest-{int(time.time())}.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2))
    print(f"Archived {len(manifest['moves'])} note(s) to {archive_dir}")
    print(f"Manifest (for --undo): {manifest_path}")


def do_undo(manifest_path):
    manifest_path = Path(manifest_path).expanduser().resolve()
    if not manifest_path.exists():
        sys.exit(f"Manifest not found: {manifest_path}")
    manifest = json.loads(manifest_path.read_text())
    restored = 0
    for move in manifest["moves"]:
        old, new = Path(move["old_path"]), Path(move["new_path"])
        if new.exists():
            old.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(new), str(old))
            restored += 1
    print(f"Restored {restored}/{len(manifest['moves'])} note(s).")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--vault")
    p.add_argument("--days", type=int, default=21)
    p.add_argument("--max-files", type=int, default=500)
    p.add_argument("--apply", action="store_true")
    p.add_argument("--undo", metavar="MANIFEST_JSON")
    args = p.parse_args()

    if args.undo:
        do_undo(args.undo)
        return

    vault = Path(args.vault or os.environ.get("OBSIDIAN_VAULT_PATH", "")).expanduser()
    if not vault.is_dir():
        sys.exit("Valid --vault PATH required (or set OBSIDIAN_VAULT_PATH).")

    if args.apply:
        do_apply(vault, args.days, args.max_files)
    else:
        do_dry_run(vault, args.days, args.max_files)


if __name__ == "__main__":
    main()
