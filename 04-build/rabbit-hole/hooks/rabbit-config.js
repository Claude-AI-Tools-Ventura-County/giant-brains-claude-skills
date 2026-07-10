#!/usr/bin/env node
// rabbit-hole — shared flag-file helpers for the scope-drip guard hooks.
//
// The guard is opt-in. Its entire state is one flag file:
//   $CLAUDE_CONFIG_DIR/.rabbit-hole-active   (falls back to ~/.claude/)
// Present and containing "on" → guard active. Absent → off. No hook ever
// creates it implicitly; only an explicit `/rabbit-hole on` (or the natural
// language equivalent) writes it.
//
// -----------------------------------------------------------------------------
// safeWriteFlag() and readFlag() below are adapted from the caveman project's
// src/hooks/caveman-config.js:
//
//   Copyright (c) 2026 Julius Brussee — MIT License
//   https://github.com/JuliusBrussee/caveman
//
// MIT permits relicensing into this GPL v2 work; the notice above is retained
// as the license requires. The hardening they implement is not incidental: the
// flag path is predictable and user-writable, so a local attacker could replace
// it with a symlink to clobber a file the user can write, or point it at a
// secret whose bytes a reader would then splice into model context.
// -----------------------------------------------------------------------------

const fs = require('fs');
const path = require('path');
const os = require('os');

const FLAG_BASENAME = '.rabbit-hole-active';

// The only value the flag may hold. Anything else — truncation, corruption, a
// planted payload — reads as "off" rather than as some mode nobody asked for.
const VALID_VALUES = ['on'];

// The longest legitimate value is "on" (2 bytes). 64 leaves slack for a
// trailing newline without enabling exfiltration through an oversized read.
const MAX_FLAG_BYTES = 64;

function getClaudeDir() {
  return process.env.CLAUDE_CONFIG_DIR || path.join(os.homedir(), '.claude');
}

function getFlagPath() {
  return path.join(getClaudeDir(), FLAG_BASENAME);
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

// Symlink-safe, size-capped, whitelist-validated read. Symmetric with the
// write above. Returns null on any anomaly, so a tampered flag degrades to off.
function readFlag(flagPath) {
  try {
    let st;
    try {
      st = fs.lstatSync(flagPath);
    } catch (e) {
      return null;
    }
    if (st.isSymbolicLink() || !st.isFile()) return null;
    if (st.size > MAX_FLAG_BYTES) return null;

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

    const raw = out.trim().toLowerCase();
    return VALID_VALUES.includes(raw) ? raw : null;
  } catch (e) {
    return null;
  }
}

function isActive() {
  return readFlag(getFlagPath()) === 'on';
}

function activate() {
  safeWriteFlag(getFlagPath(), 'on');
}

function deactivate() {
  try { fs.unlinkSync(getFlagPath()); } catch (e) { /* already off */ }
}

// The injected ruleset. Read from disk so the file stays the single source of
// truth for both hooks. Returns '' if unreadable — callers then inject nothing
// rather than a stale hardcoded copy that could drift from the skill.
function readRuleset() {
  try {
    return fs.readFileSync(path.join(__dirname, 'rabbit-ruleset.md'), 'utf8').trim();
  } catch (e) {
    return '';
  }
}

module.exports = {
  FLAG_BASENAME, VALID_VALUES, MAX_FLAG_BYTES,
  getClaudeDir, getFlagPath, safeWriteFlag, readFlag,
  isActive, activate, deactivate, readRuleset,
};
