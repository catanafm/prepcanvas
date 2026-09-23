---
id: TASK-012
title: Upload local PDF, TXT, and Markdown materials
type: feature
status: backlog
priority: medium
area: ingestion
created: 2026-09-23
---

## Context

Roadmap stage 2. Newly created subjects currently store only metadata; this is the step that makes the product useful for a real private subject.

## Acceptance criteria

- [ ] Files are uploaded per subject and stored under `data/uploads/` (git-ignored)
- [ ] PDF text extraction works offline without a cloud service
- [ ] Upload errors are recoverable and explained in the UI
- [ ] No uploaded content leaves the machine
