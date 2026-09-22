from prepcanvas.grading import grade_question, grade_questions


def test_multiple_choice_requires_the_expected_option(demo_subject):
    question = next(item for item in demo_subject["questions"] if item["id"] == "carbon-1")
    assert grade_question(question, "Scope 1")["score"] == 1
    assert grade_question(question, "Scope 2")["score"] == 0


def test_short_answer_awards_partial_credit(demo_subject):
    question = next(item for item in demo_subject["questions"] if item["id"] == "circ-3")
    result = grade_question(question, "Use durable components.")
    assert result["score"] == 1
    assert result["is_correct"] is False
    assert result["matched_points"] == ["Durability"]


def test_short_answer_accepts_source_defined_phrases(demo_subject):
    question = next(item for item in demo_subject["questions"] if item["id"] == "circ-3")
    result = grade_question(question, "Use long-lasting materials and replaceable parts.")
    assert result["score"] == 2
    assert result["is_correct"] is True


def test_unrelated_answer_gets_no_credit(demo_subject):
    question = next(item for item in demo_subject["questions"] if item["id"] == "sys-3")
    result = grade_question(question, "The company should increase quarterly revenue.")
    assert result["score"] == 0


def test_definitions_must_stay_attached_to_the_correct_scope(demo_subject):
    question = next(item for item in demo_subject["questions"] if item["id"] == "carbon-3")
    result = grade_question(
        question,
        "Scope 1 means purchased energy. Scope 2 is direct. Scope 3 is value-chain emissions.",
    )
    assert result["score"] == 1
    assert result["is_correct"] is False


def test_definitions_must_stay_attached_across_commas_and_conjunctions(demo_subject):
    question = next(item for item in demo_subject["questions"] if item["id"] == "carbon-3")
    result = grade_question(
        question,
        "Scope 1 means purchased energy, while Scope 2 is direct, and Scope 3 is value-chain emissions.",
    )
    assert result["score"] == 1
    assert result["is_correct"] is False


def test_accepted_phrases_still_require_the_correct_scope_number(demo_subject):
    question = next(item for item in demo_subject["questions"] if item["id"] == "carbon-3")
    result = grade_question(
        question,
        "Scope 1 is purchased electricity. Scope 2 covers direct operational emissions. "
        "Scope 3 covers other value-chain emissions.",
    )
    assert result["score"] == 1
    assert result["is_correct"] is False


def test_negated_definitions_receive_no_credit(demo_subject):
    question = next(item for item in demo_subject["questions"] if item["id"] == "carbon-3")
    result = grade_question(
        question,
        "Scope 1 is not direct. Scope 2 is not purchased energy. Scope 3 is not value-chain emissions.",
    )
    assert result["score"] == 0
    assert result["is_correct"] is False


def test_contracted_negations_receive_no_credit(demo_subject):
    question = next(item for item in demo_subject["questions"] if item["id"] == "carbon-3")
    result = grade_question(
        question,
        "Scope 1 isn't direct. Scope 2 doesn't cover purchased energy. "
        "Scope 3 isn't value-chain emissions.",
    )
    assert result["score"] == 0
    assert result["is_correct"] is False


def test_correct_scope_definitions_receive_full_credit(demo_subject):
    question = next(item for item in demo_subject["questions"] if item["id"] == "carbon-3")
    result = grade_question(
        question,
        "Scope 1 is direct operational emissions, Scope 2 is purchased energy, "
        "and Scope 3 covers other value-chain emissions.",
    )
    assert result["score"] == 3
    assert result["is_correct"] is True


def test_blank_answer_is_not_learning_evidence(demo_subject):
    question = next(item for item in demo_subject["questions"] if item["id"] == "carbon-1")
    assert grade_question(question, "")["is_answered"] is False


def test_question_set_returns_totals(demo_subject):
    questions = demo_subject["questions"][:2]
    answers = {question["id"]: question["correct_answer"] for question in questions}
    result = grade_questions(questions, answers)
    assert result["score"] == result["max_score"] == 2
