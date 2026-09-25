# Architecture

## Current shape

PrepCanvas is a small local Streamlit application with deterministic domain logic and SQLite persistence.

```text
Streamlit UI
    │
    ├── catalog.py       bundled sample subject
    ├── packages.py      subject package schema, validator, private files
    ├── prompts.py       build instructions for AI assistants
    ├── coaching.py      diagnostic strategy selection
    ├── grading.py       deterministic answer scoring
    ├── readiness.py     transparent mastery heuristic
    └── storage.py       subjects, attempts, profiles
             │
      SQLite + data/private/
```

`cli.py` exposes `python -m prepcanvas validate` and `python -m prepcanvas prompt` for use outside the app.

## Data boundaries

Public, versioned data:

- packaged synthetic source document and derived demo subject;
- tests and expected outputs;
- product documentation.

Local, ignored data:

- user-created subjects;
- progress and answers;
- uploaded source materials;
- parsed source artifacts;
- secrets and provider configuration.

## Why deterministic at runtime

The app works without an AI key. This makes setup reproducible, protects privacy, and keeps grading behavior testable. AI is used once, at build time, to turn a learner's materials into a subject package; from then on grading, readiness, and coaching are deterministic and offline.

## Subject packages and the build step

Every subject, the bundled sample included, gets its study content from one validated JSON file described in [subject-package.md](subject-package.md). User packages live in `data/private/subjects/<subject-id>/package.json`, next to the learner's materials and a `brief.json` written by the app.

```text
materials/  ──►  learner's own AI assistant  ──►  package.json  ──►  validator  ──►  app
                 (CLI agent via the repository skill,
                  or a chat assistant via the copied prompt)
```

- The repository ships an Agent Skill, `.claude/skills/prepcanvas-build/SKILL.md`, that any CLI coding agent can follow; `AGENTS.md` points to it for agents without skill support.
- For chat assistants, the app builds a prompt from the same schema document and imports the JSON reply.
- `packages.validate_package` is the contract: structural checks, cross-references, and a rubric self-check that grades every `model_answer` with `grading.grade_question` and rejects rubrics the model answer itself cannot satisfy. Errors block loading; warnings are shown on the Content page.
- Questions carry `origin`, `source` or `generated`, so the mock exam can replay the original practice exam or a generated variant.

PrepCanvas itself sends nothing anywhere. The assistant the learner chooses receives the materials under the learner's own account, and the UI says so next to the build instructions.

## Rubric grading

Short answers are graded against rubric points defined in the subject data. Each answer is split into clauses at sentence punctuation and at `and`, `but`, `while`, and `whereas`, so a definition only counts where it is stated. A rubric point is awarded when one clause, without negation, contains its required keywords and either an accepted phrase or the minimum number of keywords.

Before matching, words are normalized: number words become digits, hyphenated terms match their spaced and joined spellings, and a small suffix-stripping stemmer aligns inflected forms such as *durable* and *durability*. "Not only … but also" is not treated as a negation. A clause that is only a list of keywords, with no ordinary sentence words, can earn at most one keyword-based point.

## Readiness heuristic

For each topic, PrepCanvas keeps only the latest answered attempt per question. Each of those answers has a freshness of `0.5 ^ (age in days / 14)` and a weight of freshness × mode weight, where mock-exam answers count 1.5× and every other mode 1×.

- **Accuracy** is the weighted mean of the score ratios.
- **Evidence factor** is the sum of freshness divided by the number of questions required for the topic (three, or fewer when the topic has fewer questions), capped at 1. Repeating one question therefore cannot exceed one third, and a topic not practised for two weeks drops to half.
- **Topic mastery** is accuracy × evidence factor.

Overall readiness is the mean of topic mastery. A subject is marked ready only when the target score is reached and every topic has evidence.

## Moving subjects

`transfer.py` packs a subject into a zip: `subject.json` (record, coaching profile, attempts), `package.json`, `brief.json`, and the materials. Importing inserts the subject as a user subject with its original timestamps and writes the files back under `data/private/`. The sample subject is never exported.

## Data flow inside the app

The UI never reads materials. It loads the package through `SubjectFiles.load_package`, merges the database record (name, exam date, target, status) with the package content (topics, questions, sources), and passes the result to the same catalog, grading, and readiness code the sample uses. A subject without a valid package shows a setup checklist instead of a topic map, and every study mode points to the Content page.
