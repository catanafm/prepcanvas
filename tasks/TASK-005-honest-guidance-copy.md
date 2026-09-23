---
id: TASK-005
title: Make next-action and session estimate guidance accurate
type: fix
status: backlog
priority: medium
area: ui
created: 2026-09-23
---

## Problem

- With no evidence, the next best action reads "Start the diagnostic check for “Systems thinking”", but the diagnostic covers the whole subject, not one topic.
- With no evidence, the overview shows "≈ 10 focused sessions", which is `(target − 0) / 8` and looks more precise than it is.
- The "Focused sessions" metric label is truncated at common desktop widths.

## Acceptance criteria

- [ ] No-profile state recommends the subject diagnostic without naming a topic
- [ ] The session estimate is hidden or shown as a range until each topic has evidence
- [ ] Metric labels are not truncated at 1280 px width
- [ ] Tests cover the next-action text for no-evidence, partial, and ready states
