from prepcanvas.readiness import calculate_readiness, next_best_action


def test_no_evidence_means_zero_readiness(demo_subject):
    result = calculate_readiness(demo_subject, [])
    assert result["score"] == 0
    assert result["coverage"] == 0
    assert result["estimated_sessions"] > 0


def test_readiness_requires_repeated_topic_evidence(demo_subject):
    attempts = [
        {"topic_id": "systems-thinking", "score": 1, "max_score": 1},
        {"topic_id": "systems-thinking", "score": 1, "max_score": 1},
        {"topic_id": "systems-thinking", "score": 1, "max_score": 1},
    ]
    result = calculate_readiness(demo_subject, attempts)
    assert result["topics"]["systems-thinking"]["mastery"] == 100
    assert result["coverage"] == 25
    assert result["score"] == 25


def test_next_action_targets_a_topic_without_evidence(demo_subject):
    readiness = calculate_readiness(demo_subject, [])
    assert "diagnostic" in next_best_action(demo_subject, readiness).lower()


def test_blank_attempt_does_not_increase_coverage(demo_subject):
    attempts = [
        {
            "topic_id": "systems-thinking",
            "score": 0,
            "max_score": 1,
            "is_answered": False,
        }
    ]
    result = calculate_readiness(demo_subject, attempts)
    assert result["coverage"] == 0


def test_ready_requires_coverage_across_every_topic(demo_subject):
    demo_subject["target_score"] = 50
    attempts = []
    for topic_id in ["systems-thinking", "stakeholder-value"]:
        attempts.extend(
            {"topic_id": topic_id, "score": 1, "max_score": 1, "is_answered": True}
            for _ in range(3)
        )
    result = calculate_readiness(demo_subject, attempts)
    assert result["score"] == 50
    assert result["coverage"] == 50
    assert result["is_ready"] is False
    assert result["estimated_sessions"] > 0
