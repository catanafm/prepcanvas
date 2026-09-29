import json
import zipfile
import io

import pytest

from prepcanvas.packages import SubjectFiles
from prepcanvas.storage import StudyStore
from prepcanvas.transfer import ArchiveError, SubjectExists, export_subject, import_subject, inspect_archive


def populated(tmp_path, demo_subject):
    store = StudyStore(tmp_path / "a" / "progress.sqlite3")
    files = SubjectFiles(tmp_path / "a" / "private")
    store.create_subject("statistics-101", "Statistics 101", "2026-12-01", 75, {})
    store.set_status("statistics-101", "completed")
    store.save_profile("statistics-101", {"id": "coach_and_recall", "name": "Coach + active recall", "description": "Recall first."}, 0.6, 3)
    store.save_attempt("statistics-101", "practice", {"topic_id": "systems-thinking", "question_id": "sys-1", "score": 1, "max_score": 1})
    store.save_attempt(
        "statistics-101", "mock_exam", {"topic_id": "systems-thinking", "question_id": "sys-3", "score": 1, "max_score": 2},
        sitting="s1", exam_set="variant", exam_variant=2,
    )
    files.write_brief(store.get_subject("statistics-101"))
    files.save_material("statistics-101", "workbook.md", b"# Workbook")
    files.save_package("statistics-101", json.dumps({**demo_subject, "id": "statistics-101"}).encode("utf-8"))
    return store, files


def test_export_and_import_round_trip(tmp_path, demo_subject):
    store, files = populated(tmp_path, demo_subject)
    data = export_subject(store, files, "statistics-101")
    summary = inspect_archive(data)
    assert summary == {**summary, "id": "statistics-101", "name": "Statistics 101", "attempts": 2, "has_package": True, "materials": 1}

    other_store = StudyStore(tmp_path / "b" / "progress.sqlite3")
    other_files = SubjectFiles(tmp_path / "b" / "private")
    assert import_subject(other_store, other_files, data) == "statistics-101"

    original = store.get_subject("statistics-101")
    restored = other_store.get_subject("statistics-101")
    assert restored == original
    assert other_store.get_profile("statistics-101")["strategy_name"] == "Coach + active recall"
    strip = lambda rows: [{k: v for k, v in row.items() if k != "id"} for row in rows]
    assert strip(other_store.list_attempts("statistics-101")) == strip(store.list_attempts("statistics-101"))
    assert other_store.list_sittings("statistics-101")[0]["exam_variant"] == 2
    assert other_files.list_materials("statistics-101") == [{"name": "workbook.md", "bytes": 10}]
    assert other_files.load_package("statistics-101")["state"] == "valid"
    assert other_files.read_brief("statistics-101")["name"] == "Statistics 101"


def test_import_refuses_to_overwrite_unless_asked(tmp_path, demo_subject):
    store, files = populated(tmp_path, demo_subject)
    data = export_subject(store, files, "statistics-101")
    with pytest.raises(SubjectExists):
        import_subject(store, files, data)
    store.save_attempt("statistics-101", "practice", {"topic_id": "systems-thinking", "question_id": "sys-2", "score": 0, "max_score": 1})
    assert len(store.list_attempts("statistics-101")) == 3
    import_subject(store, files, data, replace=True)
    assert len(store.list_attempts("statistics-101")) == 2


def test_broken_archives_are_rejected(tmp_path):
    with pytest.raises(ArchiveError, match="not a PrepCanvas subject archive"):
        inspect_archive(b"not a zip")
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("subject.json", json.dumps({"format": 99, "subject": {"id": "x"}}))
    with pytest.raises(ArchiveError, match="incompatible"):
        inspect_archive(buffer.getvalue())


def make_archive(subject_id="synthetic", entries=None, **payload):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("subject.json", json.dumps({"format": 1, "subject": {"id": subject_id, "name": "Synthetic"}, **payload}))
        for name, value in (entries or {}).items():
            archive.writestr(name, value)
    return buffer.getvalue()


@pytest.mark.parametrize("subject_id", ["../../escaped", "/tmp/escaped", "a/b", "a\\b", "x\n", "sustainable-business-demo", 1, []])
def test_import_rejects_unsafe_subject_ids_without_mutation(tmp_path, subject_id):
    store = StudyStore(tmp_path / "db.sqlite3")
    files = SubjectFiles(tmp_path / "private")
    with pytest.raises(ArchiveError):
        import_subject(store, files, make_archive(subject_id, {"brief.json": "{}"}))
    assert store.list_subjects() == []
    assert not files.private_dir.exists()


@pytest.mark.parametrize("entries", [
    {"../brief.json": "{}"}, {"/brief.json": "{}"}, {"materials/../a.md": "x"},
    {"materials/a b.md": "x", "materials/a-b.md": "y"}, {"materials/a.exe": "x"},
])
def test_archive_rejects_unsafe_members(entries):
    with pytest.raises(ArchiveError):
        inspect_archive(make_archive(entries=entries))


def test_archive_limits_are_checked_before_reading_members(monkeypatch):
    from prepcanvas import transfer
    data = make_archive(entries={"materials/a.md": "123456"})
    monkeypatch.setattr(transfer, "MAX_ARCHIVE_MEMBERS", 1)
    with pytest.raises(ArchiveError, match="limit"):
        inspect_archive(data)
    monkeypatch.setattr(transfer, "MAX_ARCHIVE_MEMBERS", 100)
    monkeypatch.setattr(transfer, "MAX_ARCHIVE_BYTES", 3)
    with pytest.raises(ArchiveError, match="limit"):
        inspect_archive(data)


def test_archive_rejects_symlink_member():
    member = zipfile.ZipInfo("materials/a.md")
    member.create_system = 3
    member.external_attr = 0o120777 << 16
    with pytest.raises(ArchiveError, match="link"):
        inspect_archive(make_archive(entries={member: "elsewhere"}))


@pytest.mark.parametrize("payload", [{"subject": []}, {"subject": {"id": "ok"}}, {"attempts": {}}])
def test_malformed_manifest_is_recoverable(payload):
    with pytest.raises(ArchiveError):
        inspect_archive(make_archive(**payload))


def test_import_rejects_existing_subject_symlink(tmp_path):
    store = StudyStore(tmp_path / "db.sqlite3")
    files = SubjectFiles(tmp_path / "private")
    outside = tmp_path / "outside"
    outside.mkdir()
    folder = files.subject_dir("synthetic")
    folder.parent.mkdir(parents=True)
    folder.symlink_to(outside, target_is_directory=True)
    with pytest.raises(ArchiveError, match="links"):
        import_subject(store, files, make_archive(entries={"brief.json": "{}"}))
    assert list(outside.iterdir()) == []
    assert store.list_subjects() == []
