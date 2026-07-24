---
name: btw
description: Starts and maintains a manual session attention firewall for Claude Code. Invoke only with /btw when the user explicitly wants focus mode, no side quests, or a maximum of three active tasks. Create one append-only Markdown log per BTW focus session, capture the opening user prompt plus repository and branch context, and park assistant-initiated off-task findings as Action, Review Later, or Interesting instead of surfacing them in assistant prose. After activation, treat plain-language "btw check" as an in-session re-anchor rather than a new invocation.
argument-hint: "[up to 3 focus items or the opening session request]"
disable-model-invocation: true
allowed-tools:
  - 'Bash(python3 "${CLAUDE_SKILL_DIR}/scripts/btw.py" *)'
  - 'Bash(python "${CLAUDE_SKILL_DIR}/scripts/btw.py" *)'
---

# BTW — Session Attention Firewall

Keep the active BTW session focused on no more than three declared tasks. Park assistant-initiated side observations in the session log instead of describing them in assistant prose.

Invocation arguments: `$ARGUMENTS`

## Session model

- A **Claude session** is identified by `${CLAUDE_SESSION_ID}`.
- A **BTW session** begins when the user invokes `/btw` and ends when the user wraps up or all focus items complete.
- Create one new `BTW/*.md` file for each BTW session. If `/btw` is invoked again while the current BTW session is still active, re-anchor to the existing file unless the user explicitly asks to start a new BTW session.
- The helper stores only an active-file pointer outside the repository. The project record remains the single append-only Markdown file.

## Helper contract

Use `${CLAUDE_SKILL_DIR}/scripts/btw.py` for every persistent operation. Prefer `python3`; fall back to `python` only when `python3` is unavailable.

Every helper command:

- prints one JSON object and no prose;
- sets `ok: true` only after the write is flushed and verified;
- returns repository-relative file paths;
- redacts recognized live credential formats before persistence;
- keeps the log chronological and append-only;
- uses the latest successful helper result as the source of truth for focus, file path, and counts.

If a helper command exits nonzero or returns `ok: false`, surface the failure immediately. Do not claim an item was parked unless the helper confirms it.

## Start workflow

1. Capture the exact user message that invoked this skill as the opening prompt. Include `/btw` and its arguments when visible. If the interface hides the slash prefix, reconstruct it as `/btw $ARGUMENTS`. Preserve the text verbatim except detected live credentials, which must be redacted and surfaced under the safety override.
2. Start or recover the BTW session immediately so the opening prompt is not lost. Pass the prompt through a single-quoted heredoc whose delimiter does not appear in the prompt:

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/btw.py" start \
  --claude-session-id "${CLAUDE_SESSION_ID}" \
  --project-dir "${CLAUDE_PROJECT_DIR}" <<'BTW_OPENING_PROMPT'
<exact invoking user message>
BTW_OPENING_PROMPT
```

Use `--new` only when the user explicitly requests a new BTW session while another is active. The helper closes the previous file as superseded before creating the new one.

3. Establish one to three focus items:

- If the user already supplied 1–3 unambiguous tasks, treat them as confirmed. Echo them once and proceed in the same turn; do not wait for an extra yes.
- If the tasks are missing or materially ambiguous, ask: “What are the up-to-3 things we’re doing this session?”
- If more than three are supplied, ask the user to choose three. After the choice, park the remaining requested tasks as Review Later entries.
- Never infer a fourth active task.

4. Persist the focus list as JSON on stdin:

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/btw.py" focus \
  --claude-session-id "${CLAUDE_SESSION_ID}" \
  --project-dir "${CLAUDE_PROJECT_DIR}" <<'BTW_JSON'
{"items":["task 1","task 2"],"allow_git_writes":false}
BTW_JSON
```

Set `allow_git_writes` to `true` only when a declared focus item explicitly requires a mutating Git operation such as committing, switching branches, rebasing, or pushing. Editing code does not itself require Git writes.

5. If the `start` result contains a non-null `warning`, show it once. Use the helper’s wording. Do not claim that a non-ignored file will automatically be committed.

The generated file records at its top:

- the BTW and Claude session identifiers;
- local and UTC start times;
- repository name;
- active branch and commit at start;
- the opening user prompt;
- a chronological timeline of focus, context, parked, and end events.

## Relevance test

Apply this test before every user-facing message. Content may appear in assistant prose only when at least one condition is true:

1. It is required to complete a declared focus item.
2. It reports a blocker on a declared focus item.
3. It directly answers an informational question the user just asked.
4. It responds to an explicit request to inspect or discuss parked entries.
5. **Safety override:** it concerns a live or leaked credential, imminent data loss, or a destructive command about to run.

A request to perform new off-focus work does not pass condition 3 merely because it is phrased as a question. Park the request as Review Later and ask which current focus item it should replace. If the user explicitly names the replacement, update the focus without another confirmation round.

For a secret under the safety override, surface it immediately and use this remediation order: revoke at the provider first, then scrub stored copies.

Everything else—unrelated bugs, refactor temptations, design ideas, missing tests outside scope, conventions, and curiosities—must be parked and omitted from assistant prose.

## Parking workflow

Park only concrete observations supported by a file, command output, test result, or clear rationale. Use repository-relative paths; never store machine-specific absolute paths.

Classify each item as:

- **Action** — a real defect or risk likely to bite if ignored: broken logic, a security smell below the safety-override threshold, a failing edge case, or a material reliability problem.
- **Review Later** — a legitimate improvement, design question, deferred user request, missing test, or documentation gap with no immediate harm.
- **Interesting** — a context-only pattern, convention, or curiosity with no required action.

Batch all items discovered in one turn into one helper call and complete the call before producing assistant prose:

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/btw.py" park \
  --claude-session-id "${CLAUDE_SESSION_ID}" \
  --project-dir "${CLAUDE_PROJECT_DIR}" <<'BTW_JSON'
[
  {
    "category":"action",
    "finding":"One-line finding",
    "why":"Why it matters",
    "evidence":"File, test, or command evidence",
    "path":"src/example.ts"
  },
  {
    "category":"review",
    "finding":"Deferred improvement",
    "why":"Why it is worth revisiting",
    "path":"docs/design.md"
  }
]
BTW_JSON
```

The helper skips exact duplicates. When the same finding gains materially different evidence or impact, it appends an update that references the earlier event ID.

Do not include parked-item details in assistant prose. Tool interfaces may still show that a logging command ran; the enforceable promise is that the response itself contains only focus-relevant content and the recap counter.

## Recap counter

End every substantive prose turn with exactly one counter line when the running count is nonzero:

`BTW: 4 items parked (2 action, 1 review, 1 interesting)`

Use the counts from the latest successful helper result. Call `status` when counts are unknown, after compaction, after external file changes, or during a re-anchor:

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/btw.py" status \
  --claude-session-id "${CLAUDE_SESSION_ID}" \
  --project-dir "${CLAUDE_PROJECT_DIR}"
```

Do not describe the parked items in the counter.

Do not append the counter inside exact-format or machine-readable output such as JSON, YAML, a patch, a commit message, source code, or a shell command. Put it in adjacent prose when possible. Otherwise omit it for that turn and include the current count in the next normal prose response.

## Re-anchoring and focus changes

On plain-language `btw check` or visible drift:

1. Do not reload or re-invoke the skill.
2. Run `status`.
3. Restate the current 1–3 focus items in one line.
4. Continue the active task.

If no active BTW session exists, run the normal start workflow.

When focus changes, append a focus event; never rewrite the original header:

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/btw.py" focus \
  --claude-session-id "${CLAUDE_SESSION_ID}" \
  --project-dir "${CLAUDE_PROJECT_DIR}" <<'BTW_JSON'
{"items":["replacement task","retained task"],"allow_git_writes":false}
BTW_JSON
```

The helper also appends a context event when the active Git branch changes. The filename and header continue to identify the branch at session start.

## Parked-item review

Only reveal parked entries when the user asks. Retrieve them with:

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/btw.py" show \
  --claude-session-id "${CLAUDE_SESSION_ID}" \
  --project-dir "${CLAUDE_PROJECT_DIR}" \
  --category action
```

Omit `--category` to retrieve all parked entries. Answer the user’s review request directly; revealing requested entries passes the relevance test.

## Subagents

Before delegating work, give the subagent the same focus list and require it to return only focus-relevant findings. The main agent remains responsible for parking any off-focus material returned by a subagent. Do not let a subagent create a second active focus list.

## Session end

When the user wraps up or all focus items complete, close the session with completed and open items:

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/btw.py" end \
  --claude-session-id "${CLAUDE_SESSION_ID}" \
  --project-dir "${CLAUDE_PROJECT_DIR}" <<'BTW_JSON'
{"completed":["task 1"],"open":["task 2"]}
BTW_JSON
```

Then give one line containing:

- completed versus open focus items;
- final BTW counts;
- the repository-relative log path;
- a suggestion—not an automatic action—to review Action items.

## Hard rules

- Never display more than three active focus items.
- Never surface a parked item unless the user asks or the safety override applies.
- Never opportunistically modify files outside the declared tasks to fix a parked item.
- Keep Git operations read-only unless a focus item explicitly requires Git writes.
- Treat these as behavioral constraints, not a security boundary. For mechanical Git enforcement, use the optional hook documented in [references/ENFORCEMENT.md](references/ENFORCEMENT.md).
- If the log write fails, say so immediately; the failure blocks this skill’s contract.
- The helper’s own writes to the session log and external state pointer are the only automatic persistence allowed outside the declared work.

## Supporting files

- Run [scripts/btw.py](scripts/btw.py) for all session operations.
- Read [references/LOG_FORMAT.md](references/LOG_FORMAT.md) when debugging the file schema or helper payloads.
- Read [references/ENFORCEMENT.md](references/ENFORCEMENT.md) only when the user wants deterministic Git-write blocking.
