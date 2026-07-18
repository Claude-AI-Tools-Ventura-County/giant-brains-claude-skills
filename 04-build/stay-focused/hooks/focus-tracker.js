#!/usr/bin/env node
// stay-focused — UserPromptSubmit hook.
//
// Three jobs:
//   1. SET the anchor when the user says "stay focused on X" / "stay on track for
//      X" / "/stay-focused X" (or a close variant). The captured task is persisted
//      so SessionStart and every later turn can re-inject it.
//   2. CLEAR the anchor on an explicit off ("/stay-focused off", "stop staying
//      focused", "drop the focus", …).
//   3. While an anchor is set, re-anchor the discipline each turn. SessionStart
//      injects the full ruleset once, but other plugins inject competing
//      instructions every turn and compaction eventually prunes the original.
//      This short reminder keeps the anchor and the reply shape in attention.
//
// Only `/stay-focused off` is intercepted (blocked + reported). Every other prompt
// — including a set — is allowed through so the model actually does the work / the
// `/stay-focused` skill can load its full instructions on first use.
//
// Exits 0 unconditionally, on every path.

const { readAnchor, setAnchor, clearAnchor, sanitizeAnchor, getFlagPath } = require('./focus-config');

function reminder(anchor) {
  return (
    `STAY-FOCUSED ACTIVE. Anchor: "${anchor}". Every reply: (1) open with ` +
    `**Status of ${anchor}:** one honest line on its current state (fixed / shipped / ` +
    `blocked on an unmerged branch / in progress / not started / drifted / unknown) — then a ` +
    `\`---\` rule, then only the non-empty buckets, one line each: What's Shipped / What's ` +
    `Blocked / Recommended Next Steps / Optional Next Steps / Only Useful FYIs. ` +
    `(2) Minimum viable text — no preamble, no filler, drop empty buckets, never invent items. ` +
    `Re-orient to the anchor; if the thread drifted, name the drift in one line and pull back. ` +
    `A tangent the user asked for doesn't replace the anchor. Don't fake a status; if the ` +
    `anchor is done, say so and ask for a new one rather than inventing work.`
  );
}

// Extract the task from the raw (case-preserving) prompt. Tried in order; first
// match wins. Trailing sentence punctuation and wrapping quotes are trimmed.
//
// The imperative-only forms ("stay"/"keep", never the gerund "staying"/"keeping")
// are deliberate: a gerund shows up in descriptive/interrogative sentences —
// "why are we STAYING focused on the old PR?" — which must NOT re-set the anchor.
// The wh-question guard in the handler is the belt to this suspenders.
const SET_PATTERNS = [
  /\bstay\s+(?:focused|focussed)\s+on\s+(.+)$/i,
  /\bstay\s+on\s+track\s+(?:for|with|on)\s+(.+)$/i,
  /\bkeep(?:\s+(?:me|us))?\s+(?:focused|focussed)\s+on\s+(.+)$/i,
  /\bkeep(?:\s+(?:me|us))?\s+on\s+track\s+(?:for|with|on)\s+(.+)$/i,
  /^\/stay[-\s]?focused\s+(?:on\s+|to\s+|for\s+)?(.+)$/i,
];

function extractTask(rawPrompt) {
  const raw = rawPrompt.trim();
  for (const re of SET_PATTERNS) {
    const m = raw.match(re);
    if (m && m[1]) {
      let task = m[1].trim().replace(/^["'`]+|["'`]+$/g, '').replace(/[.!?,;:]+$/g, '').trim();
      task = sanitizeAnchor(task);
      // A capture that is itself an off-word ("off", "clear") is not a task.
      if (task && !/^(off|clear|done|stop|reset|none)$/i.test(task)) return task;
    }
  }
  return '';
}

let input = '';
process.stdin.on('data', chunk => { input += chunk; });

// An abnormal stdin close (broken pipe, parent crash) emits 'error'. Without a
// listener Node rethrows it as an uncaught exception and the hook exits
// non-zero, which Claude Code surfaces as a hook failure.
process.stdin.on('error', () => process.exit(0));

function emitContext(text) {
  process.stdout.write(JSON.stringify({
    hookSpecificOutput: { hookEventName: 'UserPromptSubmit', additionalContext: text },
  }));
}

process.stdin.on('end', () => {
  try {
    const data = JSON.parse(input);
    const rawPrompt = String(data.prompt || '');
    const norm = rawPrompt.trim().toLowerCase().replace(/\s+/g, ' ');

    // Questions about the guard are not commands to toggle it off.
    const isQuestion =
      /^(what|whats|what's|how|why|when|where|who|does|do|did|is|are|can|could|would|should|tell me|explain)\b/.test(norm);

    // --- Deactivation -------------------------------------------------------
    // "stop" only counts as OFF when bound to focus/track — bare "stop" must not
    // clear the anchor mid-task.
    const slashOff = /^\/stay[-\s]?focused\s+(off|clear|done|stop|reset)\b/.test(norm);
    const nlOff = !isQuestion && (
      /\bstop\s+(staying\s+)?(focused|focussed|on\s+track)\b/.test(norm) ||
      /\b(drop|clear|reset|forget)\s+(the\s+)?(focus|anchor)\b/.test(norm) ||
      /\bunfocus\b/.test(norm) ||
      /\b(turn\s+off|disable|deactivate|end)\s+(stay[-\s]?focused|the\s+focus|focus\s+mode)\b/.test(norm) ||
      /\bno\s+longer\s+(stay\s+)?(focused|on\s+track)\b/.test(norm)
    );

    if (slashOff || nlOff) {
      clearAnchor();
      if (slashOff) {
        process.stdout.write(JSON.stringify({
          decision: 'block',
          reason: 'stay-focused OFF. Anchor cleared. Replies return to normal shape. ' +
            'Set a new anchor any time with "stay focused on <task>".',
        }));
      } else {
        emitContext('stay-focused is now OFF — the session anchor was cleared. Reply normally.');
      }
      return;
    }

    // --- Set / re-affirm ----------------------------------------------------
    // A wh-question that happens to contain "stay focused on X" ("what should we
    // stay focused on, X or Y?") is never an imperative to re-anchor — skip the
    // set. Polite requests ("can we / let's / please stay focused on X") are NOT
    // wh-questions, so they still set the anchor as advertised.
    const isWhQuestion = /^(why|what|whats|what's|when|where|who|whose|how|which)\b/.test(norm);
    const task = isWhQuestion ? '' : extractTask(rawPrompt);
    if (task) {
      const saved = setAnchor(task) || task;
      // Let the prompt through (do the work / load the skill) and confirm the new
      // anchor plus the standing format in one injection.
      emitContext(`STAY-FOCUSED anchor set to: "${saved}". ${reminder(saved)}`);
      return;
    }

    // --- Per-turn reinforcement / no-anchor prompt --------------------------
    const anchor = readAnchor();
    if (anchor) {
      emitContext(reminder(anchor));
      return;
    }

    // Bare "stay focused" / "/stay-focused" with no task and nothing set: tell the
    // model to ask what to lock onto rather than guessing.
    const bareAffirm =
      /^\/stay[-\s]?focused[.!?\s]*$/.test(norm) ||
      /^(please\s+|let'?s\s+|ok\s+|okay\s+)?(stay|keep)\s+(me\s+|us\s+)?(focused|focussed|on\s+track)[.!?\s]*$/.test(norm);
    if (bareAffirm) {
      emitContext(
        'stay-focused invoked with no task and no anchor set. Ask the user, in one line, ' +
        'what to stay focused on for this session, then adopt the stay-focused reply shape ' +
        '(Status of [anchor] + --- rule + non-empty buckets, minimum viable text).'
      );
    }
    // Otherwise: guard is off, inject nothing.
  } catch (e) {
    // Silent fail.
  }
});
