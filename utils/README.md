# Utils

Standalone skills that live in this repo but are **not part of the Giant Brains suite**. Each subfolder is a normal skill (a directory containing `SKILL.md`) and installs the same way: symlink or copy it into `~/.claude/skills/`.

## Skills

- **obsidian-habit** -- Run the daily Obsidian habit-building exercise as a 6-state FSM that surfaces exactly one low-friction tactic per day. Scripts: `habit.py`, `archive_stale_notes.py`, `streak_update.py`.

## Moved to giant-brains-swe-skills (2026-08-30)

The developer tooling that used to live here -- **github-auth-debug**, **install-improve-audit**, **read-only**, **rpr**, **vscode-color**, plus the **claude-code-dotfiles-fork** and **skill-sync** kits -- now lives under `04-toolbox/` and `utils/` in [giant-brains-swe-skills](https://github.com/Claude-AI-Tools-Ventura-County/giant-brains-swe-skills). Forwarding stubs remain at the old paths for one release. Earlier moves: **shakedown** (now `03-audit/shakedown` there), **swe-diagram** (in [xyz-3-agents-swarm](https://github.com/Claude-AI-Tools-Ventura-County/xyz-3-agents-swarm)).
