---
id: TASK-011
title: Publish the first tagged release (v0.1.0)
type: chore
status: backlog
priority: medium
area: ci
created: 2026-09-23
---

## Context

Carried over from the former `TODO.md`.

## Acceptance criteria

- [ ] `CHANGELOG.md` **Unreleased** section is moved to `0.1.0` with a date
- [ ] Version in `pyproject.toml` and `prepcanvas.__version__` match the tag
- [ ] Annotated tag `v0.1.0` is pushed
- [ ] GitHub release notes are generated from the changelog
- [ ] Repository topics and description are set on GitHub

## Notes

Depends on TASK-002 and TASK-003 so the first release ships with trustworthy grading and readiness.
