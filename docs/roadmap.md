# Roadmap

The [task board](../tasks/README.md) is the source of truth for status and order. The [2026-09-29 review](reviews/2026-09-29.md) explains the current priorities.

## Delivered foundation

The tagged v0.1.1 release demonstrates the synthetic study loop. Current main additionally implements real subjects, local materials, validated packages, assistant build handoff, question origins, exam variants, archive transfer, practice navigation, and timed sittings. These additions are still under Unreleased; milestone labels are not release tags.

## Next — Reliability before release

Goal: preserve learner data and make imported content safe to use.

- TASK-042: constrain archive ids and paths, validate manifests, and bound extraction
- TASK-043: stage imports and replacements so failure preserves the previous subject and package
- TASK-044: return recoverable validation issues for malformed generated JSON
- TASK-045: preserve Unicode answers and define supported grading languages
- TASK-046: isolate timers and answer state by subject and sitting
- TASK-031: verify desktop/phone and keyboard flows, then refresh media before tagging

## Then — Trustworthy learning

Goal: connect feedback to inspectable evidence and evaluate readiness honestly.

- TASK-014: structured source citations and local supporting excerpts
- TASK-018: compare prior readiness with later mock results, distinguish repeated evidence and exam conditions, and define behavior when content changes
- Keep deterministic study workflows available without an AI provider

## Then — Easier material preparation

Goal: reduce friction in the existing user-controlled build path.

- TASK-013: offline text extraction and previews for PDF/DOCX materials
- Observe learners completing creation, building, recovery, and first practice before expanding automation
- TASK-030: optional installed-agent launcher after the reliability gate; explicit provider disclosure, cancellation, private logs, and validated output promotion

## Later — Better study decisions and optional models

- TASK-015: spaced retrieval scheduling
- TASK-019: supported Python baseline update
- TASK-016: fully offline builds through a local model
- Difficulty, learning objectives, study planning, and semantic feedback remain future work requiring concrete tasks before implementation
- Cloud-provider TASK-017 remains cancelled; the learner's existing assistant handles build-time AI

## Exploratory — Voice practice

Question read-aloud, consent-based recording, speech-to-text review, and oral follow-ups remain exploratory until the core learning loop is reliable. No delivery date is committed.
