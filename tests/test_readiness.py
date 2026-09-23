from datetime import datetime, timedelta, timezone

from prepcanvas.readiness import calculate_readiness, next_best_action


NOW = datetime(2026, 9, 23, 12, 0, tzinfo=timezone.utc)


def attempt(question_id, topic_id="systems-thinking", score=1, max_score=1, mode="practice", days_ago=0):
    return {
        "question_id": question_id,
        "topic_id": topic_id,
        "score": score,
        "max_score": max_score,
        "mode": mode,
        "is_answered": True,
        "created_at": (NOW - timedelta(days=days_ago)).isoformat(),
    }


def test_no_evidence_means_zero_readiness(demo_subject):
    result = calculate_readiness(demo_subject, [], now=NOW)
    assert result["score"] == 0
    assert result["coverage"] == 0
    assert result["estimated_sessions"] is None


def test_full_mastery_requires_distinct_questions(demo_subject):
    attempts = [attempt("sys-1"), attempt("sys-2"), attempt("sys-3", max_score=2, score=2)]
    result = calculate_readiness(demo_subject, attempts, now=NOW)
    assert result["topics"]["systems-thinking"] == {"mastery": 100, "evidence": 3, "questions": 3}
    assert result["coverage"] == 25
    assert result["score"] == 25


def test_repeating_one_question_cannot_reach_full_mastery(demo_subject):
    attempts = [attempt("sys-1") for _ in range(10)]
    topic = calculate_readiness(demo_subject, attempts, now=NOW)["topics"]["systems-thinking"]
    assert topic["evidence"] == 1
    assert topic["mastery"] == 33


def test_latest_answer_to_a_question_replaces_earlier_ones(demo_subject):
    # Newest first: the learner recently got sys-1 wrong after earlier correct answers.
    attempts = [attempt("sys-1", score=0), attempt("sys-1", days_ago=1), attempt("sys-1", days_ago=2)]
    topic = calculate_readiness(demo_subject, attempts, now=NOW)["topics"]["systems-thinking"]
    assert topic["mastery"] == 0


def test_mock_exam_answers_weigh_more_than_practice(demo_subject):
    practice_miss = [attempt("sys-1"), attempt("sys-2"), attempt("sys-3", score=0, max_score=2)]
    mock_miss = [attempt("sys-1"), attempt("sys-2"), attempt("sys-3", score=0, max_score=2, mode="mock_exam")]
    practice = calculate_readiness(demo_subject, practice_miss, now=NOW)["topics"]["systems-thinking"]
    mock = calculate_readiness(demo_subject, mock_miss, now=NOW)["topics"]["systems-thinking"]
    assert practice["mastery"] == 67
    assert mock["mastery"] == 57


def test_old_evidence_decays(demo_subject):
    fresh = [attempt(question_id) for question_id in ("sys-1", "sys-2", "sys-3")]
    stale = [attempt(question_id, days_ago=14) for question_id in ("sys-1", "sys-2", "sys-3")]
    assert calculate_readiness(demo_subject, fresh, now=NOW)["topics"]["systems-thinking"]["mastery"] == 100
    assert calculate_readiness(demo_subject, stale, now=NOW)["topics"]["systems-thinking"]["mastery"] == 50


def all_questions(demo_subject, score_ratio=1.0):
    return [
        attempt(question["id"], topic_id=question["topic_id"], score=question["points"] * score_ratio,
                max_score=question["points"])
        for question in demo_subject["questions"]
    ]


def test_estimate_appears_once_every_topic_has_evidence(demo_subject):
    result = calculate_readiness(demo_subject, all_questions(demo_subject, score_ratio=0.5), now=NOW)
    assert result["coverage"] == 100
    assert result["score"] == 50
    assert result["estimated_sessions"] == 4


def test_ready_subject_needs_no_more_sessions(demo_subject):
    result = calculate_readiness(demo_subject, all_questions(demo_subject), now=NOW)
    assert result["is_ready"] is True
    assert result["estimated_sessions"] == 0


def test_next_action_without_evidence_recommends_the_subject_diagnostic(demo_subject):
    readiness = calculate_readiness(demo_subject, [], now=NOW)
    action = next_best_action(demo_subject, readiness)
    assert action == "Take the short diagnostic to find your starting point across all topics."
    assert not any(topic["title"] in action for topic in demo_subject["topics"])


def test_next_action_with_partial_coverage_points_to_an_unanswered_topic(demo_subject):
    readiness = calculate_readiness(demo_subject, [attempt("sys-1")], now=NOW)
    assert next_best_action(demo_subject, readiness) == "Practise “Stakeholder value”: it has no answers yet."


def test_next_action_with_full_coverage_reviews_the_weakest_topic(demo_subject):
    demo_subject["target_score"] = 100
    attempts = all_questions(demo_subject)
    attempts[0] = {**attempts[0], "score": 0}
    readiness = calculate_readiness(demo_subject, attempts, now=NOW)
    weakest = next(topic for topic in demo_subject["topics"] if topic["id"] == attempts[0]["topic_id"])
    assert readiness["is_ready"] is False
    assert next_best_action(demo_subject, readiness) == (
        f'Review “{weakest["title"]}” and complete a short recall session.'
    )


def test_next_action_when_ready_suggests_a_mock_exam(demo_subject):
    readiness = calculate_readiness(demo_subject, all_questions(demo_subject), now=NOW)
    assert "mock exam" in next_best_action(demo_subject, readiness)


def test_blank_attempt_does_not_increase_coverage(demo_subject):
    blank = {**attempt("sys-1", score=0), "is_answered": False}
    result = calculate_readiness(demo_subject, [blank], now=NOW)
    assert result["coverage"] == 0


def test_ready_requires_coverage_across_every_topic(demo_subject):
    demo_subject["target_score"] = 50
    attempts = [
        attempt(question["id"], topic_id=question["topic_id"])
        for question in demo_subject["questions"]
        if question["topic_id"] in {"systems-thinking", "stakeholder-value"}
    ]
    result = calculate_readiness(demo_subject, attempts, now=NOW)
    assert result["score"] == 50
    assert result["coverage"] == 50
    assert result["is_ready"] is False
    assert result["estimated_sessions"] is None


def test_timestamps_without_timezone_are_treated_as_utc(demo_subject):
    naive = {**attempt("sys-1"), "created_at": NOW.replace(tzinfo=None).isoformat()}
    result = calculate_readiness(demo_subject, [naive], now=NOW)
    assert result["topics"]["systems-thinking"]["mastery"] == 33
