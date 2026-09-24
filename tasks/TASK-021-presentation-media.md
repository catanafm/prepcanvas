---
id: TASK-021
title: Capture diagnostic and progress media and extend the demo GIF
type: docs
status: done
priority: medium
area: docs
created: 2026-09-24
---

## Context

TASK-010 added five screenshots and a 13-second GIF. The learning journey is missing the diagnostic result and the progress page, and the GIF ends on the overview.

## Acceptance criteria

- [x] Screenshot of the diagnostic result with the recommended coaching strategy
- [x] Screenshot of the progress page with synthetic history
- [x] GIF of about 20–30 seconds: Diagnostic → Learn → Practice → Feedback → Progress, under 5 MB
- [x] README embeds the new media

## Notes

Resolution: `capture_media.py` now also saves `diagnostic.png` and `progress.png`, and the GIF has eight frames over 25.5 seconds (Diagnostic → answered → strategy → Learn → explanation → Practice → Correct feedback → Progress), about 350 KB. All media were regenerated so they include the TASK-020 fixes.
