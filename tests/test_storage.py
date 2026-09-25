import sqlite3

import pytest

from prepcanvas import storage
from prepcanvas.storage import StudyStore


def test_subjects_and_attempts_are_isolated(tmp_path, demo_subject):
    store = StudyStore(tmp_path / "progress.sqlite3")
    store.seed_demo_subject(demo_subject)
    store.create_subject("other", "Other subject", "", 75, {"notes": True})
    store.save_attempt(
        demo_subject["id"],
        "practice",
        {"topic_id": "systems-thinking", "question_id": "sys-1", "score": 1, "max_score": 1},
    )
    assert len(store.list_attempts(demo_subject["id"])) == 1
    assert store.list_attempts("other") == []


def test_coaching_profile_can_be_updated(tmp_path, demo_subject):
    store = StudyStore(tmp_path / "progress.sqlite3")
    store.seed_demo_subject(demo_subject)
    strategy = {"id": "guided", "name": "Guided", "description": "Start with examples."}
    store.save_profile(demo_subject["id"], strategy, 0.3, 2)
    profile = store.get_profile(demo_subject["id"])
    assert profile["strategy_name"] == "Guided"
    assert profile["confidence"] == 2


def test_demo_metadata_is_refreshed_without_deleting_progress(tmp_path, demo_subject):
    store = StudyStore(tmp_path / "progress.sqlite3")
    store.seed_demo_subject(demo_subject)
    updated = {**demo_subject, "name": "Updated demo name", "target_score": 75}
    store.seed_demo_subject(updated)
    subject = store.get_subject(demo_subject["id"])
    assert subject["name"] == "Updated demo name"
    assert subject["target_score"] == 75


def test_every_connection_is_closed(tmp_path, demo_subject, monkeypatch):
    opened = []
    real_connect = sqlite3.connect

    def tracking_connect(*args, **kwargs):
        connection = real_connect(*args, **kwargs)
        opened.append(connection)
        return connection

    monkeypatch.setattr(storage.sqlite3, "connect", tracking_connect)
    store = StudyStore(tmp_path / "progress.sqlite3")
    store.seed_demo_subject(demo_subject)
    store.save_attempt(
        demo_subject["id"],
        "practice",
        {"topic_id": "systems-thinking", "question_id": "sys-1", "score": 1, "max_score": 1},
    )
    store.list_attempts(demo_subject["id"])
    store.list_subjects()

    assert len(opened) >= 5
    for connection in opened:
        with pytest.raises(sqlite3.ProgrammingError):
            connection.execute("SELECT 1")


def test_writes_are_committed_before_the_connection_closes(tmp_path, demo_subject):
    path = tmp_path / "progress.sqlite3"
    StudyStore(path).seed_demo_subject(demo_subject)
    assert StudyStore(path).get_subject(demo_subject["id"])["name"] == demo_subject["name"]


def test_attempts_require_an_existing_subject(tmp_path):
    store = StudyStore(tmp_path / "progress.sqlite3")
    with pytest.raises(sqlite3.IntegrityError):
        store.save_attempt("missing-subject", "practice", {"score": 1, "max_score": 1})


def seed_progress(store, subject_id):
    store.save_attempt(subject_id, "practice", {"topic_id": "t", "question_id": "q", "score": 1, "max_score": 1})
    store.save_profile(subject_id, {"id": "guided", "name": "Guided", "description": "Examples."}, 0.3, 2)


def test_reset_progress_keeps_the_subject_and_other_subjects(tmp_path, demo_subject):
    store = StudyStore(tmp_path / "progress.sqlite3")
    store.seed_demo_subject(demo_subject)
    store.create_subject("other", "Other subject", "", 75, {})
    seed_progress(store, demo_subject["id"])
    seed_progress(store, "other")

    store.reset_progress(demo_subject["id"])

    assert store.get_subject(demo_subject["id"]) is not None
    assert store.list_attempts(demo_subject["id"]) == []
    assert store.get_profile(demo_subject["id"]) is None
    assert len(store.list_attempts("other")) == 1
    assert store.get_profile("other") is not None


def test_delete_subject_removes_its_progress(tmp_path):
    store = StudyStore(tmp_path / "progress.sqlite3")
    store.create_subject("other", "Other subject", "", 75, {})
    seed_progress(store, "other")

    store.delete_subject("other")

    assert store.get_subject("other") is None
    assert store.list_attempts("other") == []
    assert store.get_profile("other") is None


def test_sample_subject_is_not_deleted_through_delete_subject(tmp_path, demo_subject):
    store = StudyStore(tmp_path / "progress.sqlite3")
    store.seed_demo_subject(demo_subject)
    with pytest.raises(ValueError):
        store.delete_subject(demo_subject["id"])
    assert store.get_subject(demo_subject["id"]) is not None


def test_deleting_an_unknown_subject_raises(tmp_path):
    with pytest.raises(KeyError):
        StudyStore(tmp_path / "progress.sqlite3").delete_subject("missing")


def test_subjects_start_active_and_can_be_completed(tmp_path):
    store = StudyStore(tmp_path / "progress.sqlite3")
    store.create_subject("other", "Other subject", "", 75, {})
    assert store.get_subject("other")["status"] == "active"
    store.set_status("other", "completed")
    assert store.get_subject("other")["status"] == "completed"


def test_invalid_status_and_unknown_subject_are_rejected(tmp_path):
    store = StudyStore(tmp_path / "progress.sqlite3")
    store.create_subject("other", "Other subject", "", 75, {})
    with pytest.raises(ValueError):
        store.set_status("other", "archived-forever")
    with pytest.raises(KeyError):
        store.set_status("missing", "completed")


def test_existing_databases_gain_the_status_column(tmp_path):
    path = tmp_path / "legacy.sqlite3"
    with sqlite3.connect(path) as connection:
        connection.execute(
            "CREATE TABLE subjects (id TEXT PRIMARY KEY, name TEXT NOT NULL, description TEXT NOT NULL DEFAULT '', "
            "exam_date TEXT, target_score INTEGER NOT NULL DEFAULT 80, materials_json TEXT NOT NULL, "
            "is_demo INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL)"
        )
        connection.execute(
            "INSERT INTO subjects VALUES ('old', 'Old subject', '', NULL, 80, '{}', 0, '2026-01-01T00:00:00+00:00')"
        )
    connection.close()
    assert StudyStore(path).get_subject("old")["status"] == "active"


def test_removed_sample_stays_removed_across_restarts(tmp_path, demo_subject):
    path = tmp_path / "progress.sqlite3"
    store = StudyStore(path)
    store.ensure_sample_subject(demo_subject)
    seed_progress(store, demo_subject["id"])

    store.remove_sample_subject(demo_subject["id"])
    restarted = StudyStore(path)
    restarted.ensure_sample_subject(demo_subject)

    assert restarted.sample_removed()
    assert restarted.get_subject(demo_subject["id"]) is None
    assert restarted.list_attempts(demo_subject["id"]) == []
    assert restarted.get_profile(demo_subject["id"]) is None


def test_restored_sample_starts_fresh(tmp_path, demo_subject):
    store = StudyStore(tmp_path / "progress.sqlite3")
    store.ensure_sample_subject(demo_subject)
    store.remove_sample_subject(demo_subject["id"])
    store.restore_sample_subject(demo_subject)

    assert not store.sample_removed()
    assert store.get_subject(demo_subject["id"])["is_demo"] is True
    assert store.list_attempts(demo_subject["id"]) == []


def test_removing_the_sample_keeps_user_subjects(tmp_path, demo_subject):
    store = StudyStore(tmp_path / "progress.sqlite3")
    store.ensure_sample_subject(demo_subject)
    store.create_subject("other", "Other subject", "", 75, {})
    store.remove_sample_subject(demo_subject["id"])
    assert [subject["id"] for subject in store.list_subjects()] == ["other"]


def test_mock_exam_sittings_are_grouped_and_listed_newest_first(tmp_path, demo_subject):
    store = StudyStore(tmp_path / "progress.sqlite3")
    store.seed_demo_subject(demo_subject)
    for sitting, variant, scores in (("s1", 1, (1, 0)), ("s2", 2, (1, 1))):
        for question, score in zip(("sys-1", "sys-2"), scores):
            store.save_attempt(
                demo_subject["id"],
                "mock_exam",
                {"topic_id": "systems-thinking", "question_id": question, "score": score, "max_score": 1},
                sitting=sitting,
                exam_set="variant",
                exam_variant=variant,
            )
    store.save_attempt(demo_subject["id"], "practice", {"topic_id": "systems-thinking", "question_id": "sys-1", "score": 1, "max_score": 1})
    sittings = store.list_sittings(demo_subject["id"])
    assert [(row["sitting"], row["exam_variant"], row["score"], row["max_score"], row["questions"]) for row in sittings] == [
        ("s2", 2, 2, 2, 2),
        ("s1", 1, 1, 2, 2),
    ]
    assert sittings[0]["exam_set"] == "variant"


def test_existing_databases_gain_the_sitting_columns(tmp_path):
    path = tmp_path / "old.sqlite3"
    connection = sqlite3.connect(path)
    connection.executescript(
        """
        CREATE TABLE subjects (id TEXT PRIMARY KEY, name TEXT NOT NULL, description TEXT NOT NULL DEFAULT '',
            exam_date TEXT, target_score INTEGER NOT NULL DEFAULT 80, materials_json TEXT NOT NULL,
            is_demo INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL);
        CREATE TABLE attempts (id INTEGER PRIMARY KEY AUTOINCREMENT, subject_id TEXT NOT NULL, mode TEXT NOT NULL,
            topic_id TEXT, question_id TEXT, score INTEGER NOT NULL, max_score INTEGER NOT NULL,
            confidence INTEGER, created_at TEXT NOT NULL);
        """
    )
    connection.commit()
    connection.close()
    store = StudyStore(path)
    assert store.list_sittings("anything") == []
