---
name: install-improve-audit
description: Get an unfamiliar repo installing and building locally, fix only what blocks it, and open a PR carrying the fixes plus an append-only change log. The deliverable is a working build and a PR — never a findings report. Trigger when the user says "install this repo", "get this building", "clone and set this up", "make this run locally", "why won't this build", "/install-improve-audit", or hands over a repo path or URL and asks for it working. Improvements are a bounded bonus tier that opens only after the build passes, is capped at 3 items, and is always droppable. Do NOT use for repo analysis, architecture review, code-quality assessment, deliberate security scanning, or dependency-hygiene audits — this skill refuses those and names the right tool instead.
---

# Install Improve Audit

Get the target repo building locally, fix what blocks it, and open a PR. The name is
the priority order, and the order is strict:

- **Install** — the only thing that counts as success. Non-negotiable.
- **Improve** — a bonus tier, opened only after the build passes, hard-capped, always droppable.
- **Audit** — the append-only log of what you changed and why. A change log, not a code audit.

**Three outputs and no others: a working build, a committed fix set, an open PR.**

## Input

The target is the repo path or URL the user named, or the current working directory if
they named none. If they stated a `<slug>`, use it for the branch and doc names;
otherwise derive it from the repo directory name. Honor a docs-path override and a
GitHub issue number if given. Ask for nothing else — if the target resolves, start.

## Acceptance gate — read first

Your final message is invalid unless it contains all four:

1. a verdict: `INSTALLED`, `INSTALLED-DEGRADED (<what is off>)`, or `BLOCKED (<one reason>)`
2. the commands that now work, or the exact command that failed
3. the last 15 lines of install-check output — from the passing run if DONE was
   reached, from the failing run if it was not
4. the PR URL — or, if you lack push access, the branch name and the exact push
   command in its place. That is the only permitted substitute.

An issues list is not a deliverable. A code-quality assessment is not a
deliverable. A repo-is-bad summary is not a deliverable. If the repo cannot be
installed, ship `BLOCKED` with the first blocking error and the smallest next
action — not a broad assessment.

If the caller asks for a repo analysis, say this skill installs first, and that a
code-review or repo-health tool is the right one for analysis. The "Audit" in the
name is the change log, not a code audit.

## DONE — binary, nothing else counts

From a clean tree, both of these exit 0:

1. the repo's dependency install command
2. the repo's build command

Write both into `install-check.sh` at the repo root at step 4 of the order of
operations — right after branching, so the file is born on the install branch. If
that file exists or the root is not writable, use `.install-audit/install-check.sh`
and name that path in your final output.

You are not finished until the check exits 0 and you have pasted its last 15
lines verbatim. "It builds now" is not acceptance.

Edge cases, decided in advance — do not deliberate:

- **No build command exists or can be inferred:** dependency install alone is DONE.
  Verdict `INSTALLED-DEGRADED (no build command)`.
- **The documented build command also runs tests, lint, or e2e:** narrow it to the
  compile/build step only. Tests are not part of DONE. If it cannot be narrowed and
  only the test phase fails, verdict `INSTALLED-DEGRADED (tests failing, build clean)`.
- **Optional, after DONE:** start the app for 10 seconds and kill it. If it dies,
  verdict is `INSTALLED-DEGRADED` with the reason. Do not fix runtime config unless
  it is under 10 minutes.

## Budget

45 minutes of **active work** for the install. Unattended waiting — dependency
downloads, cold builds — does not count against it. The Improve box and the PR steps
happen after this clock stops, and have their own limits.

- At **20 minutes**, print one line: `STATUS <mm:ss> | last error | next move`.
- At **22 minutes**, if the build has never succeeded, all fixing stops. From that
  point the only permitted actions are:
  1. commit `install-check.sh` and every fix that did land
  2. finish the audit log
  3. write `## Blocked` and `## Recommendations`
  4. open the draft PR
  5. produce the final output

  No further source reading. No alternate-architecture research. No issue list. No
  improvements — a repo that never built has nothing to improve.

## Order of operations — do not reorder

1. **Environment, one line each, no prose:** OS/arch; the runtime version the repo
   declares (`.nvmrc`, `.python-version`, `engines`, `rust-toolchain.toml`,
   `go.mod`); the version actually installed; which version manager is available;
   package manager and version.
2. **Recon — 10 minutes max, delegated.** Launch the Explore subagent, read-only,
   with this exact return contract: *"Return the documented dependency-install
   command and build command from README, INSTALL, Makefile, and CI workflow files.
   Return the declared runtime version. Return nothing else. Do not read source
   files. Do not assess the code."* If Explore is unavailable, do the same recon
   yourself, limited to those same files and the same 10 minutes.
3. **Branch** `install/<YYYY-MM-DD>-<slug>`.
4. **Write `install-check.sh`** with the documented install and build commands.
5. **Create the audit doc:** frontmatter and an empty log table only. Nothing else
   goes in it yet.
6. **Run the documented install command.** Do not pre-diagnose. Let it fail.
7. **Loop until DONE or budget:** take the **first** error → smallest change that
   clears it → re-run → append one log row. Repeat.
8. **On DONE:** open the Improve box, if anything on its list qualifies.
9. **Write** the audit doc's status table, `## Blocked`, `## Improvements`, and
   `## Recommendations`, then open the PR.

## What you may read during the fix loop

Only files directly implicated by the error in front of you: build scripts, config
files, env templates, manifests, lockfiles, version pins, and the file the failing
command names. Do not browse the codebase looking for problems.

## Improve — the bonus tier

Opens only after `install-check.sh` exits 0. Everything in it is droppable, and
dropping all of it costs the run nothing.

**Box: 15 minutes, 3 items maximum, hard stop.** Separate from the 45-minute install
budget, and it runs before the PR steps. When either cap is hit, stop mid-item, revert
anything unfinished, and move what is left to `## Recommendations`.

**Eligible — only these, and only when the install itself put it in front of you:**

1. Record a runtime version the repo needs but does not declare (`.nvmrc`,
   `.python-version`, `engines`) — the version you had to discover the hard way.
2. Correct an install or build command in the repo's own docs that you proved wrong.
3. Add the step you had to work out yourself to the existing install docs.
4. Add a key you had to guess to an existing `.env.example`.
5. Wire `install-check.sh` into a CI workflow that already runs on push — one line,
   and only if such a workflow already exists.

**Not eligible, however tempting:** dependency upgrades the build did not need,
refactors, formatting or lint sweeps, new tests, new CI files, new doc files, renaming
or restructuring anything, or an improvement to code you never had to open. If it is
not on the list above, it is a recommendation, not an improvement.

**Rules that keep this skippable:**

- Each improvement is its own commit, prefixed `improve:`. A reviewer must be able to
  drop every one of them and still merge a working build.
- Re-run `install-check.sh` after each one. If an improvement breaks it, `git revert`
  that commit and move on — never debug an improvement.
- Improvements never change the verdict, never appear in `## Blocked`, and never delay
  the PR.
- `BLOCKED` runs skip this tier entirely.
- **Zero improvements is a normal, complete run.** Do not manufacture one to fill the
  section; an empty `## Improvements` is omitted, not apologized for.

## PDDA compliance — deliberately partial

Full PDDA compliance is **not a goal of this run** and is not achievable inside the
budget. Produce exactly what is listed below and nothing more. Do not open PDDA.md
or ROUTER.md to check whether more is required — the answer is no.

**Location:** `PROJECT/2-WORKING/INSTALL-<slug>.md`. Override with the docs path if
one was given. If the repo has no `PROJECT/` tree, fall back to
`docs/install/INSTALL-<slug>.md`, or repo root. Do not create a PDDA lifecycle
structure in a repo that lacks one.

**Frontmatter — exactly these keys:**

```
title, status, created, updated, owner, doc_type: install-audit
ratings_provisional: true
gh_issue          # only if an issue number was given
```

**Body — exactly these sections:**

```
Status table (what was completed | what's next)
the append-only fix log table
## Blocked
## Improvements     # omit if none landed
## Recommendations
```

**Deliberately omitted — do not add:** Swarm Preflight Contract, `fix_probes`,
phases, `complexity` / `risk` / `effort`, `non_goals`, `roadmap_exempt`,
MARATHON.yaml stanzas, lifecycle folder transitions.

`fix_probes` specifically: `install-check.sh` **is** the gate for this work. A probe
set authored under time pressure is where polarity inversions come from, and an
inverted probe reads as already-done. A later pass adds probes if this graduates.

`ratings_provisional: true` is load-bearing — a 45-minute run's ratings are guesses,
and the flag keeps this doc out of automated selection until a human reviews it.

**Never move the doc to `3-COMPLETED`.** That transition belongs to the closeout
chain after the PR merges, not to this run.

Two rules hold regardless of location:

- **Append-only during the run.** Each row is written **after** the fix is applied.
  No narrative sections until step 9.
- The log is a table: `| time | step | error (first line only) | change made | file | result |`

## Blocker ladder — native only, in this order

Two fix attempts per distinct error, 10 minutes max, then move down:

1. Honor the lockfile exactly (`npm ci`, `pip install -r` with hashes,
   `poetry install`, `cargo build --locked`) before touching any version.
2. Switch to the runtime version the repo **declares**, via the version manager.
   Do not edit the declaration.
3. If a postinstall script is the blocker, retry with scripts disabled
   (`--ignore-scripts` or equivalent). Log it as a degradation.
4. Relax the declared version. Log it as a degradation with the reason.
5. Exclude the failing optional component, workspace member, or extra; build the
   rest. Log what is excluded.
6. `BLOCKED`. Append to `## Blocked`: the error, what was tried, and the single
   smallest thing that would unblock it.

Containers are not an acceptable install. If one would obviously have worked, log
it once under Recommendations and move on.

## Scope fence

During the fix loop this fence is absolute. The Improve tier widens it by exactly five
listed items, and only after DONE.

**May edit freely:** dependency manifests and lockfiles, config and env files,
build and run scripts, `install-check.sh`, install docs, version-manager pins.

**May patch minimally** — only when the error is clearly build-shaped: a bad import
path, a missing shim, a syntax break from a version bump, a hardcoded absolute
path. Smallest possible diff. Log every one.

**May NOT:** refactor logic, bump majors to chase a nicer API, change public APIs,
reformat, fix lint or type errors that do not block the build, edit tests except to
make them runnable, or repair broken business logic. If the application genuinely
does not compile against its own declared runtime, that is `BLOCKED` with a
recommendation for a separate code-fixing run — not this skill's job.

Anything outside the fence is logged as a recommendation. You do not do it.

If the repo is not owned by your organization: use no credentials it did not ship
with, no internal registries, and run nothing beyond its documented install and
build commands.

## The PR — the run is not finished at DONE

1. **Commit** `install-check.sh`, the audit doc, and every fix. One commit per
   logical fix; do not squash the fix history into a single commit. The reviewer
   needs to see which change cleared which error. Improvement commits stay separate
   and keep their `improve:` prefix, so they can be dropped independently.
2. **CHANGELOG.md** — if the repo already has one, add **one** entry summarizing the
   landed fixes. If the repo has no CHANGELOG, do not create one.
3. **Push the branch.** If you lack push access to origin, stop here and hand back the
   branch name and the exact push command. That pair substitutes for the PR URL in the
   acceptance gate and in Final output — it is the one case where a run is complete
   without a URL. Everything else in the final output is still required.
4. **Open the PR.** Title: `install: <verdict> — <slug>`. Body: your final output,
   **verbatim**. It is already exactly what a reviewer needs; do not author a
   second description.
5. **Do not merge.** No auto-merge, no reviewer assignment, no labels.
6. **`BLOCKED` still ships a PR** — as a draft. `install-check.sh`, the fixes that
   did land, and the blocked doc are what let the next attempt resume rather than
   restart. A blocked run with no PR wastes the whole session.

## Final output — exactly this, nothing more

- **Verdict:** `INSTALLED` | `INSTALLED-DEGRADED (<what is off>)` | `BLOCKED (<one reason>)`
- **PR:** URL, and `draft` if drafted. With no push access: the branch name and the
  exact push command instead — the only permitted substitute for a URL
- Last 15 lines of install-check output, verbatim — the passing run on DONE, the
  failing run on `BLOCKED`. Never omitted: a run with no output is not a report.
- The copy-pasteable commands that now work, or the command that failed
- `git diff --stat` for the branch
- `## Improvements` — one line each, with the commit that carries it (omit if none)
- `## Blocked` and `## Recommendations` — ranked, each traceable to an error you hit
- `### Security — incidental findings only` (below; omit entirely if empty)

### Security — incidental findings only

Written after DONE, at the bottom. Not an audit. Never changes the verdict.

**Only what the install put in front of you** — no scanning, no grepping for
secrets, no extra tool calls, no time spent looking. Typical qualifying finds: a
credential or private key in a tracked file you opened; a committed `.env` with
real values; an install script fetching and executing remote code; a dependency
pulled over plain HTTP or from an unpinned source; no lockfile at all.

**Maximum 3 items, one line each:** what it is, the path, why it matters. No
severity ratings, no remediation plans, no CVE lookups. If you find yourself
investigating, stop — write the line and move on.

An empty security section is the expected outcome, not a gap.

## Not wanted

Architecture review, code quality assessment, deliberate security scanning,
coverage analysis, dependency hygiene review, or any finding you did not encounter
while making the build pass.

Do not deliver a static-analysis report. A final message containing findings but no
verdict and no PR is incomplete work.
