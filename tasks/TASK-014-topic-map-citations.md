---
id: TASK-014
title: Show structured citations for topics and questions
type: feature
status: backlog
priority: high
area: ingestion
created: 2026-09-23
---

## Context

Every topic and question already carries a human-readable `source` label written by the build skill. Structured citations (source id, page or section) would let the app link back into the material and check coverage.

## Acceptance criteria

- [ ] The package schema gains an optional `citations` list per topic and question (`source_id`, `locator`), validated against `sources`
- [ ] The build skill fills citations when the materials allow
- [ ] Learn and feedback screens display the citation next to the source label
- [ ] The Content review lists topics without citations

## Review update — 2026-09-29

Treat traceability as the next product milestone after TASK-042–TASK-046, not presentation polish. Schema validity and model-answer self-checks cannot verify that a claim is supported by its source.

- [ ] Citations resolve to a subject-local source and a real page/section; missing or unresolved references are visible
- [ ] Feedback lets the learner inspect the supporting excerpt locally, with a text fallback when a document preview is unavailable
- [ ] Tests cover missing sources, invalid locators, and legacy packages with labels only
