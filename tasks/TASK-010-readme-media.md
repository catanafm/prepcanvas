---
id: TASK-010
title: Add screenshots and a short demo GIF to the README
type: docs
status: done
priority: medium
area: docs
created: 2026-09-23
---

## Context

Carried over from the former `TODO.md`. The repository is shared publicly, so the README should show the product within seconds.

## Acceptance criteria

- [x] Screenshots of Overview, Learn, Practice feedback, and Mock exam results in `docs/media/`
- [x] A GIF under 5 MB showing diagnostic → learn → practice
- [x] Media use only the synthetic demo subject
- [x] README embeds the media near the top

## Notes

Capture after TASK-005 and TASK-006 so the images reflect the improved UI.

Resolution: `scripts/capture_media.py` seeds a temporary database with synthetic progress, starts the app, and drives headless Chrome over the DevTools protocol (via `tornado`, already a Streamlit dependency), so no extra tooling is required. It captures five PNGs at 2× (overview, learn, practice feedback, mock exam, phone overview) and a 7-frame, 960 px GIF of about 330 KB.
