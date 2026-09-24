# Task board

Every change to PrepCanvas is tracked as a task. See [CONTRIBUTING.md](../CONTRIBUTING.md) for the workflow and [`_template.md`](_template.md) to add a new one.

Tasks are listed in planned order. The test suite verifies that this board matches the task files.

| ID | Title | Type | Priority | Status |
|---|---|---|---|---|
| [TASK-001](TASK-001-task-workflow.md) | Establish task board and contribution workflow | docs | high | done |
| [TASK-002](TASK-002-robust-rubric-grading.md) | Make rubric grading robust to word forms and spelling variants | fix | high | done |
| [TASK-003](TASK-003-readiness-evidence-quality.md) | Base readiness on distinct questions and recent, mode-weighted evidence | fix | high | done |
| [TASK-004](TASK-004-subject-creation-feedback.md) | Show confirmation after creating a subject | fix | medium | done |
| [TASK-005](TASK-005-honest-guidance-copy.md) | Make next-action and session estimate guidance accurate | fix | medium | done |
| [TASK-008](TASK-008-storage-and-diagnostic-robustness.md) | Close SQLite connections and guard content assumptions | refactor | medium | done |
| [TASK-006](TASK-006-responsive-layout.md) | Complete visual QA and improve the mobile layout | feature | medium | done |
| [TASK-007](TASK-007-subject-management.md) | Add subject deletion and progress reset | feature | medium | done |
| [TASK-009](TASK-009-python-baseline.md) | Test supported Python versions and tidy packaging | chore | low | done |
| [TASK-010](TASK-010-readme-media.md) | Add screenshots and a short demo GIF to the README | docs | medium | done |
| [TASK-011](TASK-011-first-release.md) | Publish the first tagged release (v0.1.0) | chore | medium | done |
| [TASK-020](TASK-020-visual-qa.md) | Complete visual QA across every screen and fix findings | fix | medium | done |
| [TASK-021](TASK-021-presentation-media.md) | Capture diagnostic and progress media and extend the demo GIF | docs | medium | done |
| [TASK-022](TASK-022-release-0-1-1.md) | Publish the v0.1.1 presentation polish release | chore | medium | done |
| [TASK-012](TASK-012-local-material-upload.md) | Upload local PDF, TXT, and Markdown materials | feature | medium | backlog |
| [TASK-013](TASK-013-source-preview-classification.md) | Preview and classify sources before processing | feature | low | backlog |
| [TASK-014](TASK-014-topic-map-citations.md) | Build a topic map with source citations | feature | low | backlog |
| [TASK-015](TASK-015-spaced-review.md) | Add spaced review scheduling | feature | low | backlog |
| [TASK-016](TASK-016-local-model-provider.md) | Add an optional local-model provider interface | feature | low | backlog |
| [TASK-017](TASK-017-cloud-model-provider.md) | Add an opt-in cloud AI provider interface | feature | low | backlog |
| [TASK-018](TASK-018-validate-readiness.md) | Validate readiness against mock-exam trends | feature | low | backlog |
| [TASK-019](TASK-019-raise-python-minimum.md) | Raise the minimum Python version to 3.11 | chore | low | backlog |

## Milestones

- **v0.1.0 — Trustworthy demo:** TASK-002 → TASK-011 · released 2026-09-23
- **v0.1.1 — Presentation polish:** TASK-020 → TASK-022 · released 2026-09-24
- **v0.2.0 — Real subjects:** TASK-012 → TASK-015, TASK-019
- **v0.3.0 — Optional AI:** TASK-016 → TASK-018
