#!/usr/bin/env python3
"""Deterministic session logger for the BTW Claude Code skill.

The script owns all persistent state for a BTW focus session. It creates one
append-only Markdown file per BTW session, keeps a small active-session pointer
outside the repository, and emits machine-readable JSON only.
"""

from __future__ import annotations

import argparse
import base64
import contextlib
import datetime as dt
import hashlib
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Optional, Sequence, Tuple

VERSION = "1.0.0"
SCHEMA_VERSION = 1
CATEGORY_LABELS = {
    "action": "ACTION",
    "review": "REVIEW",
    "interesting": "INTERESTING",
}
SESSION_META_RE = re.compile(r"<!-- BTW-SESSION ([A-Za-z0-9_-]+) -->")
EVENT_META_RE = re.compile(r"<!-- BTW-META ([A-Za-z0-9_-]+) -->")


class BtwError(RuntimeError):
    """Expected operational error surfaced as compact JSON."""


# ------------------------------- serialization ------------------------------


def _json_bytes(value: Dict[str, Any]) -> bytes:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")


def _encode_meta(value: Dict[str, Any]) -> str:
    return base64.urlsafe_b64encode(_json_bytes(value)).decode("ascii").rstrip("=")


def _decode_meta(value: str) -> Dict[str, Any]:
    padding = "=" * (-len(value) % 4)
    raw = base64.urlsafe_b64decode(value + padding)
    parsed = json.loads(raw.decode("utf-8"))
    if not isinstance(parsed, dict):
        raise BtwError("Invalid BTW metadata object")
    return parsed


def _emit(payload: Dict[str, Any], *, exit_code: int = 0) -> int:
    print(json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True))
    return exit_code


def _read_json_stdin() -> Any:
    raw = sys.stdin.read()
    if not raw.strip():
        raise BtwError("Expected JSON on stdin")
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise BtwError(f"Invalid JSON on stdin: {exc.msg} at line {exc.lineno}, column {exc.colno}") from exc


# --------------------------------- time/text --------------------------------


def _now() -> Tuple[dt.datetime, dt.datetime]:
    local = dt.datetime.now().astimezone()
    utc = local.astimezone(dt.timezone.utc)
    return local, utc


def _iso_seconds(value: dt.datetime) -> str:
    return value.isoformat(timespec="seconds")


def _filename_stamp(value: dt.datetime) -> str:
    return value.strftime("%Y-%m-%dT%H%M%S")


def _one_line(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _slug(value: str, *, limit: int = 48) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip())
    cleaned = re.sub(r"-+", "-", cleaned).strip("-._")
    return (cleaned or "unknown")[:limit]


def _inline_code(value: str) -> str:
    # Git ref names cannot normally contain backticks, but normalize defensively.
    return "`" + value.replace("`", "'") + "`"


def _fenced_text(value: str) -> str:
    value = value.rstrip("\n")
    longest = max((len(match.group(0)) for match in re.finditer(r"`+", value)), default=0)
    fence = "`" * max(3, longest + 1)
    return f"{fence}text\n{value}\n{fence}"


_SECRET_PATTERNS: Sequence[Tuple[re.Pattern[str], str]] = (
    (re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----.*?-----END (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----", re.DOTALL), "[REDACTED: PRIVATE KEY]"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "[REDACTED: AWS ACCESS KEY]"),
    (re.compile(r"\bASIA[0-9A-Z]{16}\b"), "[REDACTED: AWS TEMP ACCESS KEY]"),
    (re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"), "[REDACTED: GITHUB TOKEN]"),
    (re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b"), "[REDACTED: GITHUB TOKEN]"),
    (re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}\b"), "[REDACTED: ANTHROPIC KEY]"),
    (re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{24,}\b"), "[REDACTED: API KEY]"),
    (re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b"), "[REDACTED: SLACK TOKEN]"),
    (re.compile(r"(?i)\bAuthorization\s*:\s*Bearer\s+[A-Za-z0-9._~+/=-]{12,}"), "Authorization: Bearer [REDACTED]"),
)
_GENERIC_SECRET_RE = re.compile(
    r"(?i)\b(api[_-]?key|access[_-]?token|auth[_-]?token|client[_-]?secret|secret|password)"
    r"(\s*[:=]\s*)([\"']?)([^\s\"']{12,})([\"']?)"
)


def _redact_sensitive(value: str) -> Tuple[str, int]:
    redacted = value
    count = 0
    for pattern, replacement in _SECRET_PATTERNS:
        redacted, substitutions = pattern.subn(replacement, redacted)
        count += substitutions

    def replace_generic(match: re.Match[str]) -> str:
        nonlocal count
        count += 1
        quote = match.group(3) if match.group(3) == match.group(5) else ""
        return f"{match.group(1)}{match.group(2)}{quote}[REDACTED]{quote}"

    redacted = _GENERIC_SECRET_RE.sub(replace_generic, redacted)
    return redacted, count


# -------------------------------- git context --------------------------------


def _run_git(args: Sequence[str], cwd: Path) -> Tuple[int, str]:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=str(cwd),
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    except FileNotFoundError:
        return 127, ""
    return completed.returncode, completed.stdout.strip()


def _repo_name_from_origin(origin: str) -> Optional[str]:
    if not origin:
        return None
    candidate = origin.rstrip("/")
    if ":" in candidate and "/" not in candidate.split(":", 1)[0]:
        candidate = candidate.rsplit(":", 1)[-1]
    candidate = candidate.rsplit("/", 1)[-1]
    if candidate.endswith(".git"):
        candidate = candidate[:-4]
    return candidate or None


def _git_context(project_dir: Path) -> Dict[str, Any]:
    project_dir = project_dir.expanduser().resolve()
    code, root_text = _run_git(["rev-parse", "--show-toplevel"], project_dir)
    if code != 0 or not root_text:
        return {
            "git_repository": False,
            "root": project_dir,
            "repo": project_dir.name or "project",
            "branch": "not-a-git-repository",
            "commit": "n/a",
        }

    root = Path(root_text).resolve()
    _, origin = _run_git(["config", "--get", "remote.origin.url"], root)
    repo = _repo_name_from_origin(origin) or root.name or "repository"

    branch_code, branch = _run_git(["symbolic-ref", "--quiet", "--short", "HEAD"], root)
    commit_code, commit = _run_git(["rev-parse", "--short=12", "HEAD"], root)
    if branch_code != 0 or not branch:
        branch = f"detached@{commit}" if commit_code == 0 and commit else "unborn"
    if commit_code != 0 or not commit:
        commit = "unborn"

    return {
        "git_repository": True,
        "root": root,
        "repo": repo,
        "branch": branch,
        "commit": commit,
    }


def _is_ignored(root: Path, relative_path: Path) -> Optional[bool]:
    code, _ = _run_git(["check-ignore", "-q", "--no-index", "--", relative_path.as_posix()], root)
    if code == 0:
        return True
    if code == 1:
        return False
    return None


# -------------------------------- state files --------------------------------


def _state_home() -> Path:
    override = os.environ.get("BTW_STATE_HOME")
    if override:
        return Path(override).expanduser().resolve()
    if os.name == "nt":
        base = os.environ.get("LOCALAPPDATA")
        if base:
            return Path(base) / "claude-btw" / "state"
    base = os.environ.get("XDG_STATE_HOME")
    if base:
        return Path(base).expanduser() / "claude-btw"
    return Path.home() / ".local" / "state" / "claude-btw"


def _state_path(root: Path, claude_session_id: str) -> Path:
    project_key = hashlib.sha256(str(root).encode("utf-8")).hexdigest()[:16]
    session_key = hashlib.sha256(claude_session_id.encode("utf-8")).hexdigest()[:24]
    return _state_home() / project_key / f"{session_key}.json"


def _atomic_write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.chmod(temporary, 0o600)
        except OSError:
            pass
        os.replace(temporary, path)
    finally:
        with contextlib.suppress(FileNotFoundError):
            os.unlink(temporary)


def _load_state(root: Path, claude_session_id: str) -> Optional[Dict[str, Any]]:
    path = _state_path(root, claude_session_id)
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None
    return parsed if isinstance(parsed, dict) else None


def _save_state(root: Path, claude_session_id: str, log_path: Path, *, ended: bool) -> None:
    _atomic_write_json(
        _state_path(root, claude_session_id),
        {
            "schema_version": SCHEMA_VERSION,
            "claude_session_id": claude_session_id,
            "project_root": str(root),
            "log_path": str(log_path),
            "ended": ended,
            "updated_utc": _iso_seconds(_now()[1]),
        },
    )


# ------------------------------- log metadata --------------------------------


def _read_metadata(path: Path) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise BtwError(f"Cannot read BTW log {path}: {exc}") from exc

    session_match = SESSION_META_RE.search(text)
    if not session_match:
        raise BtwError(f"BTW log is missing session metadata: {path}")
    session = _decode_meta(session_match.group(1))
    events = [_decode_meta(match.group(1)) for match in EVENT_META_RE.finditer(text)]
    return session, events


def _relative_log_path(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.name


def _status_from_path(root: Path, path: Path) -> Dict[str, Any]:
    session, events = _read_metadata(path)
    focus: List[str] = []
    allow_git_writes = False
    branch_logged = session.get("branch_at_start", "unknown")
    ended = False
    completed: List[str] = []
    open_items: List[str] = []
    counts = {"action": 0, "review": 0, "interesting": 0}
    redactions = int(session.get("redactions", 0))

    for event in events:
        event_type = event.get("type")
        redactions += int(event.get("redactions", 0) or 0)
        if event_type == "focus":
            focus = list(event.get("items") or [])
            allow_git_writes = bool(event.get("allow_git_writes", False))
        elif event_type == "context" and event.get("branch"):
            branch_logged = str(event["branch"])
        elif event_type == "park":
            category = event.get("category")
            if category in counts:
                counts[category] += 1
        elif event_type == "end":
            ended = True
            completed = list(event.get("completed") or [])
            open_items = list(event.get("open") or [])

    return {
        "active": not ended,
        "allow_git_writes": allow_git_writes,
        "branch_at_start": session.get("branch_at_start", "unknown"),
        "branch_logged": branch_logged,
        "btw_session_id": session.get("btw_session_id"),
        "claude_session_id": session.get("claude_session_id"),
        "commit_at_start": session.get("commit_at_start", "unknown"),
        "completed": completed,
        "counts": {**counts, "total": sum(counts.values())},
        "ended": ended,
        "file": _relative_log_path(root, path),
        "focus": focus,
        "git_repository": bool(session.get("git_repository")),
        "open": open_items,
        "redactions": redactions,
        "repo": session.get("repo", root.name),
        "started_local": session.get("started_local"),
        "started_utc": session.get("started_utc"),
    }


def _recover_active_log(root: Path, claude_session_id: str) -> Optional[Path]:
    btw_dir = root / "BTW"
    if not btw_dir.is_dir():
        return None
    candidates = sorted(btw_dir.glob("*.md"), key=lambda path: path.stat().st_mtime, reverse=True)
    for candidate in candidates:
        try:
            session, _ = _read_metadata(candidate)
            status = _status_from_path(root, candidate)
        except (BtwError, OSError):
            continue
        if session.get("claude_session_id") == claude_session_id and not status["ended"]:
            _save_state(root, claude_session_id, candidate, ended=False)
            return candidate
    return None


def _active_log(root: Path, claude_session_id: str, *, allow_ended: bool = False) -> Optional[Path]:
    state = _load_state(root, claude_session_id)
    if state:
        candidate = Path(str(state.get("log_path", ""))).expanduser()
        if candidate.is_file():
            try:
                status = _status_from_path(root, candidate)
            except BtwError:
                status = None
            if status and (allow_ended or not status["ended"]):
                return candidate
    if allow_ended:
        return None
    return _recover_active_log(root, claude_session_id)


# -------------------------------- file writes --------------------------------


@contextlib.contextmanager
def _locked_append(path: Path) -> Iterator[Any]:
    try:
        handle = path.open("a+", encoding="utf-8", newline="\n")
    except OSError as exc:
        raise BtwError(f"Cannot open BTW log for append: {exc}") from exc
    try:
        if os.name != "nt":
            try:
                import fcntl  # type: ignore

                fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            except (ImportError, OSError):
                pass
        yield handle
    finally:
        if os.name != "nt":
            with contextlib.suppress(Exception):
                import fcntl  # type: ignore

                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        handle.close()


def _append_event(path: Path, visible: str, meta: Dict[str, Any]) -> Dict[str, Any]:
    local, utc = _now()
    payload = dict(meta)
    payload.setdefault("event_id", uuid.uuid4().hex[:12])
    payload.setdefault("local_time", _iso_seconds(local))
    payload.setdefault("utc_time", _iso_seconds(utc))
    encoded = _encode_meta(payload)
    line = f"- [{payload['local_time']}] [{payload.get('label', str(payload.get('type', 'EVENT')).upper())}] {visible} <!-- BTW-META {encoded} -->\n"

    with _locked_append(path) as handle:
        handle.seek(0, os.SEEK_END)
        if handle.tell() and not _file_ends_with_newline(handle):
            handle.write("\n")
        handle.write(line)
        handle.flush()
        os.fsync(handle.fileno())
        handle.seek(0)
        if encoded not in handle.read():
            raise BtwError("BTW log write could not be verified")
    return payload


def _file_ends_with_newline(handle: Any) -> bool:
    position = handle.tell()
    if position == 0:
        return True
    handle.seek(position - 1)
    last = handle.read(1)
    handle.seek(position)
    return last == "\n"


def _sync_branch(root: Path, path: Path) -> int:
    status = _status_from_path(root, path)
    current = _git_context(root)["branch"]
    if current == status["branch_logged"]:
        return 0
    _append_event(
        path,
        f"Active branch changed from {_inline_code(str(status['branch_logged']))} to {_inline_code(str(current))}.",
        {
            "type": "context",
            "label": "CONTEXT",
            "branch": current,
            "previous_branch": status["branch_logged"],
        },
    )
    return 1


def _normalize_repo_path(root: Path, raw: Any) -> Optional[str]:
    value = _one_line(raw)
    if not value or value.lower() in {"n/a", "none", "null"}:
        return None
    candidate = Path(value).expanduser()
    if candidate.is_absolute():
        resolved = candidate.resolve()
    else:
        resolved = (root / candidate).resolve()
    try:
        relative = resolved.relative_to(root.resolve())
    except ValueError as exc:
        raise BtwError(f"Parked-item path must be inside the project root or omitted: {value}") from exc
    return relative.as_posix()


def _fingerprint(*parts: str) -> str:
    material = "\0".join(part.casefold().strip() for part in parts)
    return hashlib.sha256(material.encode("utf-8")).hexdigest()[:20]


# --------------------------------- commands ----------------------------------


def _resolve_context(args: argparse.Namespace) -> Tuple[str, Dict[str, Any]]:
    claude_session_id = (args.claude_session_id or os.environ.get("CLAUDE_SESSION_ID") or "").strip()
    if not claude_session_id:
        raise BtwError("Claude session ID is required; pass --claude-session-id or set CLAUDE_SESSION_ID")
    project = Path(args.project_dir or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
    context = _git_context(project)
    return claude_session_id, context


def _create_log(root: Path, context: Dict[str, Any], claude_session_id: str, prompt: str) -> Tuple[Path, Dict[str, Any]]:
    local, utc = _now()
    prompt, redactions = _redact_sensitive(prompt.rstrip("\n"))
    if not prompt.strip():
        raise BtwError("The opening user prompt is empty; pass it on stdin")

    btw_session_id = f"{_filename_stamp(local)}-{uuid.uuid4().hex[:8]}"
    repo_slug = _slug(str(context["repo"]), limit=36)
    branch_slug = _slug(str(context["branch"]), limit=36)
    session_slug = hashlib.sha256(btw_session_id.encode("utf-8")).hexdigest()[:8]
    btw_dir = root / "BTW"
    btw_dir.mkdir(parents=True, exist_ok=True)
    base = f"{_filename_stamp(local)}-{repo_slug}-{branch_slug}-{session_slug}"
    path = btw_dir / f"{base}.md"
    suffix = 2
    while path.exists():
        path = btw_dir / f"{base}-{suffix}.md"
        suffix += 1

    session_meta = {
        "schema_version": SCHEMA_VERSION,
        "btw_session_id": btw_session_id,
        "claude_session_id": claude_session_id,
        "started_local": _iso_seconds(local),
        "started_utc": _iso_seconds(utc),
        "repo": context["repo"],
        "branch_at_start": context["branch"],
        "commit_at_start": context["commit"],
        "git_repository": context["git_repository"],
        "redactions": redactions,
    }
    start_event = {
        "type": "start",
        "label": "START",
        "event_id": uuid.uuid4().hex[:12],
        "local_time": _iso_seconds(local),
        "utc_time": _iso_seconds(utc),
    }
    content = (
        f"# BTW Session — {context['repo']} @ {context['branch']}\n\n"
        "## Context\n\n"
        f"- BTW session: {_inline_code(btw_session_id)}\n"
        f"- Claude session: {_inline_code(claude_session_id)}\n"
        f"- Started (local): {_inline_code(_iso_seconds(local))}\n"
        f"- Started (UTC): {_inline_code(_iso_seconds(utc))}\n"
        f"- Repository: {_inline_code(str(context['repo']))}\n"
        f"- Active branch at start: {_inline_code(str(context['branch']))}\n"
        f"- Commit at start: {_inline_code(str(context['commit']))}\n"
        f"- Focus at start: pending declaration\n\n"
        "## Opening user prompt\n\n"
        f"{_fenced_text(prompt)}\n\n"
        "## Timeline\n\n"
        f"- [{start_event['local_time']}] [START] Session initialized. <!-- BTW-META {_encode_meta(start_event)} -->\n\n"
        f"<!-- BTW-SESSION {_encode_meta(session_meta)} -->\n"
    )

    try:
        with path.open("x", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
    except OSError as exc:
        raise BtwError(f"Cannot create BTW log {path}: {exc}") from exc

    try:
        session_check, _ = _read_metadata(path)
    except BtwError:
        with contextlib.suppress(OSError):
            path.unlink()
        raise
    if session_check.get("btw_session_id") != btw_session_id:
        with contextlib.suppress(OSError):
            path.unlink()
        raise BtwError("BTW log creation could not be verified")
    return path, session_meta


def _end_path(
    root: Path,
    path: Path,
    *,
    completed: List[str],
    open_items: List[str],
    reason: Optional[str] = None,
    redactions: int = 0,
) -> Dict[str, Any]:
    status = _status_from_path(root, path)
    if status["ended"]:
        return status
    visible_parts = []
    if reason:
        visible_parts.append(reason)
    visible_parts.append("Completed: " + ("; ".join(completed) if completed else "none declared"))
    visible_parts.append("Open: " + ("; ".join(open_items) if open_items else "none"))
    _append_event(
        path,
        "; ".join(visible_parts) + ".",
        {
            "type": "end",
            "label": "END",
            "completed": completed,
            "open": open_items,
            "reason": reason,
            "redactions": redactions,
        },
    )
    return _status_from_path(root, path)


def command_start(args: argparse.Namespace) -> Dict[str, Any]:
    claude_session_id, context = _resolve_context(args)
    root = Path(context["root"])
    existing = _active_log(root, claude_session_id)
    if existing and not args.new:
        status = _status_from_path(root, existing)
        status.update({"ok": True, "command": "start", "created": False, "warning": None})
        return status

    if existing and args.new:
        old_status = _end_path(root, existing, completed=[], open_items=_status_from_path(root, existing)["focus"], reason="Superseded by a new BTW session")
        _save_state(root, claude_session_id, existing, ended=True)
        del old_status

    prompt = sys.stdin.read()
    path, session_meta = _create_log(root, context, claude_session_id, prompt)
    _save_state(root, claude_session_id, path, ended=False)
    status = _status_from_path(root, path)

    ignored: Optional[bool] = None
    warning: Optional[str] = None
    if context["git_repository"]:
        ignored = _is_ignored(root, path.relative_to(root))
        if ignored is False:
            warning = "BTW/ is not ignored and may be included by broad staging commands such as git add -A."
    status.update(
        {
            "ok": True,
            "command": "start",
            "created": True,
            "git_ignored": ignored,
            "redactions": session_meta["redactions"],
            "warning": warning,
        }
    )
    return status


def _parse_focus_payload(payload: Any) -> Tuple[List[str], bool, int]:
    if isinstance(payload, list):
        items = payload
        allow_git_writes = False
    elif isinstance(payload, dict):
        items = payload.get("items")
        allow_git_writes = bool(payload.get("allow_git_writes", False))
    else:
        raise BtwError("Focus payload must be a JSON array or an object with an items array")
    if not isinstance(items, list):
        raise BtwError("Focus items must be a JSON array")
    cleaned: List[str] = []
    redactions = 0
    for raw in items:
        item, item_redactions = _redact_sensitive(_one_line(raw))
        redactions += item_redactions
        if item:
            cleaned.append(item)
    if not 1 <= len(cleaned) <= 3:
        raise BtwError("A BTW session requires 1 to 3 non-empty focus items")
    if len(set(value.casefold() for value in cleaned)) != len(cleaned):
        raise BtwError("Focus items must be distinct")
    return cleaned, allow_git_writes, redactions


def command_focus(args: argparse.Namespace) -> Dict[str, Any]:
    claude_session_id, context = _resolve_context(args)
    root = Path(context["root"])
    path = _active_log(root, claude_session_id)
    if not path:
        raise BtwError("No active BTW session; invoke /btw first")
    items, allow_git_writes, redactions = _parse_focus_payload(_read_json_stdin())
    branch_events = _sync_branch(root, path)
    status = _status_from_path(root, path)
    if status["focus"] == items and status["allow_git_writes"] == allow_git_writes:
        status.update({"ok": True, "command": "focus", "changed": False, "context_events_written": branch_events})
        return status
    action = "Set" if not status["focus"] else "Updated"
    display = " ".join(f"{index}) {item}" for index, item in enumerate(items, start=1))
    _append_event(
        path,
        f"{action}: {display}. Git writes explicitly allowed: {'yes' if allow_git_writes else 'no'}.",
        {
            "type": "focus",
            "label": "FOCUS",
            "items": items,
            "allow_git_writes": allow_git_writes,
            "redactions": redactions,
        },
    )
    status = _status_from_path(root, path)
    status.update({"ok": True, "command": "focus", "changed": True, "context_events_written": branch_events})
    return status


def _parse_park_payload(root: Path, payload: Any) -> List[Dict[str, Any]]:
    entries = payload.get("entries") if isinstance(payload, dict) and "entries" in payload else payload
    if not isinstance(entries, list) or not entries:
        raise BtwError("Park payload must be a non-empty JSON array or an object with an entries array")
    normalized: List[Dict[str, Any]] = []
    for index, raw in enumerate(entries, start=1):
        if not isinstance(raw, dict):
            raise BtwError(f"Park entry {index} must be a JSON object")
        category = _one_line(raw.get("category")).lower().replace(" ", "-")
        aliases = {"action-item": "action", "review-later": "review", "interesting-item": "interesting"}
        category = aliases.get(category, category)
        if category not in CATEGORY_LABELS:
            raise BtwError(f"Park entry {index} has invalid category: {category}")
        finding, finding_redactions = _redact_sensitive(_one_line(raw.get("finding")))
        why, why_redactions = _redact_sensitive(_one_line(raw.get("why") or raw.get("impact") or raw.get("context")))
        evidence, evidence_redactions = _redact_sensitive(_one_line(raw.get("evidence")))
        if not finding:
            raise BtwError(f"Park entry {index} is missing finding")
        if not why:
            raise BtwError(f"Park entry {index} is missing why/impact/context")
        path = _normalize_repo_path(root, raw.get("path"))
        normalized.append(
            {
                "category": category,
                "finding": finding,
                "why": why,
                "evidence": evidence or None,
                "path": path,
                "redactions": finding_redactions + why_redactions + evidence_redactions,
            }
        )
    return normalized


def command_park(args: argparse.Namespace) -> Dict[str, Any]:
    claude_session_id, context = _resolve_context(args)
    root = Path(context["root"])
    path = _active_log(root, claude_session_id)
    if not path:
        raise BtwError("No active BTW session; invoke /btw first")
    entries = _parse_park_payload(root, _read_json_stdin())
    branch_events = _sync_branch(root, path)
    _, existing_events = _read_metadata(path)
    prior_by_identity: Dict[str, List[Dict[str, Any]]] = {}
    prior_details = set()
    for event in existing_events:
        if event.get("type") != "park":
            continue
        identity = event.get("identity_fingerprint")
        detail = event.get("detail_fingerprint")
        if identity:
            prior_by_identity.setdefault(str(identity), []).append(event)
        if detail:
            prior_details.add(str(detail))

    written = 0
    duplicates = 0
    updates = 0
    redactions = 0
    for entry in entries:
        identity = _fingerprint(entry["category"], entry["finding"], entry["path"] or "")
        detail = _fingerprint(identity, entry["why"], entry["evidence"] or "")
        if detail in prior_details:
            duplicates += 1
            continue
        update_of = None
        if identity in prior_by_identity and prior_by_identity[identity]:
            update_of = prior_by_identity[identity][-1].get("event_id")
            updates += 1
        parts = [entry["finding"], f"why: {entry['why']}"]
        if entry["evidence"]:
            parts.append(f"evidence: {entry['evidence']}")
        parts.append(f"path: {entry['path'] or 'n/a'}")
        if update_of:
            parts.insert(0, f"Update to {update_of}")
        event = _append_event(
            path,
            " — ".join(parts) + ".",
            {
                "type": "park",
                "label": CATEGORY_LABELS[entry["category"]],
                "category": entry["category"],
                "finding": entry["finding"],
                "why": entry["why"],
                "evidence": entry["evidence"],
                "path": entry["path"],
                "identity_fingerprint": identity,
                "detail_fingerprint": detail,
                "update_of": update_of,
                "redactions": entry["redactions"],
            },
        )
        prior_by_identity.setdefault(identity, []).append(event)
        prior_details.add(detail)
        written += 1
        redactions += entry["redactions"]

    status = _status_from_path(root, path)
    status.update(
        {
            "ok": True,
            "command": "park",
            "written": written,
            "duplicates_skipped": duplicates,
            "updates_written": updates,
            "redactions_this_call": redactions,
            "context_events_written": branch_events,
        }
    )
    return status


def command_status(args: argparse.Namespace) -> Dict[str, Any]:
    claude_session_id, context = _resolve_context(args)
    root = Path(context["root"])
    path = _active_log(root, claude_session_id)
    if not path:
        raise BtwError("No active BTW session; invoke /btw first")
    branch_events = 0 if args.no_sync_context else _sync_branch(root, path)
    status = _status_from_path(root, path)
    status["current_branch"] = _git_context(root)["branch"]
    status.update({"ok": True, "command": "status", "context_events_written": branch_events})
    return status


def command_show(args: argparse.Namespace) -> Dict[str, Any]:
    claude_session_id, context = _resolve_context(args)
    root = Path(context["root"])
    path = _active_log(root, claude_session_id)
    if not path:
        raise BtwError("No active BTW session; invoke /btw first")
    branch_events = 0 if args.no_sync_context else _sync_branch(root, path)
    _, events = _read_metadata(path)
    selected = []
    for event in events:
        if event.get("type") != "park":
            continue
        if args.category and event.get("category") != args.category:
            continue
        selected.append(
            {
                key: event.get(key)
                for key in (
                    "event_id",
                    "local_time",
                    "category",
                    "finding",
                    "why",
                    "evidence",
                    "path",
                    "update_of",
                )
            }
        )
    status = _status_from_path(root, path)
    status.update({"ok": True, "command": "show", "entries": selected, "context_events_written": branch_events})
    return status


def _clean_string_list(value: Any, field: str) -> Tuple[List[str], int]:
    if value is None:
        return [], 0
    if not isinstance(value, list):
        raise BtwError(f"{field} must be a JSON array")
    result: List[str] = []
    redactions = 0
    for raw in value:
        text, item_redactions = _redact_sensitive(_one_line(raw))
        redactions += item_redactions
        if text:
            result.append(text)
    return result, redactions


def command_end(args: argparse.Namespace) -> Dict[str, Any]:
    claude_session_id, context = _resolve_context(args)
    root = Path(context["root"])
    path = _active_log(root, claude_session_id)
    if not path:
        raise BtwError("No active BTW session; invoke /btw first")
    payload = _read_json_stdin()
    if not isinstance(payload, dict):
        raise BtwError("End payload must be a JSON object")
    completed, completed_redactions = _clean_string_list(payload.get("completed"), "completed")
    open_items, open_redactions = _clean_string_list(payload.get("open"), "open")
    branch_events = _sync_branch(root, path)
    status = _end_path(
        root,
        path,
        completed=completed,
        open_items=open_items,
        redactions=completed_redactions + open_redactions,
    )
    _save_state(root, claude_session_id, path, ended=True)
    status.update({"ok": True, "command": "end", "context_events_written": branch_events})
    return status


# ----------------------------- optional git guard -----------------------------


_READ_ONLY_GIT = {
    "annotate",
    "blame",
    "cat-file",
    "check-attr",
    "check-ignore",
    "check-mailmap",
    "cherry",
    "count-objects",
    "describe",
    "diff",
    "diff-files",
    "diff-index",
    "diff-tree",
    "for-each-ref",
    "fsck",
    "grep",
    "help",
    "log",
    "ls-files",
    "ls-remote",
    "ls-tree",
    "merge-base",
    "name-rev",
    "rev-list",
    "rev-parse",
    "show",
    "show-branch",
    "shortlog",
    "status",
    "verify-commit",
    "verify-pack",
    "verify-tag",
    "version",
    "whatchanged",
}
_GIT_GLOBAL_OPTIONS_WITH_VALUE = {
    "-C",
    "-c",
    "--git-dir",
    "--work-tree",
    "--namespace",
    "--super-prefix",
    "--config-env",
    "--exec-path",
}


def _git_invocations(command: str) -> List[List[str]]:
    try:
        lexer = shlex.shlex(command, posix=True, punctuation_chars=";&|")
        lexer.whitespace_split = True
        lexer.commenters = ""
        tokens = list(lexer)
    except ValueError:
        return [["<unparsed>"]]
    invocations: List[List[str]] = []
    separators = {";", "&&", "||", "|", "&"}
    index = 0
    while index < len(tokens):
        if tokens[index] != "git":
            index += 1
            continue
        segment: List[str] = ["git"]
        index += 1
        while index < len(tokens) and tokens[index] not in separators:
            segment.append(tokens[index])
            index += 1
        invocations.append(segment)
    return invocations


def _git_subcommand(tokens: List[str]) -> Tuple[str, List[str]]:
    if tokens == ["<unparsed>"]:
        return "<unparsed>", []
    index = 1
    while index < len(tokens):
        token = tokens[index]
        if token in _GIT_GLOBAL_OPTIONS_WITH_VALUE:
            index += 2
            continue
        if any(token.startswith(prefix + "=") for prefix in _GIT_GLOBAL_OPTIONS_WITH_VALUE if prefix.startswith("--")):
            index += 1
            continue
        if token.startswith("-C") and token != "-C":
            index += 1
            continue
        if token.startswith("-c") and token != "-c":
            index += 1
            continue
        if token.startswith("-"):
            index += 1
            continue
        return token, tokens[index + 1 :]
    return "", []


def _is_read_only_git(tokens: List[str]) -> bool:
    subcommand, rest = _git_subcommand(tokens)
    if subcommand in _READ_ONLY_GIT:
        return True
    if subcommand in {"", "<unparsed>"}:
        return False
    if subcommand == "branch":
        if not rest:
            return True
        first = rest[0]
        return first in {"--show-current", "--list", "--all", "--remotes", "-a", "-r", "-v", "-vv"}
    if subcommand == "remote":
        return not rest or rest[0] in {"-v", "--verbose", "show", "get-url"}
    if subcommand == "config":
        safe = {"--get", "--get-all", "--get-regexp", "--list", "-l", "--show-origin", "--show-scope", "--get-urlmatch"}
        return bool(rest) and rest[0] in safe
    if subcommand == "tag":
        return not rest or rest[0] in {"--list", "-l", "--contains", "--no-contains", "--points-at", "--merged", "--no-merged"}
    if subcommand == "worktree":
        return bool(rest) and rest[0] == "list"
    if subcommand == "stash":
        return bool(rest) and rest[0] in {"list", "show"}
    if subcommand == "reflog":
        return not rest or rest[0] in {"show", "exists"}
    if subcommand == "submodule":
        return bool(rest) and rest[0] in {"status", "summary"}
    if subcommand == "lfs":
        return bool(rest) and rest[0] in {"status", "ls-files", "env"}
    return False


def command_guard_git_hook(_: argparse.Namespace) -> Optional[Dict[str, Any]]:
    payload = _read_json_stdin()
    if not isinstance(payload, dict):
        return None
    if payload.get("tool_name") != "Bash":
        return None
    tool_input = payload.get("tool_input") or {}
    if not isinstance(tool_input, dict):
        return None
    command = str(tool_input.get("command") or "")
    invocations = _git_invocations(command)
    if not invocations:
        return None

    claude_session_id = str(payload.get("session_id") or "").strip()
    cwd = Path(str(payload.get("cwd") or os.getcwd()))
    if not claude_session_id:
        return None
    context = _git_context(cwd)
    root = Path(context["root"])
    path = _active_log(root, claude_session_id)
    if not path:
        return None
    status = _status_from_path(root, path)
    if status["allow_git_writes"]:
        return None

    blocked = []
    for invocation in invocations:
        if not _is_read_only_git(invocation):
            blocked.append(" ".join(invocation[:4]))
    if not blocked:
        return None
    reason = (
        "BTW focus mode blocks mutating or unrecognized Git commands unless a declared focus item explicitly enables Git writes. "
        f"Blocked: {', '.join(blocked)}"
    )
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }


# ----------------------------------- CLI -------------------------------------


def _add_context_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--claude-session-id", help="Claude Code session ID; defaults to CLAUDE_SESSION_ID")
    parser.add_argument("--project-dir", help="Project directory; defaults to CLAUDE_PROJECT_DIR or cwd")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="BTW session attention-firewall helper")
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    start = subparsers.add_parser("start", help="Create or re-open the active BTW session; opening prompt is read from stdin")
    _add_context_args(start)
    start.add_argument("--new", action="store_true", help="Close an active BTW session and create a new one")
    start.set_defaults(handler=command_start)

    focus = subparsers.add_parser("focus", help="Set or update 1-3 focus items from JSON on stdin")
    _add_context_args(focus)
    focus.set_defaults(handler=command_focus)

    park = subparsers.add_parser("park", help="Append one or more triaged observations from JSON on stdin")
    _add_context_args(park)
    park.set_defaults(handler=command_park)

    status = subparsers.add_parser("status", help="Return active session state and counts")
    _add_context_args(status)
    status.add_argument("--no-sync-context", action="store_true", help="Do not append a branch-change context event")
    status.set_defaults(handler=command_status)

    show = subparsers.add_parser("show", help="Return parked entries; use only when the user asks to review them")
    _add_context_args(show)
    show.add_argument("--category", choices=sorted(CATEGORY_LABELS), help="Filter by category")
    show.add_argument("--no-sync-context", action="store_true", help="Do not append a branch-change context event")
    show.set_defaults(handler=command_show)

    end = subparsers.add_parser("end", help="Close the active BTW session from JSON on stdin")
    _add_context_args(end)
    end.set_defaults(handler=command_end)

    guard = subparsers.add_parser("guard-git-hook", help="Optional PreToolUse hook for read-only Git enforcement")
    guard.set_defaults(handler=command_guard_git_hook)
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = args.handler(args)
        if result is None:
            return 0
        return _emit(result)
    except BtwError as exc:
        return _emit({"ok": False, "error": str(exc), "command": getattr(args, "command", None)}, exit_code=2)
    except Exception as exc:  # Defensive: never leak a traceback into Claude's normal tool output.
        return _emit(
            {"ok": False, "error": f"Unexpected helper failure: {type(exc).__name__}: {exc}", "command": getattr(args, "command", None)},
            exit_code=3,
        )


if __name__ == "__main__":
    raise SystemExit(main())
