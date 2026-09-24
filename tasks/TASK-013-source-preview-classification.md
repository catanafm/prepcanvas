---
id: TASK-013
title: Extract text locally and preview each source
type: feature
status: backlog
priority: high
area: ingestion
created: 2026-09-23
---

## Acceptance criteria

- [ ] Text is extracted offline (`pypdf` for PDFs) and cached next to the upload
- [ ] Each file shows page count, a text preview, and what was detected (sections, questions)
- [ ] PDFs without a text layer are flagged with guidance instead of failing silently
- [ ] The learner can correct a file's role before processing
