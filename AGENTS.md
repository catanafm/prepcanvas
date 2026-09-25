# Project purpose

PrepCanvas is a local-first, source-grounded exam preparation companion.

# Product constraints

- Keep user materials, answers, and progress local by default.
- Never commit private source documents, transcripts, generated source artifacts, or local databases.
- Ground learning feedback in the selected subject's sources.
- Keep deterministic workflows functional without an AI provider.
- Present readiness as a transparent heuristic, not a guaranteed result.
- Use synthetic content for public demos and tests.

# Technical constraints

- Python and Streamlit
- SQLite persistence
- small modules with focused tests
- English product UI and documentation
- optional AI providers behind explicit interfaces in later iterations

# UX priorities

1. Show the next best study action.
2. Explain before testing when the learner needs foundations.
3. Use immediate feedback in learning and practice modes.
4. Delay feedback until submission in mock-exam mode.
5. Show progress by topic and distinguish mastery from evidence volume.

# Working conventions

Follow [CONTRIBUTING.md](CONTRIBUTING.md). In short:

- Every change starts from a task in `tasks/` (`TASK-NNN`). Create one from `tasks/_template.md` and add it to `tasks/README.md` if none exists.
- Branch: `task/TASK-NNN-short-slug`, from an up-to-date `main`.
- Commits: Conventional Commits ending with the task ID, e.g. `fix(grading): accept inflected word forms (TASK-002)`.
- Before finishing: tests pass, acceptance criteria are checked off, task status and board are updated, and `CHANGELOG.md` lists user-visible changes.
- Write all code, docs, commits, and task files in English.
- Experiment with `PREPCANVAS_DB_PATH` pointing to a temporary database so real study progress is never modified.

# Building study content for a subject

Learners build the study content of their own subjects with the AI agent they already use. The instructions live in [`.claude/skills/prepcanvas-build/SKILL.md`](.claude/skills/prepcanvas-build/SKILL.md) and work for any agent: read the materials in `data/private/subjects/<subject-id>/materials/`, write `package.json` following [`docs/subject-package.md`](docs/subject-package.md), and run `python -m prepcanvas validate` until it passes. Everything under `data/private/` is the learner's private material: never copy it into the repository.
