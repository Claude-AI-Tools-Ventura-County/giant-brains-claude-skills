#!/usr/bin/env bash
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONF="$SCRIPT_DIR/skill-sync.conf"
LOG="$SCRIPT_DIR/skill-sync.log"

DRY_RUN=0
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=1

log() {
  echo "[$(date -u +"%Y-%m-%dT%H:%M:%SZ")] $*" | tee -a "$LOG"
}

dry_log() {
  if [[ $DRY_RUN -eq 1 ]]; then
    echo "[DRY-RUN] $*"
  fi
}

get_repo_root() {
  git -C "$(dirname "$1")" rev-parse --show-toplevel 2>/dev/null || true
}

hash_file() {
  md5 -q "$1"
}

mtime_file() {
  stat -f %m "$1"
}

do_copy() {
  local src="$1" dest="$2"
  if [[ $DRY_RUN -eq 1 ]]; then
    dry_log "would copy $src → $dest"
    return 0
  fi
  mkdir -p "$(dirname "$dest")"
  cp -p "$src" "$dest.tmp" && mv "$dest.tmp" "$dest"
}

sync_pair() {
  local a="$1"
  local b="$2"

  if [[ -L "$a" || -L "$b" ]]; then
    log "ERROR symlink detected — skipping pair: $a <-> $b"
    return 1
  fi

  local a_exists=0 b_exists=0
  [[ -f "$a" ]] && a_exists=1
  [[ -f "$b" ]] && b_exists=1

  if [[ $a_exists -eq 0 && $b_exists -eq 0 ]]; then
    log "ERROR both files missing: $a <-> $b"
    return 1
  fi

  if [[ $a_exists -eq 0 ]]; then
    do_copy "$b" "$a"
    log "SEED B→A $a (from $b)"
    return 0
  fi

  if [[ $b_exists -eq 0 ]]; then
    do_copy "$a" "$b"
    log "SEED A→B $b (from $a)"
    return 0
  fi

  # Both exist — check dirty state for each file
  local root_a root_b
  root_a="$(get_repo_root "$a")"
  root_b="$(get_repo_root "$b")"

  if [[ -n "$root_a" ]]; then
    local rel_a="${a#$root_a/}"
    local dirty_a
    dirty_a="$(git -C "$root_a" status --porcelain -- "$rel_a" 2>/dev/null)"
    if [[ -n "$dirty_a" ]]; then
      log "SKIP dirty working tree for $a — manual sync required"
      return 0
    fi
  fi

  if [[ -n "$root_b" ]]; then
    local rel_b="${b#$root_b/}"
    local dirty_b
    dirty_b="$(git -C "$root_b" status --porcelain -- "$rel_b" 2>/dev/null)"
    if [[ -n "$dirty_b" ]]; then
      log "SKIP dirty working tree for $b — manual sync required"
      return 0
    fi
  fi

  # Hash check — skip if identical
  local hash_a hash_b
  hash_a="$(hash_file "$a")"
  hash_b="$(hash_file "$b")"

  if [[ "$hash_a" == "$hash_b" ]]; then
    log "NO-OP identical content: $(basename "$a")"
    return 0
  fi

  # mtime decides winner
  local mtime_a mtime_b
  mtime_a="$(mtime_file "$a")"
  mtime_b="$(mtime_file "$b")"

  if [[ $mtime_a -ge $mtime_b ]]; then
    do_copy "$a" "$b"
    log "SYNC A→B newer=$a mtime_a=$mtime_a mtime_b=$mtime_b"
  else
    do_copy "$b" "$a"
    log "SYNC B→A newer=$b mtime_b=$mtime_b mtime_a=$mtime_a"
  fi
}

if [[ ! -f "$CONF" ]]; then
  log "ERROR config not found: $CONF"
  exit 1
fi

EXIT=0
while IFS=$'\t' read -r file_a file_b || [[ -n "${file_a:-}" ]]; do
  [[ -z "${file_a:-}" || "${file_a:-}" == \#* ]] && continue
  sync_pair "$file_a" "$file_b" || EXIT=1
done < "$CONF"

exit $EXIT
