---
id: TASK-016
title: Add an optional local-model provider interface
type: feature
status: backlog
priority: low
area: ai
created: 2026-09-23
---

## Acceptance criteria

- [ ] A provider interface with explicit opt-in via `PREPCANVAS_AI_PROVIDER`
- [ ] A local-model adapter implements it
- [ ] The app remains fully functional with no provider configured
- [ ] Outputs include source citations and are validated before display

## Notes

Decision (2026-09-24): ingestion is deterministic and local first (TASK-012 → TASK-014, TASK-026). A local model via Ollama may later add summaries and rubric suggestions; content still comes from the learner's own files and no material leaves the machine.
