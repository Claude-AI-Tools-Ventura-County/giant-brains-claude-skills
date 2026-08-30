#!/usr/bin/env python3
"""log_myriad.py — bulletproof append to the weekly MYRIAD parking-lot file.

Division of labor:
  - The LLM does the SEMANTIC work: decide which items are myriad, and rewrite
    each to a clean, actionable sentence (strip "I left this as a plan only..."
    preamble, keep only the action). It passes those clean items to this script.
  - This script does the MECHANICAL guarantees, so trust is deterministic rather
    than promised:
      * resolve the parking-lot directory: PDDA repos get PROJECT/2-WORKING/,
        everything else falls back to a repo-root 2-WORKING/ (detect, don't depend)
      * resolve the week file (Monday-of-week) so a whole week shares ONE file
      * fuzzy-dedup each item against everything already in the week file
      * safe read-modify-write — every existing line is preserved — via a temp
        file + os.replace (atomic; a crash mid-write cannot corrupt the file)
      * read the file back and VERIFY each item is on disk; exit non-zero if not

Items arrive on stdin, one per line (a leading "- [ ] " is optional), or via
repeated --item flags. A JSON receipt is printed to stdout.

Exit codes: 0 = ok (or dry-run / nothing-new), 2 = bad args, 3 = write happened
but read-back verification FAILED (caller must NOT report success).
"""
import argparse
import datetime
import difflib
import json
import os
import re
import sys
import tempfile

CHECKBOX_RE = re.compile(r'^\s*[-*]\s*\[[ xX]\]\s*(.+)$')
STRIP_BOX_RE = re.compile(r'^\s*[-*]\s*\[[ xX]\]\s*')
SECTION_RE = re.compile(r'^#{2,3}\s')


def normalize(s):
    s = STRIP_BOX_RE.sub('', s.strip())
    s = re.sub(r'\s+', ' ', s)
    return s.strip().lower()


def monday_of(d):
    return d - datetime.timedelta(days=d.weekday())


def find_project_root(start):
    """Walk up from `start` to the nearest git root. Falls back to `start` when
    there is no repo — the parking lot must work outside git too."""
    start = os.path.abspath(start)
    cur = start
    while True:
        if os.path.exists(os.path.join(cur, '.git')):  # dir, or file for worktrees
            return cur
        parent = os.path.dirname(cur)
        if parent == cur:
            return start
        cur = parent


def detect_pdda(root):
    """Detect a PDDA-governed repo. Returns (is_pdda, reason).

    Detection only — the skill never *requires* PDDA. A repo without it simply
    gets the repo-root fallback, so this helper behaves identically either way.
    """
    project = os.path.join(root, 'PROJECT')
    if not os.path.isdir(project):
        return False, 'no PROJECT/ directory'
    if os.path.isfile(os.path.join(project, 'PDDA.md')):
        return True, 'PROJECT/PDDA.md present'
    if os.path.isdir(os.path.join(project, '2-WORKING')):
        return True, 'PROJECT/2-WORKING/ present'
    return False, 'PROJECT/ exists but is not PDDA-shaped'


def resolve_work_dir(root, explicit):
    """Pick the parking-lot directory. Returns (path, is_pdda, reason)."""
    if explicit:
        return os.path.abspath(explicit), False, 'explicit --dir override'
    is_pdda, reason = detect_pdda(root)
    if is_pdda:
        return os.path.join(root, 'PROJECT', '2-WORKING'), True, 'PDDA detected (%s)' % reason
    return os.path.join(root, '2-WORKING'), False, 'no PDDA layout (%s)' % reason


def legacy_root_files(root, work_dir):
    """Week files stranded in a repo-root 2-WORKING/ after PDDA was adopted.
    Reported, never moved — relocating an operator's backlog is their call."""
    legacy = os.path.join(root, '2-WORKING')
    if os.path.abspath(legacy) == os.path.abspath(work_dir) or not os.path.isdir(legacy):
        return []
    return sorted(
        os.path.join(legacy, n) for n in os.listdir(legacy)
        if n.startswith('MYRIAD-WEEK-') and n.endswith('.md')
    )


def default_owner():
    for key in ('MYRIAD_OWNER', 'USER', 'USERNAME'):
        value = os.environ.get(key, '').strip()
        if value:
            return value
    return 'unknown'


def render_frontmatter(mon, today, owner):
    return (
        '---\n'
        f'title: Myriad — Week of {mon.isoformat()}\n'
        'status: Active (weekly myriad parking lot)\n'
        f'created: {today.isoformat()}\n'
        f'updated: {today.isoformat()}\n'
        f'owner: {owner}\n'
        'goal: >-\n'
        '  Park non-critical follow-up items from end-of-day agent triage in one\n'
        '  durable weekly backlog.\n'
        'doc_type: backlog\n'
        'roadmap_exempt: true\n'
        '---\n\n'
    )


def ensure_frontmatter(text, mon, today, owner):
    if text.lstrip().startswith('---'):
        return text
    return render_frontmatter(mon, today, owner) + text.lstrip('\n')


STATUS_TABLE = (
    '## Status\n\n'
    "| What was just completed | What's next |\n"
    '|---|---|\n'
    '| Parking lot opened for this week by `/myriad`. | Work off the open items below. This is a '
    '**parking lot, not a burndown** — `roadmap_exempt: true`, so no ROADMAP pointer is expected. '
    'Retire the file once every box is checked or reassigned. |\n'
)


def ensure_status_table(text):
    """PDDA repos require a '## Status' table in governed docs. Seed one so a
    week file lands compliant instead of tripping the check on first write.
    Only called when PDDA was detected — plain repos keep the leaner file."""
    if re.search(r'^##\s+Status\s*$', text, re.MULTILINE):
        return text
    lines = text.splitlines()
    # Insert after the H1 when there is one, else at the top.
    idx = next((i for i, ln in enumerate(lines) if ln.startswith('# ')), None)
    at = 0 if idx is None else idx + 1
    while at < len(lines) and lines[at].strip() == '':  # skip blanks already there
        at += 1
    block = STATUS_TABLE.rstrip('\n').splitlines() + ['']
    if at:
        block = [''] + block
    lines[at:at] = block
    return '\n'.join(lines) + '\n'


def existing_norms(text):
    out = []
    for line in text.splitlines():
        if CHECKBOX_RE.match(line):
            out.append(normalize(line))
    return out


def is_dup(cand_norm, norms, threshold):
    for e in norms:
        if cand_norm == e:
            return True
        if difflib.SequenceMatcher(None, cand_norm, e).ratio() >= threshold:
            return True
    return False


def build_new_text(text, date_str, new_items):
    """Insert new_items under the '### <date>' section, preserving every existing
    line. Creates the section at EOF if absent. Returns the full new text."""
    lines = text.splitlines()
    header = f'### {date_str}'
    add = [f'- [ ] {it}' for it in new_items]

    idx = next((i for i, ln in enumerate(lines) if ln.strip() == header), None)
    if idx is None:
        if lines and lines[-1].strip() != '':
            lines.append('')
        lines.append(header)
        lines.extend(add)
    else:
        j = idx + 1
        while j < len(lines) and not SECTION_RE.match(lines[j]):
            j += 1
        while j - 1 > idx and lines[j - 1].strip() == '':
            j -= 1
        lines[j:j] = add
    return '\n'.join(lines) + '\n'


def atomic_write(path, text):
    d = os.path.dirname(path) or '.'
    fd, tmp = tempfile.mkstemp(dir=d, prefix='.myriad-', suffix='.tmp')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(text)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def main():
    ap = argparse.ArgumentParser(description='Bulletproof append to the weekly MYRIAD file.')
    ap.add_argument('--root', help='Project root to resolve from (default: nearest git root, else cwd)')
    ap.add_argument('--dir', help='Explicit parking-lot directory; overrides --root auto-resolution')
    ap.add_argument('--date', help='Override today (YYYY-MM-DD); default = today')
    ap.add_argument('--threshold', type=float, default=0.85, help='Fuzzy-dedup similarity 0-1 (default 0.85)')
    ap.add_argument('--item', action='append', default=[], help='An item (repeatable); else read stdin')
    ap.add_argument('--dry-run', action='store_true', help='Preview only; write nothing')
    args = ap.parse_args()

    today = datetime.date.fromisoformat(args.date) if args.date else datetime.date.today()
    mon = monday_of(today)
    date_str = today.isoformat()
    owner = default_owner()

    raw = list(args.item)
    if not raw and not sys.stdin.isatty():
        raw = [l for l in sys.stdin.read().splitlines() if l.strip()]
    items = []
    for r in raw:
        it = STRIP_BOX_RE.sub('', r).strip()
        if it:
            items.append(it)

    root = os.path.abspath(args.root) if args.root else find_project_root(os.getcwd())
    work_dir, is_pdda, resolution = resolve_work_dir(root, args.dir)
    path = os.path.join(work_dir, f'MYRIAD-WEEK-{mon.isoformat()}.md')
    stranded = legacy_root_files(root, work_dir)

    if os.path.exists(path):
        with open(path, encoding='utf-8') as f:
            text = f.read()
    else:
        text = f'# Myriad — Week of {mon.isoformat()}\n'
    text = ensure_frontmatter(text, mon, today, owner)
    if is_pdda:
        text = ensure_status_table(text)

    norms = existing_norms(text)
    new_items, dupes = [], []
    for it in items:
        n = normalize(it)
        if is_dup(n, norms, args.threshold):
            dupes.append(it)
        else:
            new_items.append(it)
            norms.append(n)  # dedup within this batch too

    receipt = {
        'file': path,
        'project_root': root,
        'work_dir': work_dir,
        'pdda_detected': is_pdda,
        'resolution': resolution,
        'week_of': mon.isoformat(),
        'date': date_str,
        'logged': [],
        'skipped_duplicates': dupes,
        'dry_run': args.dry_run,
        'verified': False,
    }
    if stranded:
        receipt['stranded_legacy_files'] = stranded

    if not new_items:
        receipt['message'] = 'Nothing new to log (all duplicates or empty input).'
        print(json.dumps(receipt, indent=2))
        return 0

    new_text = build_new_text(text, date_str, new_items)

    if args.dry_run:
        receipt['logged'] = new_items
        receipt['message'] = f'DRY RUN — would log {len(new_items)}, skip {len(dupes)} dupe(s). Nothing written.'
        print(json.dumps(receipt, indent=2))
        return 0

    os.makedirs(work_dir, exist_ok=True)
    atomic_write(path, new_text)

    with open(path, encoding='utf-8') as f:
        disk = set(existing_norms(f.read()))
    missing = [it for it in new_items if normalize(it) not in disk]
    if missing:
        receipt['logged'] = [it for it in new_items if it not in missing]
        receipt['missing'] = missing
        receipt['message'] = 'FAILED verification — some items are NOT on disk. Do not report success.'
        print(json.dumps(receipt, indent=2))
        return 3

    receipt['logged'] = new_items
    receipt['verified'] = True
    receipt['message'] = (f'Logged {len(new_items)} new item(s), skipped {len(dupes)} '
                          f'duplicate(s), all verified on disk.')
    print(json.dumps(receipt, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
