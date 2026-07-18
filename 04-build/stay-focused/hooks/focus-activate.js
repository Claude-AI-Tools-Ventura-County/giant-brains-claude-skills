#!/usr/bin/env node
// stay-focused — SessionStart hook.
//
// When an anchor is set, emits the anchor-discipline ruleset (with the live
// anchor spliced in) on stdout. Claude Code injects SessionStart stdout as hidden
// system context, so the rules land in the model's context without the user
// seeing them — and a session resumed the next morning still knows the anchor.
//
// When no anchor is set (the default — the guard is opt-in) this emits nothing
// and the session is identical to one where the hooks were never installed.
//
// Exits 0 unconditionally. A hook must never block session start.

const { readAnchor, buildRuleset } = require('./focus-config');

try {
  const anchor = readAnchor();
  if (anchor) {
    const ruleset = buildRuleset(anchor);
    if (ruleset) process.stdout.write(ruleset);
  }
} catch (e) {
  // Silent fail.
}

process.exit(0);
