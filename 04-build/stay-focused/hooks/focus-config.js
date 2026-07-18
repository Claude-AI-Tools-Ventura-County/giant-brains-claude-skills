#!/usr/bin/env node
// stay-focused — shared flag-file helpers for the session-anchor guard hooks.
//
// The guard is opt-in. Its entire state is one flag file:
//   $CLAUDE_CONFIG_DIR/.stay-focused-anchor   (falls back to ~/.claude/)
// Present and holding a non-empty task string → guard active, that string is the
// anchor. Absent or empty → off. No hook ever creates it implicitly; only an
// explicit "stay focused on X" (or the natural-language equivalent) writes it.
//
// This is where stay-focused diverges from rabbit-hole: rabbit-hole's flag holds
// one whitelisted token ("on"). Ours holds a short, arbitrary, user-authored task
// string, so the read/write path sanitizes rather than whitelists — the value is
// spliced into model context every turn and must stay one clean printable line.
//
// -----------------------------------------------------------------------------
// safeWriteFlag() and readRaw() below are adapted from the caveman project's
// src/hooks/caveman-config.js:
//
//   Copyright (c) 2026 Julius Brussee — MIT License
//   https://github.com/JuliusBrussee/caveman
//
// MIT permits relicensing into this GPL v2 work; the notice above is retained
// as the license requires. The hardening is not incidental: the flag path is
// predictable and user-writable, so a local attacker could replace it with a
// symlink to clobber a file the user can write, or point it at a secret whose
// bytes a reader would then splice into model context.
// -----------------------------------------------------------------------------

const fs = require('fs');
const path = require('path');
const os = require('os');

const FLAG_BASENAME = '.stay-focused-anchor';

// The anchor is free text, so there is no value whitelist. Instead the read path
// sanitizes to a single printable line and the write path caps length. 512 bytes
// is plenty for a task sentence while bounding how much a tampered or oversized
// flag could splice into context.
const MAX_FLAG_BYTES = 512;

function getClaudeDir() {
  return process.env.CLAUDE_CONFIG_DIR || path.join(os.homedir(), '.claude');
}

function getFlagPath() {
  return path.join(getClaudeDir(), FLAG_BASENAME);
}

// Collapse an arbitrary string to one clean line safe to inject: strip control
// characters (including the newlines that could forge extra context lines),
// collapse runs of whitespace, trim, and hard-cap the length. Returns '' when
// nothing printable survives — which the callers treat as "no anchor".
function sanitizeAnchor(raw) {
  if (typeof raw !== 'string') return '';
  // Strip C0 control chars (incl. newlines, which could forge extra context
  // lines) and DEL, then collapse whitespace to a single clean line.
  // eslint-disable-next-line no-control-regex
  const stripped = raw.replace(/[\x00-\x1F\x7F]/g, ' ');
  let out = stripped.replace(/\s+/g, ' ').trim().slice(0, MAX_FLAG_BYTES);
  // Cap by BYTES, not UTF-16 units. readRaw rejects a flag whose byte length
  // exceeds MAX_FLAG_BYTES, so a multi-byte-dense anchor sliced to 512 *chars*
  // could still be written and then read back as "no anchor". Trim whole chars
  // off the end until it fits, so we never cut a multi-byte char in half.
  while (out && Buffer.byteLength(out, 'utf8') > MAX_FLAG_BYTES) out = out.slice(0, -1);
  return out.trim();
}

// Symlink-safe atomic flag write: O_NOFOLLOW where available, temp + rename,
// 0600. When the parent directory is itself a symlink — a legitimate pattern,
// e.g. ~/.claude symlinked onto another volume — resolve through it and verify
// ownership rather than refusing outright.
//
// Silent-fails on every filesystem error. A hook must never block session start.
function safeWriteFlag(flagPath, content) {
  try {
    const flagDir = path.dirname(flagPath);
    fs.mkdirSync(flagDir, { recursive: true });

    let realFlagDir;
    try {
      const lstat = fs.lstatSync(flagDir);
      if (lstat.isSymbolicLink()) {
        realFlagDir = fs.realpathSync(flagDir);
        const realStat = fs.statSync(realFlagDir);
        if (!realStat.isDirectory()) return;
        if (typeof process.getuid === 'function') {
          if (realStat.uid !== process.getuid()) return;
        } else {
          // Windows has no uid — verify the resolved path stays under $HOME.
          const home = path.resolve(os.homedir()).toLowerCase();
          const real = path.resolve(realFlagDir).toLowerCase();
          if (real !== home && !real.startsWith(home + path.sep)) return;
        }
      } else {
        realFlagDir = flagDir;
      }
    } catch (e) {
      return;
    }

    // The flag file itself must never be a symlink — that is the clobber vector.
    const realFlagPath = path.join(realFlagDir, path.basename(flagPath));
    try {
      if (fs.lstatSync(realFlagPath).isSymbolicLink()) return;
    } catch (e) {
      if (e.code !== 'ENOENT') return;
    }

    const tempPath = path.join(realFlagDir, `${FLAG_BASENAME}.${process.pid}.${Date.now()}`);
    const O_NOFOLLOW = typeof fs.constants.O_NOFOLLOW === 'number' ? fs.constants.O_NOFOLLOW : 0;
    const flags = fs.constants.O_WRONLY | fs.constants.O_CREAT | fs.constants.O_EXCL | O_NOFOLLOW;
    let fd;
    try {
      fd = fs.openSync(tempPath, flags, 0o600);
      fs.writeSync(fd, String(content));
      try { fs.fchmodSync(fd, 0o600); } catch (e) { /* best-effort on Windows */ }
    } finally {
      if (fd !== undefined) fs.closeSync(fd);
    }
    fs.renameSync(tempPath, realFlagPath);
  } catch (e) {
    // Silent fail — the flag is best-effort.
  }
}

// Symlink-safe, size-capped read. Symmetric with the write above. Returns '' on
// any anomaly, so a tampered flag degrades to "no anchor" rather than injecting
// whatever bytes happen to be there.
function readRaw(flagPath) {
  try {
    let st;
    try {
      st = fs.lstatSync(flagPath);
    } catch (e) {
      return '';
    }
    if (st.isSymbolicLink() || !st.isFile()) return '';
    if (st.size > MAX_FLAG_BYTES) return '';

    const O_NOFOLLOW = typeof fs.constants.O_NOFOLLOW === 'number' ? fs.constants.O_NOFOLLOW : 0;
    let fd;
    let out;
    try {
      fd = fs.openSync(flagPath, fs.constants.O_RDONLY | O_NOFOLLOW);
      const buf = Buffer.alloc(MAX_FLAG_BYTES);
      const n = fs.readSync(fd, buf, 0, MAX_FLAG_BYTES, 0);
      out = buf.slice(0, n).toString('utf8');
    } finally {
      if (fd !== undefined) fs.closeSync(fd);
    }
    return out;
  } catch (e) {
    return '';
  }
}

// The current anchor, sanitized. '' means no anchor / guard off.
function readAnchor() {
  return sanitizeAnchor(readRaw(getFlagPath()));
}

function isActive() {
  return readAnchor() !== '';
}

// Persist a new anchor. Sanitizes first; a task that sanitizes to '' is a no-op
// rather than a write that would silently disable the guard.
function setAnchor(task) {
  const clean = sanitizeAnchor(task);
  if (clean) safeWriteFlag(getFlagPath(), clean);
  return clean;
}

function clearAnchor() {
  try { fs.unlinkSync(getFlagPath()); } catch (e) { /* already off */ }
}

// The injected ruleset, with the live anchor spliced into the {{ANCHOR}} slot so
// both hooks and the model share one source of truth. Read from disk so the file
// stays canonical. Returns '' if unreadable — callers then inject nothing rather
// than a stale hardcoded copy that could drift from the skill.
function buildRuleset(anchor) {
  try {
    const tmpl = fs.readFileSync(path.join(__dirname, 'focus-ruleset.md'), 'utf8').trim();
    // Replace with a FUNCTION, not a string: a literal replacement string would
    // interpret $&, $1, $$ etc. inside the user's anchor ("fix the $100 bug" would
    // lose the "1"). A replacer function is passed the anchor verbatim.
    const fill = anchor || '(none set — ask the user what to stay focused on)';
    return tmpl.replace(/\{\{ANCHOR\}\}/g, () => fill);
  } catch (e) {
    return '';
  }
}

module.exports = {
  FLAG_BASENAME, MAX_FLAG_BYTES,
  getClaudeDir, getFlagPath, sanitizeAnchor, safeWriteFlag, readRaw,
  readAnchor, isActive, setAnchor, clearAnchor, buildRuleset,
};
