---
id: TASK-043
title: Preserve existing data when an import or replacement fails
type: fix
status: done
priority: high
area: storage
created: 2026-09-29
---

## Context

Review finding from TASK-041 against commit 41021b8.

## Problem

transfer.import_subject deletes the existing database record and subject folder before importing the new payload. Replacing a synthetic existing subject with attempts=[{}] raises KeyError and leaves both its record and materials deleted. The Content page also overwrites package.json before validating the candidate.

## Acceptance criteria

- [x] Validate the entire archive, package, attempts, profile, and materials before replacing an existing subject
- [x] Stage filesystem writes and coordinate database commit with recoverable file promotion; retain the previous state until success
- [x] On validation, disk-write, or database failure, preserve the original record, progress, materials, brief, and package
- [x] Validate uploaded package.json before promotion; keep the last valid package active if the candidate fails
- [x] Show a recoverable import error and cover failures at each stage using synthetic fixtures and injected failures

## Notes

Use synthetic content and temporary database/private directories. See [the review](../docs/reviews/2026-09-29.md).

## Implementation

Archive replacement validates and stages the complete subject before committing, restores previous data on failures, and preserves the active package when a JSON upload is rejected

Validation: focused regression tests and `./scripts/run_tests.sh -q`.
