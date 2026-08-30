---
name: vscode-color
description: |
  MOVED to giant-brains-swe-skills (04-toolbox/vscode-color) — invoke it from there. Original triggers follow.
  Give a git repo a stable, distinct VS Code background tint so windows are
  tellable apart at a glance. The color is scoped to the workspace
  (.vscode/settings.json under workbench.colorCustomizations), so it applies every
  session with no per-session step. Two modes: deterministic (SHA-256 of the repo's
  GitHub slug -> a hue, same repo always same color) and manual override (the user
  names a color or feel). Tints seven surfaces — editor, sidebar, activity bar,
  panel, active tab, title bar, status bar — tuned subtle for dark themes, with a
  --light variant.

  Trigger when the user says "tint this repo", "give this workspace a background
  color", "make this window a different color", "set the editor background for this
  repo", "color-code my repos", or "/vscode-repo-tint". Also offer it unprompted
  when a user complains they can't tell two VS Code windows apart.

  Not for global/user-level VS Code theming (this writes per-repo workspace settings
  only) and not for non-git folders (the deterministic color is keyed off the git
  remote slug).
---

# vscode-color — moved

This skill now lives in [giant-brains-swe-skills](https://github.com/Claude-AI-Tools-Ventura-County/giant-brains-swe-skills/tree/main/04-toolbox/vscode-color). Install it from there and invoke that copy; this stub exists for one release so existing symlinks keep resolving, and will be removed in the release after v1.1.0.

```bash
git clone https://github.com/Claude-AI-Tools-Ventura-County/giant-brains-swe-skills.git && cd giant-brains-swe-skills && ln -s "$PWD/04-toolbox/vscode-color" ~/.claude/skills/vscode-color
```
