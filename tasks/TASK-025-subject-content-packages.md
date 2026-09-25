---
id: TASK-025
title: Store study content for user subjects as validated local packages
type: feature
status: done
priority: high
area: storage
created: 2026-09-24
---

## Context

Only the bundled demo had topics and questions; user subjects stored metadata only. Every way of producing content, an AI agent, a chat assistant, or a text editor, needs one documented target format and a strict check before the app trusts it.

## Acceptance criteria

- [x] A documented subject package schema (topics, questions, rubrics, sources, origin) in `docs/subject-package.md`, shared by the sample and user subjects; the sample JSON is a valid package
- [x] Packages for user subjects are saved under `data/private/subjects/<subject-id>/package.json` (git-ignored, overridable with `PREPCANVAS_PRIVATE_DIR`) and loaded by the app
- [x] Packages are validated on load and with `python -m prepcanvas validate`: structural checks, cross-references, package id equal to the subject id, and a rubric self-check that grades every model answer against its own rubric; errors block loading, warnings are shown
- [x] A user subject with a valid package works in Diagnostic, Learn, Practice, Mock exam, and Progress
- [x] Tests use synthetic packages only

## Notes

The rubric self-check is what makes AI-written rubrics safe to trust: an assistant can iterate locally until the validator passes. Deterministic grading is unchanged.
