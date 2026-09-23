---
id: TASK-001
title: Establish task board and contribution workflow
type: docs
status: done
priority: high
area: tasks
created: 2026-09-23
---

## Context

The project is developed incrementally and is also a public portfolio piece. Changes should be traceable from a planned task to a branch, commits, a pull request, and a changelog entry.

## Problem

Planning lived in a flat `TODO.md` checklist without IDs, priorities, or acceptance criteria, and there were no branch, commit, or pull request conventions.

## Acceptance criteria

- [x] Task files with IDs (`TASK-NNN`), front matter, and acceptance criteria live in `tasks/`
- [x] A task board lists every task with type, priority, and status
- [x] `CONTRIBUTING.md` defines branch, commit, pull request, and done conventions
- [x] A pull request template and a changelog exist
- [x] Agent instructions (`AGENTS.md`, `CLAUDE.md`) reference the workflow
- [x] Tests verify that the board and task files stay in sync
- [x] Findings from the first project review and the former `TODO.md` items are captured as tasks

## Notes

`TODO.md` is replaced by the task board.
