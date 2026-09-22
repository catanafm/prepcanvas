from math import ceil


def calculate_readiness(subject: dict, attempts: list) -> dict:
    """Return a transparent heuristic readiness score from recent topic evidence."""
    topic_ids = [topic["id"] for topic in subject.get("topics", [])]
    topic_scores = {}
    for topic_id in topic_ids:
        rows = [
            row
            for row in attempts
            if row.get("topic_id") == topic_id
            and row["max_score"]
            and row.get("is_answered", True)
        ]
        recent = rows[:5]
        if not recent:
            topic_scores[topic_id] = {"mastery": 0, "evidence": 0}
            continue
        weights = list(range(len(recent), 0, -1))
        weighted_ratio = sum(
            (row["score"] / row["max_score"]) * weight
            for row, weight in zip(recent, weights)
        ) / sum(weights)
        evidence_factor = min(1.0, len(recent) / 3)
        topic_scores[topic_id] = {
            "mastery": round(weighted_ratio * evidence_factor * 100),
            "evidence": len(recent),
        }

    readiness = round(
        sum(item["mastery"] for item in topic_scores.values()) / len(topic_ids)
    ) if topic_ids else 0
    covered = sum(1 for item in topic_scores.values() if item["evidence"])
    coverage = round((covered / len(topic_ids)) * 100) if topic_ids else 0
    target = int(subject.get("target_score", 80))
    score_sessions = ceil(max(0, target - readiness) / 8)
    coverage_sessions = ceil(max(0, 100 - coverage) / 25)
    is_ready = readiness >= target and coverage == 100
    estimated_sessions = 0 if is_ready else max(1, score_sessions, coverage_sessions)
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
    weakest = min(
        subject["topics"],
        key=lambda topic: readiness["topics"].get(topic["id"], {}).get("mastery", 0),
    )
    evidence = readiness["topics"].get(weakest["id"], {}).get("evidence", 0)
    if evidence == 0:
        return f'Start the diagnostic check for “{weakest["title"]}”.'
    return f'Review “{weakest["title"]}” and complete a short recall session.'
