#!/usr/bin/env node
// rabbit-hole — UserPromptSubmit hook.
//
// Two jobs:
//   1. Toggle the guard flag on explicit request (`/rabbit-hole on|off`, or the
//      natural-language equivalents).
//   2. While the guard is on, re-anchor the trigger rule each turn. SessionStart
//      injects the full ruleset once, but other plugins inject competing
//      instructions every turn and context compaction eventually prunes the
//      original. This short reminder keeps the rule in the model's attention.
//
// Bare `/rabbit-hole` is deliberately NOT intercepted — that is the skill's own
// slash command, and it must keep invoking a one-shot triage. Only the `on` and
// `off` arguments are toggles, and those are blocked from reaching the skill.
//
// Exits 0 unconditionally, on every path.

const { isActive, activate, deactivate, getFlagPath } = require('./rabbit-config');

const REMINDER =
  'RABBIT-HOLE GUARD ACTIVE. Before raising a third unsolicited finding on a task ' +
  'the user framed as small: stop, sweep the task once end to end, sort every finding ' +
  'into Blocking / In scope, optional / Out of scope, dropped, then ask for the nod. ' +
  'Never invent a finding to fill a bucket; drop empty buckets. Do not fire on ' +
  'genuinely exploratory work, or mid-debug when each finding narrows the same bug.';

let input = '';
process.stdin.on('data', chunk => { input += chunk; });

// An abnormal stdin close (broken pipe, parent crash) emits 'error'. Without a
// listener Node rethrows it as an uncaught exception and the hook exits
// non-zero, which Claude Code surfaces as a hook failure.
process.stdin.on('error', () => process.exit(0));

process.stdin.on('end', () => {
  try {
    const data = JSON.parse(input);
    const prompt = (data.prompt || '').trim().toLowerCase().replace(/\s+/g, ' ');

    // --- Deactivation -------------------------------------------------------
    // "stop" is deliberately absent from these patterns. "stop going down rabbit
    // holes" is one of the skill's own TRIGGER phrases — a user asking for a
    // triage right now, not asking to uninstall the guard that produces it.
    const slashOff = /^\/rabbit-hole\s+(off|disable)\b/.test(prompt);
    const wantsOff = slashOff ||
      /\b(disable|deactivate)\s+(the\s+)?rabbit[-\s]?hole\b/.test(prompt) ||
      /\brabbit[-\s]?hole\s+(guard\s+)?(mode\s+)?(off|disabled)\b/.test(prompt) ||
      /\bturn\s+off\s+(the\s+)?rabbit[-\s]?hole\b/.test(prompt);

    // Questions about the guard are not commands to toggle it.
    const isQuestion =
      /^(what|whats|what's|how|why|when|where|who|does|do|did|is|are|can|could|would|should|tell me|explain)\b/.test(prompt);

    const slashOn = /^\/rabbit-hole\s+on\b/.test(prompt);
    const wantsOn = !wantsOff && !isQuestion && (slashOn ||
      /\b(activate|enable|turn on|switch on)\s+(the\s+)?rabbit[-\s]?hole\b/.test(prompt) ||
      /\brabbit[-\s]?hole\s+(guard\s+)?mode\s+(on|please|now)\b/.test(prompt));

    if (wantsOff) deactivate();
    else if (wantsOn) activate();

    // A slash toggle is a control command, not a request. Block it from reaching
    // the skill (which would otherwise run a triage on the word "on") and report
    // the new state instead.
    if (slashOn || slashOff) {
      const state = slashOn
        ? `Rabbit-hole guard ON. Trigger rule injected each turn. Flag: ${getFlagPath()}\n` +
          'Scope-drip triage will fire on its own when a small task starts growing. ' +
          'Turn off with `/rabbit-hole off`.'
        : 'Rabbit-hole guard OFF. `/rabbit-hole` still works as a one-shot triage.';
      process.stdout.write(JSON.stringify({ decision: 'block', reason: state }));
      return;
    }

    // --- Per-turn reinforcement --------------------------------------------
    if (isActive()) {
      process.stdout.write(JSON.stringify({
        hookSpecificOutput: {
          hookEventName: 'UserPromptSubmit',
          additionalContext: REMINDER,
        },
      }));
    }
  } catch (e) {
    // Silent fail.
  }
});
