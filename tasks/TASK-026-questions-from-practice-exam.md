---
id: TASK-026
title: Build questions and rubrics from a practice exam and its answer key
type: feature
status: backlog
priority: high
area: ingestion
created: 2026-09-24
---

## Context

A practice exam plus a master solution is the most exam-like material a learner has. The earlier private prototype parsed both locally with `pypdf`; that approach is proven for the target format.

## Acceptance criteria

- [ ] Numbered questions, points, and multiple-choice options are extracted from the practice exam text locally
- [ ] Model answers are matched from the answer key by question number
- [ ] Rubric points (accepted phrases and keywords) are derived from each model answer and can be edited before saving
- [ ] The learner reviews every extracted question before it enters the subject package
- [ ] Parsers are tested against synthetic exam documents only
