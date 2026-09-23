import pytest

from prepcanvas.catalog import diagnostic_questions, get_question, get_topic


def test_diagnostic_uses_one_multiple_choice_question_per_topic(demo_subject):
    questions = diagnostic_questions(demo_subject)
    assert [question["topic_id"] for question in questions] == [topic["id"] for topic in demo_subject["topics"]]
    assert all(question["type"] == "multiple_choice" for question in questions)


def test_diagnostic_skips_topics_without_multiple_choice_questions(demo_subject):
    demo_subject["questions"] = [
        question
        for question in demo_subject["questions"]
        if not (question["topic_id"] == "carbon-basics" and question["type"] == "multiple_choice")
    ]
    topics = [question["topic_id"] for question in diagnostic_questions(demo_subject)]
    assert "carbon-basics" not in topics
    assert len(topics) == len(demo_subject["topics"]) - 1


def test_subject_without_questions_has_no_diagnostic(demo_subject):
    demo_subject["questions"] = []
    assert diagnostic_questions(demo_subject) == []


def test_unknown_ids_raise_descriptive_key_errors(demo_subject):
    with pytest.raises(KeyError, match="Unknown topic 'nope'"):
        get_topic(demo_subject, "nope")
    with pytest.raises(KeyError, match="Unknown question 'nope'"):
        get_question(demo_subject, "nope")
