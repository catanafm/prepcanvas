---
id: TASK-047
title: Build and validate a private subject package
type: chore
status: in-progress
priority: medium
area: packages
created: 2026-09-29
---

## Context

A learner requested a local subject build using the existing build skill.

## Problem

The supplied private materials need a validated study package.

## Acceptance criteria

- [ ] Triage and read all supplied materials; retain source provenance locally.
- [ ] Build source-grounded lessons, questions, rubrics, and an exam-sized variant pool.
- [ ] Validate the package and run the existing test suite with temporary storage.
- [ ] Keep all source content and generated study artifacts in ignored private storage.

## Notes

No application code changes. Git metadata writes are denied in this workspace, preventing refresh of main and creation of the task branch. No private content belongs in this task or the changelog.
