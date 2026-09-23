---
id: TASK-019
title: Raise the minimum Python version to 3.11
type: chore
status: backlog
priority: low
area: ci
created: 2026-09-23
---

## Context

Python 3.9 reached end of life in October 2025. TASK-009 kept 3.9 as the minimum because the maintainer's machine only has 3.9 (Command Line Tools and Anaconda).

## Acceptance criteria

- [ ] Python 3.12 is installed locally and `.venv` is rebuilt with it
- [ ] `requires-python = ">=3.11"` and classifiers updated
- [ ] CI matrix drops 3.9 and 3.10
- [ ] README requirements updated
- [ ] Code may use 3.10+ syntax (`X | None`, `match`) where it improves clarity
