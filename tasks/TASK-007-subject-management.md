---
id: TASK-007
title: Add subject deletion and progress reset
type: feature
status: done
priority: medium
area: storage
created: 2026-09-23
---

## Context

Real use involves several subjects over time and occasional fresh starts before an exam.

## Problem

Subjects and attempts can only be created. There is no way to delete a subject, reset its progress, or retake the diagnostic from a clean state.

## Acceptance criteria

- [x] A user subject can be deleted together with its attempts and coaching profile
- [x] Progress for any subject, including the demo, can be reset
- [x] Destructive actions require explicit confirmation in the UI
- [x] The demo subject itself cannot be deleted
- [x] Storage tests cover cascade deletion and reset

## Notes

Resolution: `StudyStore.reset_progress` and `StudyStore.delete_subject` run in one transaction each; deleting the demo raises `ValueError`. Each subject on the Subjects page has a *Manage subject* expander with a confirmation checkbox that enables *Reset progress* and, for user subjects, *Delete subject*. Deleting the selected subject switches the sidebar back to the demo and shows a toast.
