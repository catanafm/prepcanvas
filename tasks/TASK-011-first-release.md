---
id: TASK-011
title: Publish the first tagged release (v0.1.0)
type: chore
status: done
priority: medium
area: ci
created: 2026-09-23
---

## Context

Carried over from the former `TODO.md`.

## Acceptance criteria

- [x] `CHANGELOG.md` **Unreleased** section is moved to `0.1.0` with a date
- [x] Version in `pyproject.toml` and `prepcanvas.__version__` match the tag
- [x] Annotated tag `v0.1.0` is pushed
- [x] GitHub release notes are generated from the changelog
- [x] Repository topics and description are set on GitHub

## Notes

Depends on TASK-002 and TASK-003 so the first release ships with trustworthy grading and readiness.

Resolution: released on 2026-09-23 as `v0.1.0` (annotated tag on the squash-merge commit of this task). Release notes are the `0.1.0` changelog section. Repository topics: `education`, `exam-preparation`, `learning`, `local-first`, `python`, `spaced-repetition`, `sqlite`, `streamlit`.
