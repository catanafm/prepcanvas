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
