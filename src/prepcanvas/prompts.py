"""Prompts that ask an AI assistant to build a subject package from local materials.

The same schema document drives the repository skill for CLI agents and the
copy-and-paste prompt for chat assistants, so the two never drift apart.
"""

from pathlib import Path

from prepcanvas.packages import MATERIALS_DIR, PACKAGE_FILE


ROOT_DIR = Path(__file__).resolve().parents[2]
SCHEMA_DOC = ROOT_DIR / "docs" / "subject-package.md"
SKILL_NAME = "prepcanvas-build"


def schema_text() -> str:
    return SCHEMA_DOC.read_text(encoding="utf-8")


def display_path(path) -> str:
    """A subject folder as shown to the learner: repository-relative when inside the repository."""
    path = Path(path)
    try:
        return path.resolve().relative_to(ROOT_DIR).as_posix()
    except ValueError:
        return str(path)


def agent_request(subject_id: str, subject_dir) -> str:
    """The one-line request to give a CLI coding agent opened in the repository."""
    return (
        f"Use the {SKILL_NAME} skill to build the PrepCanvas subject '{subject_id}' "
        f"from the files in {display_path(subject_dir)}/{MATERIALS_DIR}."
    )


def chat_prompt(brief: dict, materials: list, subject_dir) -> str:
    """A self-contained prompt for a chat assistant that receives the materials as attachments."""
    subject_id = brief["id"]
    files = "\n".join(f"- {item['name']}" for item in materials) or "- (attach your workbook, practice exam, answer key, or notes)"
    exam = brief.get("exam_date") or "not set"
    return f"""You are helping me prepare for an exam. Build a PrepCanvas subject package from the attached study materials.

Subject id: {subject_id}
Subject name: {brief["name"]}
Exam date: {exam}
Target score: {brief.get("target_score", 80)}%

Attached materials:
{files}

What to produce
0. First decide what each attachment is: course book, practice exam, answer key, notes, or transcript. Ignore anything that is not study material for this subject (a CV, an invoice, a file from another course) and tell me which files you ignored and why. If there is no course book and no practice exam, or the files belong to different courses, ask me before building.
1. Read every kept attachment completely. Identify the topics the exam covers, using the course book structure as the backbone.
2. Write one topic object per topic with a summary, key concepts, a worked example, a common mistake, and a coach question, all grounded in the materials and labelled with a `source`.
3. If a practice exam or exercises are attached, turn each question into a question object with `"origin": "source"`. Use the answer key or model answers for `correct_answer`, `model_answer`, and the rubric.
4. For every topic, add new questions in the same style with `"origin": "generated"`, so that each topic has at least three questions and at least one multiple-choice question.
5. Follow the schema below exactly. Every `model_answer` must earn full marks against its own rubric, so pick accepted phrases and keywords that actually appear in the model answer.
6. Reply with only the JSON object, no commentary, so I can save it as `{display_path(subject_dir)}/{PACKAGE_FILE}`. Use `"id": "{subject_id}"`.

Do not invent facts that the materials do not support. Write in the language of the materials unless I ask otherwise.

--- Schema ---

{schema_text()}"""
