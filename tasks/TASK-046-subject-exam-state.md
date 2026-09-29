---
id: TASK-046
title: Isolate active exam sessions by subject and sitting
type: fix
status: backlog
priority: high
area: ui
created: 2026-09-29
---

## Context

Review finding from TASK-041 against commit 41021b8.

## Problem

exam_run is keyed only by exam set and variant. AppTest with two synthetic subjects confirms that starting an exam in alpha, returning to the library, and opening the same exam set in beta reuses alpha's started_at and skips Start exam. Widget keys also omit subject and sitting identity.

## Acceptance criteria

- [ ] Bind each active run and answer widget to subject id, package revision, exam set, variant, and sitting identity
- [ ] Opening another subject never reuses its predecessor’s timer or answers
- [ ] Define and display whether navigating away resumes or abandons an exam, and preserve that policy consistently
- [ ] A fresh sitting starts with blank answers and a new timer; package changes cannot silently change an active exam
- [ ] Cover cross-subject switching, returning to a run, retaking an exam, and package replacement in AppTest

## Notes

Use synthetic content and temporary database/private directories. See [the review](../docs/reviews/2026-09-29.md).
