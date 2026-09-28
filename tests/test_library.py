from datetime import date, datetime, timedelta, timezone

import pytest

from prepcanvas.library import exam_countdown, group_subjects, last_activity


TODAY = date(2026, 9, 24)
NOW = datetime(2026, 9, 24, 12, 0, tzinfo=timezone.utc)


@pytest.mark.parametrize(
    "exam_date, expected",
    [
        (None, "No exam date"),
        ("", "No exam date"),
        ("2026-10-06", "Exam in 12 days"),
        ("2026-09-25", "Exam tomorrow"),
        ("2026-09-24", "Exam today"),
        ("2026-09-23", "Exam was yesterday"),
        ("2026-09-14", "Exam was 10 days ago"),
    ],
)
def test_exam_countdown(exam_date, expected):
    assert exam_countdown(exam_date, TODAY) == expected


def attempt(days_ago):
    return {"created_at": (NOW - timedelta(days=days_ago)).isoformat()}


@pytest.mark.parametrize(
    "attempts, expected",
    [
        ([], "Not started"),
        ([attempt(0)], "Studied today"),
        ([attempt(1), attempt(5)], "Studied yesterday"),
        ([attempt(4)], "Studied 4 days ago"),
    ],
)
def test_last_activity_uses_the_newest_attempt(attempts, expected):
    assert last_activity(attempts, NOW) == expected


def test_group_subjects_by_status_with_soonest_exam_first():
    subjects = [
        {"name": "No date", "status": "active", "exam_date": None},
        {"name": "Later", "status": "active", "exam_date": "2026-12-01"},
        {"name": "Sooner", "status": "active", "exam_date": "2026-10-01"},
        {"name": "Done", "status": "completed", "exam_date": "2026-06-01"},
        {"name": "Legacy row without status", "exam_date": None},
    ]
    groups = group_subjects(subjects)
    assert [s["name"] for s in groups["active"]] == ["Sooner", "Later", "Legacy row without status", "No date"]
    assert [s["name"] for s in groups["completed"]] == ["Done"]


def test_recently_studied_subjects_come_before_never_studied_ones():
    subjects = [
        {"id": "a", "name": "Algebra", "exam_date": "2026-10-01", "status": "active"},
        {"id": "b", "name": "Biology", "exam_date": "2026-12-01", "status": "active"},
        {"id": "c", "name": "Chemistry", "exam_date": None, "status": "active"},
        {"id": "d", "name": "Drama", "exam_date": "2026-11-01", "status": "completed"},
    ]
    last_studied = {"b": "2026-09-27T10:00:00+00:00", "c": "2026-09-28T08:00:00+00:00", "a": None}
    groups = group_subjects(subjects, last_studied)
    assert [s["id"] for s in groups["active"]] == ["c", "b", "a"], "newest activity first, then soonest exam"
    assert [s["id"] for s in groups["completed"]] == ["d"]
    assert [s["id"] for s in group_subjects(subjects)["active"]] == ["a", "b", "c"], "without activity: soonest exam first"
