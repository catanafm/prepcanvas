import pytest

from prepcanvas.grading import grade_question, grade_questions, stem


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


def grade(demo_subject, question_id, answer):
    question = next(item for item in demo_subject["questions"] if item["id"] == question_id)
    return grade_question(question, answer)


@pytest.mark.parametrize(
    "question_id, answer, expected",
    [
        ("circ-3", "Durability and repairability.", 2),
        ("circ-3", "Make it repairable and long lasting.", 2),
        ("circ-3", "The product should be not only durable but also modular.", 2),
        ("sys-3", "It ignores trade offs; the system boundary is narrow.", 2),
        (
            "carbon-3",
            "Scope one is direct, scope two is purchased energy, scope three covers the value chain.",
            3,
        ),
        ("carbon-3", "Scope 3: value chain.", 1),
    ],
)
def test_correct_answers_in_natural_wording_receive_credit(demo_subject, question_id, answer, expected):
    assert grade(demo_subject, question_id, answer)["score"] == expected


@pytest.mark.parametrize("spelling", ["trade-offs", "trade offs", "tradeoffs", "trade-off"])
def test_hyphenated_keywords_match_any_spelling(demo_subject, spelling):
    result = grade(demo_subject, "sys-3", f"The decision ignores {spelling}.")
    assert result["matched_points"] == ["Recognizes trade-offs or unintended consequences"]


@pytest.mark.parametrize(
    "forms",
    [
        ("durable", "durability"),
        ("repair", "repairable", "repairability", "repaired"),
        ("modular", "modularity"),
        ("influence", "influenced", "influences"),
        ("boundary", "boundaries"),
    ],
)
def test_inflected_forms_share_a_stem(forms):
    assert len({stem(word) for word in forms}) == 1


def test_unrelated_words_do_not_collapse_into_rubric_stems():
    assert stem("during") != stem("durable")


def test_real_negation_still_blocks_credit_after_not_only_handling(demo_subject):
    result = grade(demo_subject, "circ-3", "It is not durable and it is not modular.")
    assert result["score"] == 0


def test_bare_keyword_list_does_not_receive_full_credit(demo_subject):
    stuffed = "durable modular repair boundary narrow trade-offs consequences affected stakeholder influence decision"
    assert grade(demo_subject, "stake-3", stuffed)["score"] == 1
    assert grade(demo_subject, "sys-3", stuffed)["score"] == 1


def test_one_sentence_explanation_can_cover_several_points(demo_subject):
    result = grade(demo_subject, "stake-3", "Ask how strongly the affected stakeholder can influence the decision")
    assert result["score"] == 2


def test_every_model_answer_receives_full_credit(demo_subject):
    for question in demo_subject["questions"]:
        if question["type"] == "short_answer":
            result = grade_question(question, question["model_answer"])
            assert result["is_correct"], question["id"]
