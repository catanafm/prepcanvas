---
id: TASK-026
title: Build questions and rubrics from a practice exam and its answer key
type: feature
status: done
priority: high
area: ingestion
created: 2026-09-24
---

## Context

A practice exam plus a master solution is the most exam-like material a learner has. Rather than parsing institution-specific layouts deterministically, the build skill (TASK-027) reads them and writes questions with `origin: source`, and the validator (TASK-025) guarantees that every rubric is satisfiable.

## Acceptance criteria

- [x] The build skill turns numbered questions, points, and options from the practice exam into `origin: source` questions and takes answers and rubrics from the answer key
- [x] Similar new questions carry `origin: generated`, so the two sets stay distinguishable
- [x] The learner reviews every topic and question on the Content page before studying
- [x] Rubric points derived from model answers are checked by the validator (model answer earns full marks) and covered by tests with synthetic content only

## Notes

The earlier idea of a local `pypdf` parser for the target format was replaced: the agent reads the files directly, and text extraction moves to TASK-013.
