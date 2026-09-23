# Changelog

All notable changes to this project are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses [Semantic Versioning](https://semver.org/). Entries reference the task that introduced them.

## [Unreleased]

### Added

- Subjects can be managed from the Subjects page: reset progress for any subject, including the demo, or delete a user subject with all of its progress. Both actions require an explicit confirmation (TASK-007).
- Task board, task template, contribution guide, and pull request template for a task-driven workflow (TASK-001).
- Local-first Streamlit MVP with a synthetic demo subject, diagnostic coaching profiles, guided learning, targeted practice, a delayed-feedback mock exam, and transparent readiness tracking.
- CI for tests and privacy checks on Python 3.9 and 3.11.

### Changed

- Workspace navigation moved from the sidebar to wrapping pills above the content, so it stays reachable on phones; overview and progress metrics render as a responsive grid (four across on desktop, 2 × 2 on phones); the Streamlit developer toolbar is hidden (TASK-006).
- Readiness counts the latest answer per distinct question, weighs mock-exam answers 1.5×, and lets evidence decay with a 14-day half-life, so repeating one question can no longer inflate topic mastery. The topic map shows questions answered per topic (TASK-003).

### Fixed

- SQLite connections are closed after every operation and foreign keys are enforced; the diagnostic skips topics without a multiple-choice question instead of crashing (TASK-008).
- The next best action recommends the subject-wide diagnostic before any evidence exists, points to unanswered topics, and suggests a mock exam once the target is reached. The session estimate stays hidden until every topic has evidence, and the metric label no longer truncates (TASK-005).
- Creating a subject shows a confirmation and selects the new subject instead of discarding the message on rerun (TASK-004).
- Short-answer grading accepts inflected word forms, hyphen and spacing variants, number words, and "not only … but also", and no longer awards full credit to bare keyword lists (TASK-002).

### Removed

- `TODO.md`, replaced by the task board in `tasks/` (TASK-001).
