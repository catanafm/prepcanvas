# Subject package

A subject package is one JSON file, `package.json`, that holds everything PrepCanvas needs to coach, practise, and examine a subject: topics, questions, rubrics, and where each item comes from. The bundled sample subject uses the same format, so the sample is also the reference example: [`src/prepcanvas/demo_data/sustainable_business.json`](../src/prepcanvas/demo_data/sustainable_business.json).

Packages for your own subjects live outside version control at:

```text
data/private/subjects/<subject-id>/
  brief.json      written by the app: name, exam date, target
  materials/      your workbook, practice exam, answer key, notes
  package.json    the study content, produced by you or your AI agent
```

Validate a package with:

```bash
PYTHONPATH=src python -m prepcanvas validate data/private/subjects/<subject-id>/package.json
```

Errors block loading; warnings are advice. The app runs the same validation every time it opens a subject.

## Top level

| Field | Required | Meaning |
|---|---|---|
| `schema_version` | yes | Always `1`. |
| `id` | yes | Lowercase slug; must equal the subject folder name. |
| `name` | yes | Subject name shown in the app. |
| `description` | no | One sentence for the subject overview. |
| `target_score` | no | Integer 1–100. The app keeps the target set in the UI. |
| `exam_date` | no | `YYYY-MM-DD` or `null`. |
| `materials` | no | Map of material kinds to `true`/`false` (`workbook`, `practice_tests`, `sample_answers`, `notes`, `transcripts`, `other`). |
| `sources` | no | List of the files the content was built from, see below. |
| `topics` | yes | Non-empty list of topics. |
| `questions` | yes | Non-empty list of questions. |

### Sources

```json
{"id": "workbook", "role": "workbook", "title": "Course workbook", "file": "materials/workbook.pdf"}
```

`role` is one of `workbook`, `practice_exam`, `answer_key`, `notes`, `transcript`, `other`. `file` is optional and relative to the subject folder. List exactly the files the content was built from: a file that was excluded as not study material does not belong here, and the validator warns about a listed file that does not exist.

## Topics

Every topic is a self-contained lesson. Text is shown to the learner as written.

| Field | Required | Meaning |
|---|---|---|
| `id` | yes | Slug, unique within the package. |
| `title` | yes | Short name. |
| `summary` | yes | The core idea in two to four sentences. |
| `key_concepts` | yes | Three to six short terms. |
| `worked_example` | yes | A concrete scenario that applies the idea. |
| `common_mistake` | yes | The trap learners fall into. |
| `coach_question` | yes | One open question that makes the learner think before answering. |
| `source` | yes | Human-readable label of where the topic comes from, e.g. `Course workbook · Chapter 3, pp. 41–48`. |

Every topic needs at least one question. The diagnostic uses the first multiple-choice question of each topic, and readiness treats three distinct questions per topic as full evidence, so aim for at least three questions per topic including one multiple-choice question.

## Questions

Common fields:

| Field | Required | Meaning |
|---|---|---|
| `id` | yes | Slug, unique within the package. |
| `topic_id` | yes | Id of an existing topic. |
| `type` | yes | `multiple_choice` or `short_answer`. |
| `points` | yes | Positive integer. |
| `prompt` | yes | The question as shown to the learner. |
| `explanation` | yes | Feedback shown after answering, regardless of the score. |
| `source` | yes | Where the question comes from, e.g. `Practice exam 2024 · Q7` or `Generated from workbook · Chapter 3`. |
| `origin` | yes | `source` when the question is taken from the materials (a practice exam, a workbook exercise), `generated` when it is a new question written in the style of the materials. The mock exam can be limited to either set. |

### Multiple choice

```json
{
  "id": "sys-1",
  "topic_id": "systems-thinking",
  "type": "multiple_choice",
  "points": 1,
  "origin": "source",
  "prompt": "Which question best reflects systems thinking?",
  "options": ["Which department owns this metric?", "What else changes when we change this?", "How fast can we ship?"],
  "correct_answer": "What else changes when we change this?",
  "explanation": "Systems thinking asks about interactions and side effects beyond the immediate metric.",
  "source": "Course workbook · Chapter 1"
}
```

`options` holds at least two distinct strings and `correct_answer` is exactly one of them.

### Short answer

```json
{
  "id": "sys-3",
  "topic_id": "systems-thinking",
  "type": "short_answer",
  "points": 2,
  "origin": "generated",
  "prompt": "Why can improving one sustainability metric make the overall system worse?",
  "model_answer": "The metric may use a narrow system boundary and ignore trade-offs or unintended consequences elsewhere.",
  "rubric_points": [
    {
      "label": "Recognizes a narrow system boundary",
      "points": 1,
      "accepted_phrases": ["narrow boundary", "limited system boundary", "looks at only one part"],
      "keywords": ["boundary", "narrow"],
      "minimum_keyword_matches": 2
    },
    {
      "label": "Recognizes trade-offs or unintended consequences",
      "points": 1,
      "accepted_phrases": ["unintended consequences", "creates trade-offs", "shifts the problem"],
      "keywords": ["trade-offs", "consequences"],
      "minimum_keyword_matches": 1
    }
  ],
  "explanation": "A local improvement is not necessarily a system improvement. Check boundaries, trade-offs, and delayed effects.",
  "source": "Generated from workbook · Chapter 1"
}
```

Short answers are graded deterministically, without a model. Each rubric point is awarded when one clause of the answer, without a negation, contains all `required_keywords` and either one of the `accepted_phrases` or at least `minimum_keyword_matches` of the `keywords` (default: all of them). Words are stemmed, so `durable` matches `durability`.

Rules for rubrics:

- `rubric_points` is non-empty; each point has a `label`, positive `points`, and `accepted_phrases` and/or `keywords`.
- The rubric points add up to at least the question's `points`.
- **The `model_answer` must earn full marks against its own rubric.** The validator grades it and reports which points fail. Write the model answer the way a strong student would, then choose phrases and keywords that appear in it and in reasonable paraphrases.
- Keywords are single words or short terms; accepted phrases are two to five words. Avoid keywords that appear in the prompt itself, otherwise restating the question scores points.

## Validation summary

Errors (the package will not load):

- wrong `schema_version`, missing required fields, ids that are not slugs, duplicate ids, unknown `topic_id`;
- package `id` different from the subject folder name;
- multiple-choice questions whose `correct_answer` is not one of the `options`;
- short-answer questions without a `model_answer`, with unreachable full marks, or whose model answer fails its own rubric;
- topics without any question.

Warnings (the package loads, but the experience is weaker):

- a topic without a multiple-choice question is skipped by the diagnostic;
- a topic with fewer than three questions cannot reach full evidence in the readiness heuristic;
- rubric points that add up to more than the question's points are capped.
