---
id: TASK-030
title: Run an installed CLI agent from the Content page
type: feature
status: backlog
priority: medium
area: ai
created: 2026-09-25
---

## Context

The Content page shows the command to give a coding agent (TASK-028). Running it from the app would remove the terminal step for learners who have `claude`, `codex`, or `gemini` installed.

## Acceptance criteria

- [ ] The app detects installed agents with `shutil.which` and offers a *Build with <agent>* button only when one is found
- [ ] The agent runs headless (`claude -p`, `codex exec`, `gemini -p`) as a detached process with the build request; the page shows progress from a log file and never blocks Streamlit
- [ ] The result is validated exactly like a manual build; errors are shown on the Content page
- [ ] The UI states which vendor receives the materials before the run starts

## Notes

Vendors have changed their rules for programmatic use of subscriptions several times in 2026; keep the launcher optional and the terminal path documented.
