import copy

from prepcanvas.exams import (
    available_sets,
    compose_variant,
    default_duration,
    describe,
    exam_questions,
    format_duration,
    next_variant,
    shortfalls,
    time_status,
)
from prepcanvas.packages import validate_package


def test_sample_blueprint_is_fillable(demo_subject):
    assert shortfalls(demo_subject) == []
    assert available_sets(demo_subject) == ["variant", "all"]


def test_variants_are_deterministic_and_follow_the_blueprint(demo_subject):
    first = compose_variant(demo_subject, 4)
    again = compose_variant(demo_subject, 4)
    assert [q["id"] for q in first] == [q["id"] for q in again]
    assert [q["type"] for q in first] == ["multiple_choice"] * 4 + ["short_answer"] * 2
    assert describe(first) == "4 multiple choice · 2 short answer · 8 points"
    assert len({q["id"] for q in first}) == 6


def test_variants_differ_and_spread_across_topics(demo_subject):
    variants = [compose_variant(demo_subject, n) for n in range(1, 6)]
    assert len({tuple(q["id"] for q in variant) for variant in variants}) > 1
    for variant in variants:
        multiple_choice = [q for q in variant if q["type"] == "multiple_choice"]
        assert len({q["topic_id"] for q in multiple_choice}) == 4, "one multiple-choice question per topic"


def test_sections_are_presented_in_course_order(demo_subject):
    order = {topic["id"]: index for index, topic in enumerate(demo_subject["topics"])}
    variant = compose_variant(demo_subject, 2)
    multiple_choice = [order[q["topic_id"]] for q in variant if q["type"] == "multiple_choice"]
    assert multiple_choice == sorted(multiple_choice)


def test_exam_sets_select_the_right_questions(demo_subject):
    for question in demo_subject["questions"]:
        if question["topic_id"] == "carbon-basics":
            question["origin"] = "generated"
    assert available_sets(demo_subject) == ["source", "variant", "all"]
    assert len(exam_questions(demo_subject, "source")) == 9
    assert len(exam_questions(demo_subject, "all")) == 12
    assert len(exam_questions(demo_subject, "variant", 3)) == 6


def test_package_without_blueprint_offers_no_variants(demo_subject):
    demo_subject.pop("exam_blueprint")
    assert compose_variant(demo_subject, 1) == []
    assert available_sets(demo_subject) == ["all"]


def test_blueprint_is_validated_against_the_pool(demo_subject):
    subject = copy.deepcopy(demo_subject)
    subject["exam_blueprint"]["sections"][0]["count"] = 9
    subject["exam_blueprint"]["sections"].append({"type": "short_answer", "count": 1, "points": 7})
    errors = [issue for issue in validate_package(subject) if issue["level"] == "error"]
    assert [issue["path"] for issue in errors] == ["$.exam_blueprint.sections[0]", "$.exam_blueprint.sections[2]"]
    assert "needs 9 multiple_choice question(s) worth 1 point(s) but the pool has 8" in errors[0]["message"]

    subject["exam_blueprint"] = {"sections": []}
    assert validate_package(subject)[0]["path"] == "$.exam_blueprint"


def test_duration_comes_from_the_blueprint_or_the_points(demo_subject):
    questions = compose_variant(demo_subject, 1)
    assert default_duration(demo_subject, questions) == 30, "8 points rounds up to the 30-minute floor"
    demo_subject["exam_blueprint"]["duration_minutes"] = 45
    assert default_duration(demo_subject, questions) == 45
    demo_subject.pop("exam_blueprint")
    assert default_duration(demo_subject, demo_subject["questions"] * 5) == 85, "17 points × 5 copies"


def test_time_formatting_and_status():
    assert format_duration(30) == "30 s"
    assert format_duration(125) == "2 min 05 s"
    assert format_duration(600) == "10 min"
    assert format_duration(3900) == "1 h 05 min"
    assert time_status(0, 700) == "11 min, no time limit"
    assert time_status(5400, 2520) == "42 min of 1 h 30 min"
    assert time_status(5400, 5700) == "1 h 35 min, over the 1 h 30 min limit by 5 min"


def test_blueprint_duration_is_validated(demo_subject):
    demo_subject["exam_blueprint"]["duration_minutes"] = "ninety"
    assert [issue["path"] for issue in validate_package(demo_subject)] == ["$.exam_blueprint.duration_minutes"]


def test_next_variant_skips_sat_ones():
    assert next_variant([]) == 1
    assert next_variant([1, 2, 4]) == 3
