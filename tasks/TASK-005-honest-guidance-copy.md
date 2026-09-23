---
id: TASK-005
title: Make next-action and session estimate guidance accurate
type: fix
status: done
priority: medium
area: ui
created: 2026-09-23
---

## Problem

- With no evidence, the next best action reads "Start the diagnostic check for “Systems thinking”", but the diagnostic covers the whole subject, not one topic.
- With no evidence, the overview shows "≈ 10 focused sessions", which is `(target − 0) / 8` and looks more precise than it is.
- The "Focused sessions" metric label is truncated at common desktop widths.

## Acceptance criteria

- [x] No-profile state recommends the subject diagnostic without naming a topic
- [x] The session estimate is hidden or shown as a range until each topic has evidence
- [x] Metric labels are not truncated at 1280 px width
- [x] Tests cover the next-action text for no-evidence, partial, and ready states

## Notes

Resolution: `estimated_sessions` is `None` until coverage is 100%, then `ceil((target − readiness) / 8)`; the overview shows "—" with an explanatory tooltip. The metric is labelled "Est. sessions". The next best action now has four states: no evidence → diagnostic, partial coverage → first unanswered topic, full coverage → weakest topic, ready → mock exam.
