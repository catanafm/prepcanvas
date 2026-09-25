"""Move a subject between computers: one zip with its record, progress, package, brief, and materials."""

import io
import json
import zipfile
from datetime import datetime, timezone

from prepcanvas.packages import BRIEF_FILE, MATERIALS_DIR, PACKAGE_FILE, SubjectFiles, safe_material_name
from prepcanvas.storage import StudyStore


ARCHIVE_FORMAT = 1
MANIFEST = "subject.json"


class ArchiveError(ValueError):
    """The file is not a PrepCanvas subject archive."""


class SubjectExists(ValueError):
    """A subject with the archive's id already exists and replacing was not requested."""


def export_subject(store: StudyStore, files: SubjectFiles, subject_id: str) -> bytes:
    payload = store.export_subject(subject_id)
    payload["format"] = ARCHIVE_FORMAT
    payload["exported_at"] = datetime.now(timezone.utc).isoformat()
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(MANIFEST, json.dumps(payload, indent=2))
        for name in (PACKAGE_FILE, BRIEF_FILE):
            path = files.subject_dir(subject_id) / name
            if path.is_file():
                archive.write(path, name)
        for material in files.list_materials(subject_id):
            archive.write(files.materials_dir(subject_id) / material["name"], f'{MATERIALS_DIR}/{material["name"]}')
    return buffer.getvalue()


def _open(data: bytes) -> zipfile.ZipFile:
    try:
        archive = zipfile.ZipFile(io.BytesIO(data))
        manifest = json.loads(archive.read(MANIFEST).decode("utf-8"))
    except (zipfile.BadZipFile, KeyError, UnicodeDecodeError, json.JSONDecodeError):
        raise ArchiveError("This file is not a PrepCanvas subject archive.")
    if manifest.get("format") != ARCHIVE_FORMAT or not isinstance(manifest.get("subject"), dict) or not manifest["subject"].get("id"):
        raise ArchiveError("This archive was made by an incompatible PrepCanvas version.")
    return archive


def inspect_archive(data: bytes) -> dict:
    """What an archive contains, for a confirmation before importing."""
    archive = _open(data)
    manifest = json.loads(archive.read(MANIFEST).decode("utf-8"))
    names = archive.namelist()
    return {
        "id": manifest["subject"]["id"],
        "name": manifest["subject"]["name"],
        "attempts": len(manifest.get("attempts", [])),
        "has_package": PACKAGE_FILE in names,
        "materials": sum(1 for name in names if name.startswith(f"{MATERIALS_DIR}/") and not name.endswith("/")),
        "exported_at": manifest.get("exported_at"),
    }


def import_subject(store: StudyStore, files: SubjectFiles, data: bytes, replace: bool = False) -> str:
    """Restore a subject from an archive; returns its id."""
    archive = _open(data)
    manifest = json.loads(archive.read(MANIFEST).decode("utf-8"))
    subject_id = manifest["subject"]["id"]
    if store.get_subject(subject_id):
        if not replace:
            raise SubjectExists(subject_id)
        store.delete_subject(subject_id)
        files.delete_subject(subject_id)
    store.import_subject(manifest)
    folder = files.subject_dir(subject_id)
    folder.mkdir(parents=True, exist_ok=True)
    for name in (PACKAGE_FILE, BRIEF_FILE):
        if name in archive.namelist():
            (folder / name).write_bytes(archive.read(name))
    for name in archive.namelist():
        if name.startswith(f"{MATERIALS_DIR}/") and not name.endswith("/"):
            files.save_material(subject_id, safe_material_name(name.split("/", 1)[1]), archive.read(name))
    return subject_id
