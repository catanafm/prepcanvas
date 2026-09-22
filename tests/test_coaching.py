from prepcanvas.coaching import recommend_strategy


def test_low_score_selects_guided_foundations():
    assert recommend_strategy(0.25, 3)["id"] == "guided_foundations"


def test_middle_score_selects_coach_and_recall():
    assert recommend_strategy(0.65, 4)["id"] == "coach_and_recall"


def test_high_score_and_confidence_select_exam_simulation():
    assert recommend_strategy(0.9, 5)["id"] == "exam_simulation"
