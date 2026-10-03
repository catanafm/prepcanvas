---
id: TASK-045
title: Preserve non-English answers and declare grading language support
type: fix
status: done
priority: high
area: grading
created: 2026-09-29
---

## Context

Review finding from TASK-041 against commit 41021b8.

## Problem

Build prompts request the language of the materials, but normalize_text strips everything outside a-z and digits. A synthetic multiple-choice question with correct_answer="Да" awards full points to "Нет", while reporting is_answered=False. English suffix and negation rules also do not provide general multilingual grading.

## Acceptance criteria

- [x] Normalize Unicode text without dropping meaningful letters; different non-English options must remain distinguishable
- [x] Never award credit to an empty normalized answer or silently omit a meaningful answer from evidence
- [x] Define supported short-answer languages and show explicit limitations for unsupported morphology and negation
- [x] Make the build prompt, package validator, and grading feedback agree on language support
- [x] Cover Cyrillic options, accented Latin text, empty answers, accepted phrases, and supported-language negation with synthetic regressions

## Notes

Use synthetic content and temporary database/private directories. See [the review](../docs/reviews/2026-09-29.md).

## Implementation

Grading preserves Unicode and distinguishes non-English options; short-answer language support is explicit in packages, build prompts, validation, and feedback

Validation: focused regression tests and `./scripts/run_tests.sh -q`.
