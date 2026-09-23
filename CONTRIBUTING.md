# Contributing

PrepCanvas uses a lightweight, task-driven workflow. Every change — feature, fix, refactor, or documentation — starts with a task and ends with a reviewed, squash-merged pull request.

All code, documentation, commit messages, and task files are written in English.

## 1. Tasks

Tasks live in [`tasks/`](tasks/) as Markdown files with YAML-style front matter. The [task board](tasks/README.md) is the single source of truth for what is planned, in progress, and done.

- **ID format:** `TASK-NNN`, zero-padded, sequential, never reused.
- **File name:** `tasks/TASK-NNN-short-slug.md`.
- **Template:** copy [`tasks/_template.md`](tasks/_template.md).

| Field | Allowed values |
|---|---|
| `type` | `feature`, `fix`, `refactor`, `chore`, `docs`, `test` |
| `status` | `backlog`, `in-progress`, `done`, `cancelled` |
| `priority` | `high`, `medium`, `low` |

To add a task, create the file, then add a row to the board. The test suite checks that the board and the task files stay in sync.

## 2. Branches

Branch from an up-to-date `main`, one branch per task:

```text
task/TASK-NNN-short-slug
```

Example: `task/TASK-002-robust-rubric-grading`.

## 3. Commits

Commits follow [Conventional Commits](https://www.conventionalcommits.org/) with the task ID at the end of the subject line:

```text
<type>(<scope>): <imperative summary> (TASK-NNN)
```

Examples:

```text
fix(grading): accept inflected word forms in rubric keywords (TASK-002)
docs(tasks): add task board and contribution workflow (TASK-001)
```

- `type` matches the task type (`feature` → `feat`).
- `scope` is the affected area: `grading`, `readiness`, `storage`, `ui`, `coaching`, `ci`, `docs`, `tasks`.
- Keep the subject under 72 characters; explain the *why* in the body when it is not obvious.

## 4. Pull requests

- **Title:** the final squash commit message, e.g. `fix(grading): accept inflected word forms (TASK-002)`.
- **Body:** use the [pull request template](.github/pull_request_template.md) and link the task file.
- **Merge:** squash merge into `main`, so each task lands as one commit.

## 5. Definition of done

A task is done when:

- [ ] every acceptance criterion in the task file is met;
- [ ] new behaviour is covered by tests and `./scripts/run_tests.sh -q` passes;
- [ ] the task `status` is `done` and the board is updated;
- [ ] user-visible changes are listed under **Unreleased** in [`CHANGELOG.md`](CHANGELOG.md);
- [ ] documentation reflects the change;
- [ ] no private materials, personal answers, local databases, or absolute user paths are committed.

## Local development

```bash
./scripts/setup.sh
./scripts/run_tests.sh -q
./scripts/run_app.sh
```

Use `PREPCANVAS_DB_PATH=/tmp/prepcanvas-dev.sqlite3` when experimenting so your real study progress stays untouched.

### README media

Screenshots and the demo GIF in `docs/media/` are generated, not hand-made. After a visible UI change, regenerate them:

```bash
.venv/bin/python scripts/capture_media.py
```

The script starts the app on a temporary database with synthetic progress and drives headless Google Chrome (set `CHROME_PATH` if it is not in the default location).
