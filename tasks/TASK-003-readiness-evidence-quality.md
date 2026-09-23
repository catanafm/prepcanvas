---
id: TASK-003
title: Base readiness on distinct questions and recent, mode-weighted evidence
type: fix
status: backlog
priority: high
area: readiness
created: 2026-09-23
---

## Context

Readiness is the headline metric on the overview screen. It should reflect demonstrated knowledge across a topic, not repetition.

## Problem

`calculate_readiness` treats every saved attempt as independent evidence. Answering the same question (`sys-1`) three times yields `evidence: 3`, and three correct repeats yield 100% topic mastery. Diagnostic, practice, and mock-exam answers carry equal weight, and evidence never ages.

## Acceptance criteria

- [ ] Evidence counts distinct questions; repeated answers to one question use the latest result
- [ ] Mock-exam answers weigh more than practice answers
- [ ] Older evidence decays so mastery reflects the current state
- [ ] Repeating a single question cannot push a topic to full mastery
- [ ] `docs/architecture.md` describes the updated heuristic
- [ ] Unit tests cover repetition, mode weighting, and decay

## Notes

Keep the heuristic explainable in one paragraph; transparency is a product principle.
