---
id: TASK-022
title: Publish the v0.1.1 presentation polish release
type: chore
status: done
priority: medium
area: ci
created: 2026-09-24
---

## Acceptance criteria

- [x] `CHANGELOG.md` **Unreleased** section is moved to `0.1.1` with a date
- [x] Version in `pyproject.toml` and `prepcanvas.__version__` is `0.1.1`
- [x] Annotated tag `v0.1.1` is pushed
- [x] GitHub release notes are generated from the changelog

## Notes

Ships TASK-020 and TASK-021. Tag and release are created immediately after this task is merged.
