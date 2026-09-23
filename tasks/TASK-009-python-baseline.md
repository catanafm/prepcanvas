---
id: TASK-009
title: Test supported Python versions and tidy packaging
type: chore
status: done
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

- [x] CI matrix covers Python 3.9, 3.11, 3.12, and 3.13
- [x] `setup.sh` prefers the newest available interpreter and recommends 3.12 when only an older one is found
- [x] Build requirement is `setuptools>=77`
- [x] Scripts and CI install dev dependencies from one place (`requirements.txt`), with a test that keeps its pins in sync with `pyproject.toml`
- [x] Unused code is removed

## Notes

Decision (2026-09-23): the maintainer's machine only has Python 3.9, so the minimum stays at 3.9 for now and raising it to 3.11 moved to TASK-019. The original criterion `requires-python = ">=3.11"` was replaced by broader CI coverage.

Resolution: interpreter selection lives in `scripts/_python.sh`, shared by `setup.sh` and `rebuild_venv.sh`; it skips Anaconda's `python3` in favour of the system interpreter unless `PYTHON_BIN` is set. Setup also upgrades pip inside `.venv`. `pyproject.toml` gains Python version classifiers.
