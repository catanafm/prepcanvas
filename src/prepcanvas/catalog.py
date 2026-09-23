import json
from pathlib import Path


DEMO_SUBJECT_PATH = Path(__file__).resolve().parent / "demo_data" / "sustainable_business.json"


def load_demo_subject() -> dict:
    """Load the synthetic subject shipped with the public repository."""
    return json.loads(DEMO_SUBJECT_PATH.read_text(encoding="utf-8"))


def get_topic(subject: dict, topic_id: str) -> dict:
    topic = next((topic for topic in subject["topics"] if topic["id"] == topic_id), None)
    if topic is None:
        raise KeyError(f"Unknown topic '{topic_id}' in subject '{subject.get('id')}'")
    return topic


def get_question(subject: dict, question_id: str) -> dict:
    question = next((question for question in subject["questions"] if question["id"] == question_id), None)
    if question is None:
        raise KeyError(f"Unknown question '{question_id}' in subject '{subject.get('id')}'")
    return question


def diagnostic_questions(subject: dict) -> list:
    """Pick the first multiple-choice question of each topic; topics without one are skipped."""
    questions = []
    for topic in subject["topics"]:
        question = next(
            (
                question
                for question in subject["questions"]
                if question["topic_id"] == topic["id"] and question["type"] == "multiple_choice"
            ),
            None,
        )
        if question:
            questions.append(question)
    return questions
