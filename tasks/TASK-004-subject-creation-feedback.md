---
id: TASK-004
title: Show confirmation after creating a subject
type: fix
status: backlog
priority: medium
area: ui
created: 2026-09-23
---

## Context

Creating a subject is the first step for any real, non-demo use of the product.

## Problem

`app/streamlit_app.py` calls `st.success(...)` and then `st.rerun()` immediately, so the confirmation is discarded before it renders. Verified with `AppTest`: zero success messages after a successful create.

## Acceptance criteria

- [ ] A confirmation is visible after the rerun (for example via `st.toast` or a session-state flash message)
- [ ] The newly created subject is selected automatically
- [ ] An `AppTest` smoke test asserts the confirmation and selection
