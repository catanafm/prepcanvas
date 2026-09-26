---
id: TASK-036
title: Move through practice questions with Next and Random instead of a dropdown
type: feature
status: done
priority: high
area: ui
created: 2026-09-26
---

## Problem

Practice asks the learner to pick each question from a dropdown of full question texts. With sixty questions that is slow, and it hides which questions still need work.

## Acceptance criteria

- [x] Practice shows one question at a time with *Next question* and *Random question*; Next prefers questions never answered, then the ones answered longest ago
- [x] The question header says where the learner is: position in the focus, whether it was answered before, and the last score
- [x] The focus (all topics or one topic) still narrows the set; changing focus restarts the sequence
- [x] Covered by smoke tests
