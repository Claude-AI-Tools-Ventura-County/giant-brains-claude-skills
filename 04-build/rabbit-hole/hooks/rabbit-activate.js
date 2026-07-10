#!/usr/bin/env node
// rabbit-hole — SessionStart hook.
//
// When the guard flag is on, emits the trigger ruleset on stdout. Claude Code
// injects SessionStart stdout as hidden system context, so the rules land in
// the model's context without the user seeing them.
//
// When the flag is off (the default — the guard is opt-in) this emits nothing
// and the session is identical to one where the hooks were never installed.
//
// Exits 0 unconditionally. A hook must never block session start.

const { isActive, readRuleset } = require('./rabbit-config');

try {
  if (isActive()) {
    const ruleset = readRuleset();
    if (ruleset) process.stdout.write(ruleset);
  }
} catch (e) {
  // Silent fail.
}

process.exit(0);
