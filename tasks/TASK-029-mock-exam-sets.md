---
id: TASK-029
title: Let the mock exam replay the practice exam or a generated variant
type: feature
status: done
priority: medium
area: ui
created: 2026-09-25
---

## Context

Packages label questions with `origin: source` (from the learner's practice exam) or `origin: generated` (new similar questions). Sitting the original exam and then a fresh variant is the closest thing to exam simulation the materials allow.

## Acceptance criteria

- [x] When a package contains both origins, the Mock exam page offers *Practice exam from your materials*, *New variant with generated questions*, and *Everything*
- [x] Only the chosen set is shown, graded, and saved; single-origin packages behave as before
- [x] Covered by a smoke test
