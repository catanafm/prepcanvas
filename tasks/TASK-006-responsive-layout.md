---
id: TASK-006
title: Complete visual QA and improve the mobile layout
type: feature
status: done
priority: medium
area: ui
created: 2026-09-23
---

## Context

Carried over from the former `TODO.md` ("Complete visual QA at desktop and mobile widths").

## Problem

At 375 px width the four overview metrics stack into a full screen of cards, and navigation is hidden in the collapsed sidebar. The Streamlit "Deploy" toolbar button is visible even though the app is local-first.

## Acceptance criteria

- [x] Overview metrics render as a 2 × 2 grid on narrow screens
- [x] Primary navigation is reachable without opening the sidebar on mobile
- [x] `client.toolbarMode = "minimal"` hides developer toolbar items
- [x] Every page is checked at 375 px and 1280 px; findings are noted in this task

## Notes

Resolution:

- Navigation is a horizontal `st.radio` styled as pills (`.st-key-page`). `st.segmented_control` was tried first, but Streamlit 1.50's `AppTest` cannot serialize a single-select button group once any other widget reruns the app, which broke the smoke tests.
- Metrics use a small `render_metrics` helper that emits a CSS grid; below 640 px it switches to two columns and the hero heading shrinks.
- `client.toolbarMode = "minimal"` in `.streamlit/config.toml`.

Visual QA:

| Width | Screen | Finding |
|---|---|---|
| 375 px | Overview | Pills wrap to three rows, metrics are 2 × 2, no developer toolbar. |
| 375 px | Practice | Navigation reachable, answer radios keep their normal styling. |
| 1280 px | Overview | Pills fit one row, four metrics in one row, no label truncation. |

The subject selector stays in the sidebar; switching subjects on a phone still needs the sidebar toggle, which is acceptable because it is infrequent.
