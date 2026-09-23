---
id: TASK-003
title: Base readiness on distinct questions and recent, mode-weighted evidence
type: fix
status: done
priority: high
area: readiness
created: 2026-09-23
---

## Context

Readiness is the headline metric on the overview screen. It should reflect demonstrated knowledge across a topic, not repetition.

## Problem

`calculate_readiness` treats every saved attempt as independent evidence. Answering the same question (`sys-1`) three times yields `evidence: 3`, and three correct repeats yield 100% topic mastery. Diagnostic, practice, and mock-exam answers carry equal weight, and evidence never ages.

## Acceptance criteria

- [x] Evidence counts distinct questions; repeated answers to one question use the latest result
- [x] Mock-exam answers weigh more than practice answers
- [x] Older evidence decays so mastery reflects the current state
- [x] Repeating a single question cannot push a topic to full mastery
- [x] `docs/architecture.md` describes the updated heuristic
- [x] Unit tests cover repetition, mode weighting, and decay

## Notes

Keep the heuristic explainable in one paragraph; transparency is a product principle.

Resolution: mode weight 1.5× for mock exams, 14-day half-life, and three distinct questions for full evidence. `calculate_readiness` accepts an explicit `now` so decay is deterministic in tests. The overview caption changed from "recent evidence points" to "N of M questions answered".
