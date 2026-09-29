---
id: TASK-044
title: Return structured errors for malformed package values
type: fix
status: done
priority: high
area: content
created: 2026-09-29
---

## Context

Review finding from TASK-041 against commit 41021b8.

## Problem

validate_package records field errors but continues iterating invalid values. Replacing topics or questions with integer 1 in the sample package raises TypeError instead of returning issues. Content loads during library rendering, so malformed AI output can disrupt normal navigation.

## Acceptance criteria

- [x] Return structured issues for every JSON value at the root and nested schema fields without uncaught type or key errors
- [x] Skip dependent validation after container/type checks fail; reject unhashable topic references cleanly
- [x] Read invalid encodings and malformed JSON as PackageError with actionable messages
- [x] Keep the library, Content page, and CLI usable with an invalid package; preserve the candidate for correction
- [x] Add parameterized malformed-input cases and an AppTest recovery scenario

## Notes

Use synthetic content and temporary database/private directories. See [the review](../docs/reviews/2026-09-29.md).

## Implementation

Malformed package fields now return structured validation errors; the library, Content page, and CLI remain usable while invalid files are kept for correction

Validation: focused regression tests and `./scripts/run_tests.sh -q`.
