---
id: TASK-014
title: Show structured citations for topics and questions
type: feature
status: backlog
priority: medium
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
