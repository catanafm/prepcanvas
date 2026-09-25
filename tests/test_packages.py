import copy
import json

import pytest

from prepcanvas.packages import (
    PackageError,
    SubjectFiles,
    content_summary,
    has_errors,
    read_package,
    safe_material_name,
    validate_package,
)


def errors(issues):
    return [issue for issue in issues if issue["level"] == "error"]


def warnings(issues):
    return [issue for issue in issues if issue["level"] == "warning"]


def short_answer(subject):
    return next(question for question in subject["questions"] if question["type"] == "short_answer")


def test_bundled_sample_is_a_valid_package(demo_subject):
    assert validate_package(demo_subject, expected_id="sustainable-business-demo") == []
    assert content_summary(demo_subject) == {"topics": 4, "questions": 12, "source": 12, "generated": 0}


def test_schema_version_and_required_fields_are_checked():
    issues = validate_package({"id": "Bad Id", "topics": [], "questions": []})
    paths = {issue["path"] for issue in errors(issues)}
    assert {"$.schema_version", "$.id", "$.name", "$.topics", "$.questions"} <= paths
    assert validate_package([])[0]["message"] == "The package must be a JSON object."


def test_package_id_must_match_the_subject(demo_subject):
    issues = validate_package(demo_subject, expected_id="statistics-101")
    assert [issue["path"] for issue in errors(issues)] == ["$.id"]
    assert "statistics-101" in issues[0]["message"]


def test_questions_need_an_origin_and_an_existing_topic(demo_subject):
    subject = copy.deepcopy(demo_subject)
    subject["questions"][0].pop("origin")
    subject["questions"][1]["topic_id"] = "nope"
    subject["questions"][2]["origin"] = "invented"
    issues = errors(validate_package(subject))
    assert [issue["path"] for issue in issues] == [
        "$.questions[0].origin",
        "$.questions[1].topic_id",
        "$.questions[2].origin",
    ]


def test_multiple_choice_answer_must_be_one_of_the_options(demo_subject):
    subject = copy.deepcopy(demo_subject)
    subject["questions"][0]["correct_answer"] = "Something else"
    subject["questions"][1]["options"] = ["Only one"]
    issues = errors(validate_package(subject))
    assert [issue["path"] for issue in issues] == ["$.questions[0].correct_answer", "$.questions[1].options"]


def test_model_answer_must_earn_full_marks_against_its_own_rubric(demo_subject):
    subject = copy.deepcopy(demo_subject)
    question = short_answer(subject)
    question["rubric_points"][0]["accepted_phrases"] = ["phrase that never appears"]
    question["rubric_points"][0]["keywords"] = ["absent", "missing"]
    issues = errors(validate_package(subject))
    assert len(issues) == 1
    assert issues[0]["path"].endswith(".rubric_points")
    assert "1/2 against its own rubric" in issues[0]["message"]
    assert question["rubric_points"][0]["label"] in issues[0]["message"]


def test_rubric_structure_is_checked_before_grading(demo_subject):
    subject = copy.deepcopy(demo_subject)
    question = short_answer(subject)
    question["rubric_points"] = [{"label": "No way to match this", "points": 2}]
    question.pop("model_answer")
    issues = errors(validate_package(subject))
    messages = " ".join(issue["message"] for issue in issues)
    assert "model_answer" in messages
    assert "accepted_phrases" in messages


def test_rubric_points_must_reach_the_question_points(demo_subject):
    subject = copy.deepcopy(demo_subject)
    question = short_answer(subject)
    question["points"] = 5
    issues = errors(validate_package(subject))
    assert len(issues) == 1
    assert "full marks are unreachable" in issues[0]["message"]

    question["points"] = 1
    issues = validate_package(subject)
    assert not has_errors(issues)
    assert any("capped" in issue["message"] for issue in warnings(issues))


def test_duplicate_ids_are_reported(demo_subject):
    subject = copy.deepcopy(demo_subject)
    subject["topics"][1]["id"] = subject["topics"][0]["id"]
    subject["questions"][1]["id"] = subject["questions"][0]["id"]
    messages = [issue["message"] for issue in errors(validate_package(subject))]
    assert any(message.startswith("Duplicate topic id") for message in messages)
    assert any(message.startswith("Duplicate question id") for message in messages)


def test_topic_coverage_produces_errors_and_warnings(demo_subject):
    subject = copy.deepcopy(demo_subject)
    subject["questions"] = [
        question
        for question in subject["questions"]
        if question["topic_id"] != "carbon-basics"
        and not (question["topic_id"] == "systems-thinking" and question["type"] == "multiple_choice")
    ]
    issues = validate_package(subject)
    assert [issue["message"] for issue in errors(issues)] == [
        "Topic 'carbon-basics' has no questions, so it could never show progress."
    ]
    messages = [issue["message"] for issue in warnings(issues)]
    assert any("skipped by the diagnostic" in message for message in messages)
    assert any("systems-thinking' has 1 question(s)" in message for message in messages)


def test_sources_are_validated(demo_subject):
    subject = copy.deepcopy(demo_subject)
    subject["sources"] = [{"id": "x", "role": "homework", "title": "X"}]
    issues = errors(validate_package(subject))
    assert [issue["path"] for issue in issues] == ["$.sources[0].role"]


def test_read_package_reports_missing_and_broken_files(tmp_path):
    with pytest.raises(PackageError, match="No package found"):
        read_package(tmp_path / "package.json")
    broken = tmp_path / "package.json"
    broken.write_text("{not json", encoding="utf-8")
    with pytest.raises(PackageError, match="not valid JSON"):
        read_package(broken)


def test_subject_files_round_trip(tmp_path, demo_subject):
    files = SubjectFiles(tmp_path / "private")
    subject_id = "statistics-101"
    assert files.load_package(subject_id)["state"] == "missing"
    assert files.list_materials(subject_id) == []

    saved = files.save_material(subject_id, "../My Notes (v2).PDF", b"%PDF-1.4")
    assert saved.name == "My-Notes-v2.pdf"
    assert saved.parent == files.materials_dir(subject_id)
    assert files.list_materials(subject_id) == [{"name": "My-Notes-v2.pdf", "bytes": 8}]
    with pytest.raises(ValueError, match="Unsupported file type"):
        files.save_material(subject_id, "script.exe", b"MZ")

    brief_path = files.write_brief({"id": subject_id, "name": "Statistics 101", "exam_date": "2026-12-01", "target_score": 75})
    brief = files.read_brief(subject_id)
    assert brief_path.name == "brief.json"
    assert brief["name"] == "Statistics 101" and brief["target_score"] == 75

    files.save_package(subject_id, json.dumps(demo_subject).encode("utf-8"))
    status = files.load_package(subject_id)
    assert status["state"] == "invalid"
    assert status["issues"][0]["path"] == "$.id"

    package = {**demo_subject, "id": subject_id}
    files.save_package(subject_id, json.dumps(package).encode("utf-8"))
    status = files.load_package(subject_id)
    assert status["state"] == "valid"
    assert status["issues"] == []
    assert len(status["package"]["questions"]) == 12
    assert "_warnings" not in status["package"]

    files.remove_material(subject_id, "My-Notes-v2.pdf")
    assert files.list_materials(subject_id) == []
    files.delete_subject(subject_id)
    assert not files.subject_dir(subject_id).exists()


@pytest.mark.parametrize(
    "raw, expected",
    [("workbook.pdf", "workbook.pdf"), ("Practice Exam 2024.docx", "Practice-Exam-2024.docx"), ("..", "material"), ("", "material")],
)
def test_material_names_are_flattened(raw, expected):
    assert safe_material_name(raw) == expected
