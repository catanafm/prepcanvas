# Changelog

All notable changes to this project are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses [Semantic Versioning](https://semver.org/). Entries reference the task that introduced them.

## [Unreleased]

### Added

- A subject can be exported from Settings as one archive with its materials, study content, coaching profile, and every saved answer, and imported from the library on another computer, optionally replacing a subject with the same id (TASK-035).
- Numbered mock-exam variants: a package may carry an `exam_blueprint` taken from the practice exam, and the Mock exam page composes variant N from the question pool by that blueprint, spread across topics, so a variant can be retaken until mastered while the next one differs. *Next new variant* and *Random variant* buttons, a structure line with the total points, and a list of sittings with scores on the Progress page. The build skill and chat prompt ask for the blueprint and a pool of at least three questions per slot (TASK-032).
- The build skill and the chat prompt triage the materials first: every file gets a role, files that are not study material for the subject are excluded and named in the report, and the agent asks instead of building when no course book or practice exam is present. The validator warns about a listed source file that does not exist (TASK-033).
- Your own subjects are now studyable: a subject *Content* page to add materials (PDF, TXT, Markdown, DOCX) into a private per-subject folder, build the study content with the AI assistant you already use, import a package, and review the validation result and every topic and question. The Overview shows a setup checklist until content loads, and every study mode links to the Content page (TASK-012, TASK-028).
- A documented subject package format shared by the sample and user subjects, with `python -m prepcanvas validate` and in-app validation: structural checks, cross-references, and a rubric self-check that rejects rubrics the model answer cannot satisfy (TASK-025).
- The `prepcanvas-build` Agent Skill and an `AGENTS.md` pointer, so Claude Code, Codex, Gemini CLI, or any agent that reads the repository can build a subject package from the materials and validate it; a copy-and-paste prompt (`python -m prepcanvas prompt`) covers chat assistants (TASK-027).
- Questions taken from a practice exam are labelled `origin: source` and generated ones `origin: generated`; the mock exam can be limited to either set (TASK-026, TASK-029).
- The demo is a *Sample* subject that can be removed with its progress, stays removed across restarts, and can be added back from the library; an empty library offers *Create your first subject* and *Explore the sample subject* (TASK-024).
- A subject library home screen: welcome, *In progress* and *Completed* groups, a *+ New subject* card, and per-subject cards with exam countdown, last activity, readiness, and coverage. Subjects can be marked as completed and reopened (TASK-023).

### Changed

- Subject tabs are ordered by use: Overview, Learn, Practice, Mock exam, Progress, then Diagnostic, Content, and Settings (TASK-034).
- Creating a subject asks only for a name, exam date, and target, then opens the Content page; the material checkboxes are gone, materials are real files now (TASK-028).
- README, architecture, and roadmap describe the build-time AI approach and state that the app sends nothing anywhere while the assistant you choose receives your materials under your own account (TASK-028).
- The sidebar subject dropdown is replaced by the library; inside a subject, *← All subjects* returns home and the *Subjects* tab became per-subject *Settings* (TASK-023).

## [0.1.1] - 2026-09-24

Presentation polish: every screen reviewed at desktop and phone widths, clearer progress history, and a fuller README walkthrough.

### Added

- README shows the diagnostic result and progress page, and the demo GIF now follows Diagnostic → Learn → Practice → Feedback → Progress over about 25 seconds (TASK-021).

### Changed

- Progress activity names the question and topic and shows local time; the three progress metrics stay in one row on phones (TASK-020).
- Source labels read "Sustainable Business workbook (synthetic) · Topic" instead of a repository file path (TASK-020).

### Fixed

- Tighter spacing above the navigation and after the next best action, and a smaller hero heading on phones (TASK-020).
- Creating a subject, and opening a subject without study content, now explain that material upload comes in a later release and point to the demo subject (TASK-020).

## [0.1.0] - 2026-09-23

First public release: a trustworthy, fully local demo of the study loop — diagnose, learn, practise, mock exam, and track readiness.

### Added

- Local-first Streamlit MVP with a synthetic demo subject, diagnostic coaching profiles, guided learning, targeted practice, a delayed-feedback mock exam, and transparent readiness tracking.
- Subjects can be managed from the Subjects page: reset progress for any subject, including the demo, or delete a user subject with all of its progress. Both actions require an explicit confirmation (TASK-007).
- README screenshots, a phone layout screenshot, and a demo GIF, all generated reproducibly by `scripts/capture_media.py` from the synthetic demo (TASK-010).
- CI for tests and privacy checks on Python 3.9, 3.11, 3.12, and 3.13 (TASK-009).
- Task board, task template, contribution guide, and pull request template for a task-driven workflow (TASK-001).

### Changed

- Setup scripts choose the newest available Python and recommend 3.12; development dependencies install from `requirements.txt` only, with a test that keeps its pins in sync with `pyproject.toml` (TASK-009).
- Workspace navigation moved from the sidebar to wrapping pills above the content, so it stays reachable on phones; overview and progress metrics render as a responsive grid (four across on desktop, 2 × 2 on phones); the Streamlit developer toolbar is hidden (TASK-006).
- Readiness counts the latest answer per distinct question, weighs mock-exam answers 1.5×, and lets evidence decay with a 14-day half-life, so repeating one question can no longer inflate topic mastery. The topic map shows questions answered per topic (TASK-003).

### Fixed

- SQLite connections are closed after every operation and foreign keys are enforced; the diagnostic skips topics without a multiple-choice question instead of crashing (TASK-008).
- The next best action recommends the subject-wide diagnostic before any evidence exists, points to unanswered topics, and suggests a mock exam once the target is reached. The session estimate stays hidden until every topic has evidence, and the metric label no longer truncates (TASK-005).
- Creating a subject shows a confirmation and selects the new subject instead of discarding the message on rerun (TASK-004).
- Short-answer grading accepts inflected word forms, hyphen and spacing variants, number words, and "not only … but also", and no longer awards full credit to bare keyword lists (TASK-002).

### Removed

- `TODO.md`, replaced by the task board in `tasks/` (TASK-001).

[Unreleased]: https://github.com/catanafm/prepcanvas/compare/v0.1.1...HEAD
[0.1.1]: https://github.com/catanafm/prepcanvas/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/catanafm/prepcanvas/releases/tag/v0.1.0
