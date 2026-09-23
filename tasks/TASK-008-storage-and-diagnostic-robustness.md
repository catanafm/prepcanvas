---
id: TASK-008
title: Close SQLite connections and guard content assumptions
type: refactor
status: backlog
priority: medium
area: storage
created: 2026-09-23
---

## Problem

- `StudyStore` uses `with sqlite3.connect(...)`, which commits but does not close the connection; every call leaks a handle until garbage collection.
- Foreign keys are declared but `PRAGMA foreign_keys` is never enabled.
- The diagnostic calls `next(...)` for a multiple-choice question per topic and raises `StopIteration` when a topic has none — this will break once real materials are ingested.
- `catalog.get_topic` and `get_question` raise bare `StopIteration` for unknown IDs.

## Acceptance criteria

- [ ] Connections are closed deterministically (context manager with `closing`)
- [ ] Foreign key enforcement is enabled
- [ ] Topics without a multiple-choice question are skipped by the diagnostic, with a test
- [ ] Unknown topic or question IDs raise a descriptive `KeyError`
