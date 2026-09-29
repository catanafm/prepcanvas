---
id: TASK-042
title: Confine subject archives to validated private paths
type: fix
status: done
priority: high
area: storage
created: 2026-09-29
---

## Context

Review finding from TASK-041 against commit 41021b8.

## Problem

The archive manifest id is passed directly to SubjectFiles.subject_dir. A synthetic archive with id `../../escaped` writes brief.json outside the private subjects directory. safe_material_name only protects material filenames, not the subject id. See transfer.py:46 and 70–81, packages.py:subject_dir.

## Acceptance criteria

- [x] Validate archive ids as strict subject slugs before any database or filesystem mutation; reject absolute paths and traversal
- [x] Enforce resolved-path containment in SubjectFiles, including symlink escapes, and reserve the bundled sample id from user imports
- [x] Validate the manifest shape and archive member names; reject collisions after filename normalization
- [x] Bound member count and total uncompressed bytes before extraction and report ArchiveError without a traceback
- [x] Add synthetic traversal, absolute-path, symlink, malformed-manifest, and archive-limit regression tests

## Notes

Use synthetic content and temporary database/private directories. See [the review](../docs/reviews/2026-09-29.md).

## Implementation

Subject archives now reject unsafe ids, paths, links, duplicate filenames, malformed manifests, and oversized contents before import; subject storage rejects symlink escapes

Validation: focused regression tests and `./scripts/run_tests.sh -q`.
