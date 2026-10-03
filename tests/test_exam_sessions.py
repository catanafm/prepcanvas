import copy

from prepcanvas.exam_sessions import exam_identity


def test_identity_includes_subject_content_and_selection(demo_subject):
    original = exam_identity(demo_subject, "variant", 1)
    assert original == exam_identity(copy.deepcopy(demo_subject), "variant", 1)
    for changed in [dict(demo_subject, id="other"), dict(demo_subject, topics=[])]:
        assert original != exam_identity(changed, "variant", 1)
    changed = copy.deepcopy(demo_subject)
    changed["questions"][0]["correct_answer"] = "New correct answer"
    assert original != exam_identity(changed, "variant", 1)
    assert original != exam_identity(demo_subject, "variant", 2)
    assert original != exam_identity(demo_subject, "all", None)
