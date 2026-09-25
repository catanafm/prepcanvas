---
id: TASK-013
title: Cache extracted text so every agent can read PDF and DOCX materials
type: feature
status: backlog
priority: medium
area: ingestion
created: 2026-09-23
---

## Context

Some CLI agents cannot open PDF or DOCX files. A plain-text copy next to each material makes the build skill (TASK-027) vendor-neutral by construction and lets the Content page show what was detected.

## Acceptance criteria

- [ ] Text is extracted offline (`pypdf` for PDFs, `python-docx` or zip parsing for DOCX) into `materials/.text/<file>.txt`, as an optional dependency the app works without
- [ ] The Content page shows page count and a short preview per file
- [ ] PDFs without a text layer are flagged with guidance instead of failing silently
- [ ] The build skill points agents to the cached text when it exists
- [ ] Covered by tests with synthetic documents only
