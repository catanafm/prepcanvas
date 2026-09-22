import re


def normalize_text(value: str) -> str:
    lowered = (value or "").lower()
    lowered = re.sub(r"n['’]t\b", " not", lowered)
    return " ".join(re.sub(r"[^a-z0-9\s-]", " ", lowered).split())


def _matches_rubric_point(answer: str, point: dict) -> bool:
    phrases = [normalize_text(item) for item in point.get("accepted_phrases", [])]
    keywords = {normalize_text(item) for item in point.get("keywords", [])}
    keywords.discard("")
    required = {normalize_text(item) for item in point.get("required_keywords", [])}
    required.discard("")
    minimum = point.get("minimum_keyword_matches", len(keywords))
    clause_texts = [
        normalize_text(item)
        for item in re.split(r"[.!?;,\n]+|\b(?:and|but|while|whereas)\b", answer or "", flags=re.IGNORECASE)
    ]
    for clause_text in clause_texts:
        clause = set(clause_text.split())
        if not clause or clause & {"no", "not", "never"} or not required <= clause:
            continue
        if any(phrase and phrase in clause_text for phrase in phrases):
            return True
        if keywords and len(clause & keywords) >= minimum:
            return True
    return False


def grade_question(question: dict, answer: str) -> dict:
    """Grade one demo question without an external AI service."""
    is_answered = bool(normalize_text(answer))
    if question["type"] == "multiple_choice":
        is_correct = normalize_text(answer) == normalize_text(question["correct_answer"])
        awarded = question["points"] if is_correct else 0
        return {
            "question_id": question["id"],
            "topic_id": question["topic_id"],
            "score": awarded,
            "max_score": question["points"],
            "is_answered": is_answered,
            "is_correct": is_correct,
            "matched_points": [],
            "missing_points": [] if is_correct else [question["correct_answer"]],
            "feedback": question["explanation"],
        }

    matched = []
    missing = []
    score = 0
    for point in question["rubric_points"]:
        if _matches_rubric_point(answer, point):
            matched.append(point["label"])
            score += point["points"]
        else:
            missing.append(point["label"])
    score = min(score, question["points"])
    return {
        "question_id": question["id"],
        "topic_id": question["topic_id"],
        "score": score,
        "max_score": question["points"],
        "is_answered": is_answered,
        "is_correct": score == question["points"],
        "matched_points": matched,
        "missing_points": missing,
        "feedback": question["explanation"],
    }


def grade_questions(questions: list, answers: dict) -> dict:
    results = [grade_question(question, answers.get(question["id"], "")) for question in questions]
    return {
        "results": results,
        "score": sum(item["score"] for item in results),
        "max_score": sum(item["max_score"] for item in results),
    }
