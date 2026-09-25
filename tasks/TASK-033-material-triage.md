---
id: TASK-033
title: Triage materials before building so only study material becomes content
type: feature
status: in-progress
priority: high
area: ai
created: 2026-09-25
---

## Context

The build skill reads every file in the materials folder. A CV, an invoice, or a file from another course dropped there by mistake would become topics and questions.

## Acceptance criteria

- [ ] The skill and the chat prompt classify every file by role (course book, practice exam, answer key, notes, transcript) before reading for content, exclude files that are not study material for this subject, and name the excluded files and the reason in the report
- [ ] With no course book and no practice exam among the files, or with files that belong to different courses, the agent stops and asks instead of building
- [ ] `sources` in the package lists only the files that were used; the validator warns about a listed file that does not exist next to the package
- [ ] Covered by tests for the validator part
