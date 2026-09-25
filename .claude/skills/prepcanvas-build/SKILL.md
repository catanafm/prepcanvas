---
name: prepcanvas-build
description: Build or rebuild the study content of a PrepCanvas subject (topics, questions taken from a practice exam, similar generated questions, and grading rubrics) from the learner's own materials in data/private/subjects/<subject-id>/materials, then validate the package with `python -m prepcanvas validate`. Use when asked to build, generate, refresh, or extend a PrepCanvas subject.
argument-hint: [subject-id]
---

# Build a PrepCanvas subject package

You turn a learner's study materials into `data/private/subjects/<subject-id>/package.json`, the file PrepCanvas loads to run its diagnostic, coaching, practice, and mock exam. Grading in the app is deterministic and happens without you, so the quality of the questions and rubrics you write is what the learner will experience.

The subject id is `$ARGUMENTS` when given; otherwise take it from the request or list `data/private/subjects/`.

## 1. Read the brief and the materials

- `data/private/subjects/<subject-id>/brief.json` holds the name, exam date, and target score. If it is missing, ask for the subject name and use the folder name as the id.
- `data/private/subjects/<subject-id>/materials/` holds the files. Read every one of them completely before writing anything. Typical roles: a workbook or course book (the backbone of the topics), a practice or mock exam, an answer key or model answers, notes, transcripts.
- If a PDF has no text layer or you cannot read a format, stop and tell the learner which file to convert; do not guess its content.
- Everything here is private. Never copy material text into the repository, tests, docs, or commit messages. The package itself is git-ignored.

## 2. Design the topics

- Use the workbook or course structure to define 4–10 topics that together cover the exam. Merge tiny sections; split chapters that mix unrelated ideas.
- For each topic write, in the learner's own materials' terms: a summary (two to four sentences), three to six key concepts, a worked example, the common mistake, and one coach question that makes the learner think before answering.
- Set `source` to a label a learner can follow back to the file, e.g. `Course workbook · Chapter 3, pp. 41–48`.

## 3. Write the questions

- **From the materials, `"origin": "source"`.** Turn every practice-exam question and workbook exercise into a question object. Keep the wording, points, and options. Take `correct_answer`, `model_answer`, and the rubric from the answer key. Label the source with the exam name and question number.
- **Similar new questions, `"origin": "generated"`.** For every topic add questions in the same style and difficulty until each topic has at least three questions and at least one multiple-choice question. Vary the scenario, not just the wording. Label them `Generated from <file> · <section>`.
- Multiple choice: three to five distinct options, one correct, plausible distractors drawn from the common mistakes in the materials.
- Short answer: a `model_answer` written the way a strong student would, then `rubric_points` whose `accepted_phrases` and `keywords` appear in that model answer and in reasonable paraphrases. Avoid keywords that appear in the prompt. Rubric points must add up to the question's points.
- `explanation` is shown after every answer, right or wrong: state why the answer is what it is, with a pointer into the materials.
- Do not invent facts the materials do not support. Write in the language of the materials unless asked otherwise.

## 4. Write and validate the package

Follow [docs/subject-package.md](../../../docs/subject-package.md) exactly; the bundled sample `src/prepcanvas/demo_data/sustainable_business.json` is a complete example. Set `"id"` to the subject id, `schema_version` to `1`, and list the files you used in `sources`.

Then run, from the repository root:

```bash
PYTHONPATH=src python -m prepcanvas validate data/private/subjects/<subject-id>/package.json
```

(Use `.venv/bin/python` if the project virtual environment exists.) Fix every `ERROR` and re-run until the command reports `valid`. The check that fails most often is *the model answer scores N/M against its own rubric*: adjust the accepted phrases or keywords so the model answer earns full marks. Treat `WARNING` lines as advice and fix them when the materials allow.

## 5. Report

Tell the learner: how many topics and questions you produced, how many came from the materials and how many are generated, what you could not use, and any warnings left. Ask them to open the subject's **Content** page in PrepCanvas and review the topics and questions before studying. Do not modify anything under `src/`, `app/`, or `tests/` for this task.
