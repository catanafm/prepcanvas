---
id: TASK-039
title: Time the mock exam like the real one
type: feature
status: done
priority: high
area: ui
created: 2026-09-26
---

## Context

Exam variants now mirror the real exam's structure and points, but not its clock. Working under time pressure is the part of exam simulation that practice cannot give.

## Acceptance criteria

- [x] `exam_blueprint` may carry `duration_minutes`; the build skill takes it from the practice exam when stated, and the validator checks it
- [x] The Mock exam page hides the questions until *Start exam*; the learner can keep the blueprint duration, set another, or switch the limit off
- [x] A live countdown shows the remaining time; when it runs out, the page says so and unanswered questions can be handed in as blanks that score zero
- [x] Each sitting records the limit and the time used; results and the Progress list show them, including sittings handed in after the limit
- [x] Covered by tests
