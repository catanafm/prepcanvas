---
id: TASK-012
title: Upload study materials by role in a new-subject wizard
type: feature
status: backlog
priority: high
area: ingestion
created: 2026-09-23
---

## Context

Roadmap stage 2. Creation becomes a guided wizard: basics → upload materials → review → ready.

## Acceptance criteria

- [ ] The wizard collects name, exam date, and target, then accepts files by role: workbook / course book, practice exam, answer key / model answers, notes, transcripts
- [ ] PDF, TXT, and Markdown files are stored under `data/uploads/<subject>/` (git-ignored); files can be listed and removed
- [ ] Size limits and unsupported formats are explained in the UI
- [ ] No uploaded content leaves the machine; the privacy promise is stated next to the upload control
