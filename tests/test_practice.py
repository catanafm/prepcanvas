import random

from prepcanvas.practice import next_question, practice_order, question_status, random_question, remaining


def attempt(question_id, created_at, score=1):
    return {"question_id": question_id, "created_at": created_at, "score": score, "max_score": 1}


def test_unanswered_questions_come_first_then_the_oldest_answers(demo_subject):
    questions = demo_subject["questions"][:4]
    attempts = [attempt("sys-2", "2026-09-25T10:00:00+00:00"), attempt("sys-1", "2026-09-20T10:00:00+00:00")]
    assert [q["id"] for q in practice_order(questions, attempts)] == ["sys-3", "stake-1", "sys-1", "sys-2"]
    assert remaining(questions, attempts) == 2


def test_next_question_skips_the_one_on_screen(demo_subject):
    questions = demo_subject["questions"][:2]
    assert next_question(questions, [], current_id="sys-1")["id"] == "sys-2"
    assert next_question(questions[:1], [], current_id="sys-1")["id"] == "sys-1"


def test_random_question_never_repeats_the_current_one(demo_subject):
    questions = demo_subject["questions"][:3]
    rng = random.Random(1)
    for _ in range(20):
        assert random_question(questions, "sys-2", rng)["id"] != "sys-2"


def test_status_names_the_last_answer(demo_subject):
    question = demo_subject["questions"][0]
    assert question_status(question, []) == "Not answered yet"
    status = question_status(question, [attempt("sys-1", "2026-09-25T10:00:00+00:00", score=0)])
    assert status.startswith("Last answered 25 Sep") and status.endswith("0/1")
