---
id: TASK-012
title: Add study materials to a subject from the Content page
type: feature
status: done
priority: high
area: ingestion
created: 2026-09-23
---

## Context

Roadmap stage 2. Materials are the input for the build step (TASK-027, TASK-028). They are files on disk, so an AI agent can read them, and they never leave the machine through PrepCanvas.

## Acceptance criteria

- [x] The subject's Content page accepts PDF, TXT, Markdown, and DOCX files and stores them under `data/private/subjects/<subject-id>/materials/` (git-ignored); files can be listed and removed
- [x] Size limits and unsupported formats are explained in the UI
- [x] PrepCanvas never sends the files anywhere; the privacy statement next to the upload control says so and names the assistant the learner chooses as the only recipient
- [x] Covered by tests

## Notes

The original wizard step "files by role" was dropped: the build skill infers roles (workbook, practice exam, answer key, notes) from the content, and a role picker added friction without improving the result.
