---
id: TASK-002
title: Make rubric grading robust to word forms and spelling variants
type: fix
status: backlog
priority: high
area: grading
created: 2026-09-23
---

## Context

Short-answer grading is the core feedback loop. False negatives tell a learner they are wrong when they are right, which erodes trust faster than any other defect.

## Problem

`grading.py` matches rubric keywords as exact tokens. Observed results on the demo subject:

| Question | Answer | Score | Expected |
|---|---|---|---|
| `circ-3` | "Durability and repairability." | 0/2 | 2/2 |
| `circ-3` | "Make it repairable and long lasting." | 0/2 | 2/2 |
| `circ-3` | "The product should be not only durable but also modular." | 1/2 | 2/2 |
| `sys-3` | "It ignores trade offs; the system boundary is narrow." | 1/2 | 2/2 |
| `carbon-3` | "Scope one is direct, scope two is purchased energy, scope three covers the value chain." | 0/3 | 3/3 |

Causes: no stemming or inflection handling, hyphenated keywords do not match spaced or joined spellings, number words are not normalised, and the negation guard rejects "not only … but also".

Conversely, an answer made only of rubric keywords with no sentence structure receives full credit.

## Acceptance criteria

- [ ] Keywords match common inflections (`durable` ↔ `durability`, `repair` ↔ `repairable`)
- [ ] Hyphenated, spaced, and joined spellings are equivalent (`trade-offs`, `trade offs`, `tradeoffs`)
- [ ] Number words one–ten are normalised to digits
- [ ] "not only X but also Y" credits X
- [ ] Every example in the table above is a regression test with the expected score
- [ ] Existing negation and scope-binding tests still pass
- [ ] A bare keyword list does not receive full credit on multi-point questions

## Notes

Keep grading deterministic and dependency-free; a small suffix-stripping stemmer is sufficient. Semantic grading belongs to the optional AI provider stage.
