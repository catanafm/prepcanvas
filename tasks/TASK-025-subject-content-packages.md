---
id: TASK-025
title: Store study content for user subjects as local packages
type: feature
status: backlog
priority: high
area: storage
created: 2026-09-24
---

## Context

Only the bundled demo has topics and questions; user subjects store metadata only. Every ingestion step (TASK-012 → TASK-014) needs a place to put its output.

## Acceptance criteria

- [ ] A documented subject package schema (topics, questions, rubrics, sources, citations) shared by the demo and user subjects
- [ ] Packages for user subjects are saved under `data/private/subjects/` (git-ignored) and loaded by the app
- [ ] Packages are validated on load with clear errors
- [ ] A user subject with a valid package works in Diagnostic, Learn, Practice, Mock exam, and Progress
- [ ] Tests use synthetic packages only
