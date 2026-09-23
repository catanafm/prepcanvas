from datetime import datetime, timezone
from math import ceil


# Mock exams are closest to real exam conditions, so they count for more.
MODE_WEIGHTS = {"mock_exam": 1.5}
# Evidence loses half of its weight every two weeks.
HALF_LIFE_DAYS = 14
# Distinct questions needed before a topic can reach full mastery.
REQUIRED_QUESTIONS = 3


def _age_days(created_at, now: datetime) -> float:
    if not created_at:
        return 0.0
    try:
        moment = datetime.fromisoformat(created_at)
    except ValueError:
        return 0.0
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)
    return max(0.0, (now - moment).total_seconds() / 86400)


def _latest_answer_per_question(rows: list) -> list:
    """Keep the newest attempt for each question; rows arrive newest first."""
    latest = {}
    for index, row in enumerate(rows):
        latest.setdefault(row.get("question_id") or f"attempt-{index}", row)
    return list(latest.values())


def _topic_mastery(rows: list, question_count: int, now: datetime) -> dict:
    evidence = _latest_answer_per_question(rows)
    if not evidence:
        return {"mastery": 0, "evidence": 0, "questions": question_count}
    freshness = [0.5 ** (_age_days(row.get("created_at"), now) / HALF_LIFE_DAYS) for row in evidence]
    weights = [value * MODE_WEIGHTS.get(row.get("mode"), 1.0) for row, value in zip(evidence, freshness)]
    total_weight = sum(weights)
    accuracy = (
        sum((row["score"] / row["max_score"]) * weight for row, weight in zip(evidence, weights)) / total_weight
        if total_weight
        else 0.0
    )
    required = min(REQUIRED_QUESTIONS, question_count) if question_count else REQUIRED_QUESTIONS
    evidence_factor = min(1.0, sum(freshness) / required)
    return {
        "mastery": round(accuracy * evidence_factor * 100),
        "evidence": len(evidence),
        "questions": question_count,
    }


def calculate_readiness(subject: dict, attempts: list, now: datetime = None) -> dict:
    """Return a transparent heuristic readiness score from recent topic evidence.

    `attempts` must be ordered newest first, as returned by `StudyStore.list_attempts`.
    """
    now = now or datetime.now(timezone.utc)
    topic_ids = [topic["id"] for topic in subject.get("topics", [])]
    questions = subject.get("questions", [])
    topic_scores = {}
    for topic_id in topic_ids:
        rows = [
            row
            for row in attempts
            if row.get("topic_id") == topic_id
            and row["max_score"]
            and row.get("is_answered", True)
        ]
        question_count = sum(1 for question in questions if question["topic_id"] == topic_id)
        topic_scores[topic_id] = _topic_mastery(rows, question_count, now)

    readiness = round(
        sum(item["mastery"] for item in topic_scores.values()) / len(topic_ids)
    ) if topic_ids else 0
    covered = sum(1 for item in topic_scores.values() if item["evidence"])
    coverage = round((covered / len(topic_ids)) * 100) if topic_ids else 0
    target = int(subject.get("target_score", 80))
    is_ready = readiness >= target and coverage == 100
    # Without evidence in every topic the estimate would be a guess, so it stays unset.
    if is_ready:
        estimated_sessions = 0
    elif coverage < 100:
        estimated_sessions = None
    else:
        estimated_sessions = max(1, ceil((target - readiness) / 8))
    return {
        "score": readiness,
        "coverage": coverage,
        "estimated_sessions": estimated_sessions,
        "is_ready": is_ready,
        "topics": topic_scores,
        "target": target,
    }


def next_best_action(subject: dict, readiness: dict) -> str:
    if not subject.get("topics"):
        return "Add study materials to create a topic map."
    if not readiness["coverage"]:
        return "Take the short diagnostic to find your starting point across all topics."
    if readiness["is_ready"]:
        return "You have reached your target. Take a mock exam to confirm it under exam conditions."
    topics = readiness["topics"]
    unanswered = next((topic for topic in subject["topics"] if not topics[topic["id"]]["evidence"]), None)
    if unanswered:
        return f'Practise “{unanswered["title"]}”: it has no answers yet.'
    weakest = min(subject["topics"], key=lambda topic: topics[topic["id"]]["mastery"])
    return f'Review “{weakest["title"]}” and complete a short recall session.'
