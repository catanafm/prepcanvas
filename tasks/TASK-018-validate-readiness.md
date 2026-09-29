---
id: TASK-018
title: Validate readiness against mock-exam trends
type: feature
status: backlog
priority: medium
area: readiness
created: 2026-09-23
---

## Acceptance criteria

- [ ] The progress page charts mock-exam scores over time next to readiness
- [ ] Divergence between readiness and mock results is surfaced to the learner
- [ ] Findings feed back into the readiness heuristic documentation

## Review update — 2026-09-29

Run after grading and exam-state fixes. Distinguish a repeated question from independent evidence; the same question pool powers coaching, practice, and mock exams. Do not describe a chart alone as validation against real outcomes.

- [ ] Compare readiness with the next completed mock sitting using only evidence available before that sitting
- [ ] Separate first-seen questions from repeated items and timed/on-time sittings from untimed/overtime sittings
- [ ] Document sample size, selection limitations, and uncertainty; use synthetic examples in the public repository
- [ ] Document and test what happens to prior evidence when a package changes question content or reuses ids
