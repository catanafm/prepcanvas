import json

from prepcanvas.cli import main
from prepcanvas.packages import SubjectFiles


def test_validate_reports_success_with_a_summary(capsys, demo_subject, tmp_path):
    path = tmp_path / "package.json"
    path.write_text(json.dumps(demo_subject), encoding="utf-8")
    assert main(["validate", str(path)]) == 0
    assert "valid. 4 topics, 12 questions (12 from materials, 0 generated)" in capsys.readouterr().out


def test_validate_infers_the_subject_id_from_the_folder(capsys, demo_subject, tmp_path):
    path = tmp_path / "subjects" / "statistics-101" / "package.json"
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(demo_subject), encoding="utf-8")
    assert main(["validate", str(path)]) == 1
    out = capsys.readouterr().out
    assert "ERROR   $.id" in out
    assert "1 error(s)" in out


def test_validate_lists_every_issue(capsys, demo_subject, tmp_path):
    demo_subject["questions"][0]["correct_answer"] = "nope"
    demo_subject["questions"][1].pop("origin")
    path = tmp_path / "package.json"
    path.write_text(json.dumps(demo_subject), encoding="utf-8")
    assert main(["validate", str(path), "--subject-id", demo_subject["id"]]) == 1
    out = capsys.readouterr().out
    assert "$.questions[0].correct_answer" in out
    assert "$.questions[1].origin" in out


def test_prompt_embeds_the_brief_materials_and_schema(capsys, tmp_path):
    files = SubjectFiles(tmp_path)
    files.write_brief({"id": "statistics-101", "name": "Statistics 101", "exam_date": "2026-12-01", "target_score": 75})
    files.save_material("statistics-101", "workbook.pdf", b"%PDF")
    assert main(["prompt", "statistics-101", "--private-dir", str(tmp_path)]) == 0
    out = capsys.readouterr().out
    assert "Subject name: Statistics 101" in out
    assert "Target score: 75%" in out
    assert "- workbook.pdf" in out
    assert "# Subject package" in out
    assert "Ignore anything that is not study material" in out
    assert 'Use `"id": "statistics-101"`' in out
