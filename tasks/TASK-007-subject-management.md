---
id: TASK-007
title: Add subject deletion and progress reset
type: feature
status: backlog
priority: medium
area: storage
created: 2026-09-23
---

## Context

Real use involves several subjects over time and occasional fresh starts before an exam.

## Problem

Subjects and attempts can only be created. There is no way to delete a subject, reset its progress, or retake the diagnostic from a clean state.

## Acceptance criteria

- [ ] A user subject can be deleted together with its attempts and coaching profile
- [ ] Progress for any subject, including the demo, can be reset
- [ ] Destructive actions require explicit confirmation in the UI
- [ ] The demo subject itself cannot be deleted
- [ ] Storage tests cover cascade deletion and reset
