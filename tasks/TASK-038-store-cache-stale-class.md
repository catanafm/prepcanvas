---
id: TASK-038
title: Stop caching the StudyStore across code reloads
type: fix
status: done
priority: high
area: storage
created: 2026-09-26
---

## Problem

`get_store` is wrapped in `st.cache_resource`, so a running app keeps the `StudyStore` instance created from the old class after `storage.py` changes. After pulling the exam-variant release, the Mock exam page crashed with `'StudyStore' object has no attribute 'list_sittings'` until the app was restarted.

## Acceptance criteria

- [x] The store is created per run; opening SQLite and running the idempotent migrations costs milliseconds
- [x] Pulling a new version no longer requires a restart for storage changes
