---
id: TASK-032
title: Compose numbered mock-exam variants from a question pool and an exam blueprint
type: feature
status: in-progress
priority: high
area: ui
created: 2026-09-25
---

## Context

A learner has one real practice exam. Sitting it once teaches its answers, not the subject. Twenty variants with the same structure, drawn from a pool of questions written strictly from the course book, are the closest thing to exam simulation the materials allow.

## Problem

The mock exam shows every question of the chosen origin at once, so a "new variant" is always the same set, and its length and points never match the real exam.

## Acceptance criteria

- [ ] The package may carry an `exam_blueprint`: ordered sections with question `type`, `count`, and `points` per question, taken from the practice exam; the validator checks that the pool can fill every section and reports what is missing
- [ ] `Variant N` is composed deterministically from the pool by the blueprint, spread across topics, so variant 4 is always the same exam and variant 5 differs; variants may share questions
- [ ] The Mock exam page offers the original practice exam, a numbered variant (default: the first not yet sat), a random variant, and everything, and states the structure and total points of the chosen set
- [ ] Each submission is saved as one sitting with its variant; the Progress page lists mock-exam sittings with variant, date, and score
- [ ] The build skill, the chat prompt, and the schema document ask for the blueprint and for a pool of at least three questions per section slot spread across topics, with point values that match the blueprint
- [ ] Covered by tests
