---
id: TASK-048
title: Exempt private study content from repository task tracking
type: docs
status: done
priority: medium
area: docs
created: 2026-10-03
---

## Context

Repository tasks track changes to PrepCanvas itself. Generating a learner's private study content is app usage and must not create public planning or release records.

## Acceptance criteria

- [x] AGENTS.md, CONTRIBUTING.md, and the build skill explicitly exempt private content work from task, branch, commit, PR, and changelog requirements
- [x] Source materials, generated packages, extracts, reports, and intermediate artifacts remain in ignored private storage
- [x] Remove the mistakenly created private-build task and its board/release entries without touching the content
- [x] Confirm representative private outputs are git-ignored and task metadata remains consistent

## Notes

This task tracks the repository convention change, not a learner's content build. Retire TASK-047; do not reuse its id.
