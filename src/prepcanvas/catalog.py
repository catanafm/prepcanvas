import json
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
DEMO_SUBJECT_PATH = Path(__file__).resolve().parent / "demo_data" / "sustainable_business.json"


def load_demo_subject() -> dict:
    """Load the synthetic subject shipped with the public repository."""
    return json.loads(DEMO_SUBJECT_PATH.read_text(encoding="utf-8"))


def get_topic(subject: dict, topic_id: str) -> dict:
    return next(topic for topic in subject["topics"] if topic["id"] == topic_id)


def get_question(subject: dict, question_id: str) -> dict:
    return next(question for question in subject["questions"] if question["id"] == question_id)
