---
id: TASK-009
title: Move to a supported Python baseline and tidy packaging
type: chore
status: backlog
priority: low
area: ci
created: 2026-09-23
---

## Problem

- Python 3.9 reached end of life in October 2025; local setup defaults to the Command Line Tools interpreter.
- `pyproject.toml` uses an SPDX `license = "MIT"` string, which requires `setuptools>=77`, but declares `setuptools>=68`.
- ~~`catalog.ROOT_DIR` is unused.~~ Removed in TASK-008.
- Development dependencies are split between `requirements.txt`, the `dev` extra, and ad hoc `pip install pytest` in scripts.

## Acceptance criteria

- [ ] `requires-python = ">=3.11"`; CI matrix covers 3.11 and 3.12 (or newer)
- [ ] `setup.sh` prefers a supported interpreter and explains how to install one
- [ ] Build requirement is `setuptools>=77`
- [ ] Scripts and CI install dev dependencies from one place
- [ ] Unused code is removed
