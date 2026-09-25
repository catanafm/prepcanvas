---
id: TASK-016
title: Build packages fully offline with a local model
type: feature
status: backlog
priority: low
area: ai
created: 2026-09-23
---

## Context

The build step relies on the learner's own AI assistant (TASK-027). Learners who want nothing to leave the machine could use a local model through Ollama or a similar runtime.

## Acceptance criteria

- [ ] `python -m prepcanvas build --provider ollama <subject-id>` produces a package from the materials using the same schema document and validator
- [ ] The app remains fully functional with no provider configured
- [ ] The Content page explains the quality trade-off of small local models for rubric writing

## Notes

Decision (2026-09-25): bring-your-own-agent is the primary path; a local model is an optional, fully offline alternative and not a requirement.
