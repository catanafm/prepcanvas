"""Which practice question comes next: never-answered first, then the ones answered longest ago."""

import random
from datetime import datetime


def latest_attempts(attempts: list) -> dict:
    """Newest attempt per question; `attempts` arrive newest first."""
    latest = {}
    for row in attempts:
        if row.get("question_id"):
            latest.setdefault(row["question_id"], row)
    return latest


def practice_order(questions: list, attempts: list) -> list:
    latest = latest_attempts(attempts)
    unanswered = [question for question in questions if question["id"] not in latest]
    answered = sorted(
        (question for question in questions if question["id"] in latest),
        key=lambda question: latest[question["id"]]["created_at"],
    )
    return unanswered + answered


def next_question(questions: list, attempts: list, current_id=None) -> dict:
    """The most useful question to do next, never the one on screen unless it is the only one."""
    order = practice_order(questions, attempts)
    candidates = [question for question in order if question["id"] != current_id]
    return (candidates or order)[0]


def random_question(questions: list, current_id=None, rng=random) -> dict:
    candidates = [question for question in questions if question["id"] != current_id]
    return rng.choice(candidates or questions)


def question_status(question: dict, attempts: list) -> str:
    latest = latest_attempts(attempts).get(question["id"])
    if latest is None:
        return "Not answered yet"
    when = datetime.fromisoformat(latest["created_at"]).astimezone().strftime("%d %b")
    return f'Last answered {when} · {latest["score"]}/{latest["max_score"]}'


def remaining(questions: list, attempts: list) -> int:
    latest = latest_attempts(attempts)
    return sum(1 for question in questions if question["id"] not in latest)
