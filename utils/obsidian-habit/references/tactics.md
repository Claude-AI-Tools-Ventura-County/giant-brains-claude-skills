# Tactics reference: homepage, capture, pull

These three tactics touch OS-level shortcuts, community plugins, or external
services (Slack/cron) — not safely scriptable generically across machines.
Present them to the user as a short checklist; do not attempt to automate
the install/config steps yourselves.

## Tactic 1 — Front-door homepage (lock the vault to one small note)

Goal: the user never sees the full vault tree on open — only one small note.

- [ ] Install the **Homepage** community plugin (Settings → Community plugins)
- [ ] Install/enable the core **Daily Notes** plugin if not already on
- [ ] Homepage plugin settings → set target to the daily note (e.g. `Today`)
- [ ] File Explorer → collapse the root folder by default so the tree isn't
      the first thing visible even if the user navigates away from Homepage

Time: ~5 minutes. This is Day 1 because it requires zero decisions about
content — only about what's visible.

## Tactic 2 — Frictionless capture shortcut

Goal: capture never requires opening the Obsidian UI at all.

- [ ] Pick a launcher already installed (Raycast, Alfred, Obsidian mobile
      widget, or a simple shell alias)
- [ ] Bind it to append a single line to `Inbox.md` in the vault root —
      no vault browsing involved
- [ ] Test it once: capture a throwaway line, confirm it lands in `Inbox.md`

Time: ~10 minutes. Emphasize: this removes "ugh, all those notes" from the
*capture* action specifically — browsing is a separate problem tactics 1/3
already handle.

## Tactic 4 — rebalance-OS morning pull

Goal: flip the interaction model — the RAG resurfaces the user instead of the
user going to find something.

- [ ] Confirm rebalance-OS's `ask` / vault-search MCP tool responds to a
      manual query first (sanity check before automating)
- [ ] Add a scheduled job (launchd, since the TCC grant pattern is already
      solved for this machine) that each morning:
      1. Queries for 2-3 notes: oldest untouched, weighted by semantic
         relevance to yesterday's GitHub/calendar activity
      2. Drops the result into Slack DM, terminal MOTD, or a `Today.md` block
- [ ] If rebalance-OS is unreachable when this tactic comes up in rotation,
      fall back to a manual version: user runs one `ask` query by hand each
      morning instead of skipping the day entirely

Time: ~1-2 hours for the scheduled version, ~2 minutes/day for the manual
fallback. It's fine to adopt the manual fallback now and upgrade to the
scheduled job later — that's a separate, optional follow-up, not a blocker.

## Tactic 5 — script-backed (see scripts/streak_update.py)

Streak tracking is scriptable and handled by `streak_update.py`. No manual
steps needed beyond deciding whether to also mirror it visually with the
community **Tracker** plugin (optional, cosmetic only).
