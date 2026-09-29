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
| [TASK-023](TASK-023-subject-library.md) | Add a subject library home screen | feature | high | done |
| [TASK-024](TASK-024-removable-sample-subject.md) | Treat the demo as a removable sample subject | feature | high | done |
| [TASK-025](TASK-025-subject-content-packages.md) | Store study content for user subjects as validated local packages | feature | high | done |
| [TASK-012](TASK-012-local-material-upload.md) | Add study materials to a subject from the Content page | feature | high | done |
| [TASK-027](TASK-027-build-skill.md) | Ship an Agent Skill that builds subject packages with the learner's own assistant | feature | high | done |
| [TASK-028](TASK-028-content-page.md) | Guide a new subject from creation to study content on a Content page | feature | high | done |
| [TASK-026](TASK-026-questions-from-practice-exam.md) | Build questions and rubrics from a practice exam and its answer key | feature | high | done |
| [TASK-029](TASK-029-mock-exam-sets.md) | Let the mock exam replay the practice exam or a generated variant | feature | medium | done |
| [TASK-034](TASK-034-tab-order.md) | Order subject tabs by how often they are used | fix | medium | done |
| [TASK-033](TASK-033-material-triage.md) | Triage materials before building so only study material becomes content | feature | high | done |
| [TASK-032](TASK-032-exam-variants.md) | Compose numbered mock-exam variants from a question pool and an exam blueprint | feature | high | done |
| [TASK-035](TASK-035-subject-export-import.md) | Export a subject with its progress and import it on another computer | feature | medium | done |
| [TASK-038](TASK-038-store-cache-stale-class.md) | Stop caching the StudyStore across code reloads | fix | high | done |
| [TASK-036](TASK-036-practice-flow.md) | Move through practice questions with Next and Random instead of a dropdown | feature | high | done |
| [TASK-037](TASK-037-sidebar-subject-summary.md) | Show the open subject and its key numbers in the sidebar | feature | medium | done |
| [TASK-039](TASK-039-timed-mock-exam.md) | Time the mock exam like the real one | feature | high | done |
| [TASK-040](TASK-040-library-layout.md) | Put subjects first in the library and give the cards one height | fix | medium | done |
| [TASK-041](TASK-041-review-and-backlog.md) | Review the current implementation and reprioritize the backlog | docs | high | done |
| [TASK-042](TASK-042-archive-boundaries.md) | Confine subject archives to validated private paths | fix | high | done |
| [TASK-043](TASK-043-atomic-subject-import.md) | Preserve existing data when an import or replacement fails | fix | high | backlog |
| [TASK-044](TASK-044-total-package-validation.md) | Return structured errors for malformed package values | fix | high | backlog |
| [TASK-045](TASK-045-unicode-grading.md) | Preserve non-English answers and declare grading language support | fix | high | backlog |
| [TASK-046](TASK-046-subject-exam-state.md) | Isolate active exam sessions by subject and sitting | fix | high | backlog |
| [TASK-014](TASK-014-topic-map-citations.md) | Show structured citations for topics and questions | feature | high | backlog |
| [TASK-018](TASK-018-validate-readiness.md) | Validate readiness against mock-exam trends | feature | medium | backlog |
| [TASK-013](TASK-013-source-preview-classification.md) | Cache extracted text so every agent can read PDF and DOCX materials | feature | medium | backlog |
| [TASK-031](TASK-031-readme-media-subject-flow.md) | Refresh README media for the subject flow | docs | medium | backlog |
| [TASK-030](TASK-030-run-agent-from-app.md) | Run an installed CLI agent from the Content page | feature | low | backlog |
| [TASK-015](TASK-015-spaced-review.md) | Add spaced review scheduling | feature | low | backlog |
| [TASK-019](TASK-019-raise-python-minimum.md) | Raise the minimum Python version to 3.11 | chore | low | backlog |
| [TASK-016](TASK-016-local-model-provider.md) | Build packages fully offline with a local model | feature | low | backlog |
| [TASK-017](TASK-017-cloud-model-provider.md) | Add an opt-in cloud AI provider interface | feature | low | cancelled |

## Current priorities — 2026-09-29

1. **Reliability gate:** TASK-042 → TASK-043 → TASK-044 → TASK-045 → TASK-046. Resolve archive boundaries, data-loss risks, malformed packages, language grading, and cross-subject exam state before another release.
2. **Trustworthy learning:** TASK-014, TASK-018. Inspectable evidence and honest readiness take precedence over more generated questions or automation.
3. **Onboarding and release QA:** TASK-013, TASK-031. Make materials readable, exercise the actual subject flow, and refresh media.
4. **Later:** TASK-030, TASK-015, TASK-019, TASK-016. CLI launch remains optional; cloud-provider TASK-017 stays cancelled.

See [the implementation and product review](../docs/reviews/2026-09-29.md) for evidence and scope.

## Milestones

- **v0.1.0 — Trustworthy demo:** released 2026-09-23.
- **v0.1.1 — Presentation polish:** released 2026-09-24; latest repository tag at review time.
- **Implemented, unreleased:** real subjects, assistant-built packages, variants, transfer, practice navigation, timed exams, library layout (TASK-012, TASK-023–TASK-029, TASK-032–TASK-040). Previous v0.2.0–v0.2.3 board labels described work batches, not published releases; pyproject.toml still reports 0.1.1.
- **Next release, version TBD:** reliability gate plus TASK-031; update version/changelog and run the release checklist before tagging.
- **Next product milestone:** traceable sources and readiness evaluation (TASK-014, TASK-018), followed by smoother extraction (TASK-013).
- **Later:** spaced review, optional agent launcher, and offline model builds; no dates committed.

| [TASK-047](TASK-047-build-private-subject.md) | Build and validate a private subject package | chore | medium | in-progress |
