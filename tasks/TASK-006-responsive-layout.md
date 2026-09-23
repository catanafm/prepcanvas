---
id: TASK-006
title: Complete visual QA and improve the mobile layout
type: feature
status: backlog
priority: medium
area: ui
created: 2026-09-23
---

## Context

Carried over from the former `TODO.md` ("Complete visual QA at desktop and mobile widths").

## Problem

At 375 px width the four overview metrics stack into a full screen of cards, and navigation is hidden in the collapsed sidebar. The Streamlit "Deploy" toolbar button is visible even though the app is local-first.

## Acceptance criteria

- [ ] Overview metrics render as a 2 × 2 grid on narrow screens
- [ ] Primary navigation is reachable without opening the sidebar on mobile
- [ ] `client.toolbarMode = "minimal"` hides developer toolbar items
- [ ] Every page is checked at 375 px and 1280 px; findings are noted in this task
