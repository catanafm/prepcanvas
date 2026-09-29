"""Move a subject between computers: one zip with its record, progress, package, brief, and materials."""

import io
import json
import zipfile
import stat
from pathlib import PurePosixPath
from datetime import datetime, timezone

from prepcanvas.packages import BRIEF_FILE, MATERIALS_DIR, PACKAGE_FILE, SubjectFiles, safe_material_name, SLUG, MATERIAL_SUFFIXES, MAX_MATERIAL_BYTES
from prepcanvas.storage import StudyStore


ARCHIVE_FORMAT = 1
MANIFEST = "subject.json"
MAX_ARCHIVE_MEMBERS = 1000
MAX_ARCHIVE_BYTES = 256 * 1024 * 1024
MAX_METADATA_BYTES = 10 * 1024 * 1024
SAMPLE_ID = "sustainable-business-demo"


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
    archive = None
    try:
        if len(data) > MAX_ARCHIVE_BYTES:
            raise ArchiveError("Archive exceeds the 256 MB limit.")
        archive = zipfile.ZipFile(io.BytesIO(data))
        members = archive.infolist()
        if len(members) > MAX_ARCHIVE_MEMBERS or sum(m.file_size for m in members) > MAX_ARCHIVE_BYTES:
            raise ArchiveError("Archive exceeds the file count or expanded size limit.")
        targets = set()
        for member in members:
            name = member.filename
            parts = PurePosixPath(name).parts
            mode = member.external_attr >> 16
            if stat.S_ISLNK(mode) or member.flag_bits & 1 or "\\" in name:
                raise ArchiveError("Archive contains a link, encrypted file, or unsafe path.")
            if name in (MANIFEST, PACKAGE_FILE, BRIEF_FILE):
                target = name
                limit = MAX_METADATA_BYTES
            elif name == MATERIALS_DIR + "/" and member.is_dir():
                continue
            elif len(parts) == 2 and parts[0] == MATERIALS_DIR and not member.is_dir():
                clean = safe_material_name(parts[1])
                if parts[1] in (".", "..") or PurePosixPath(clean).suffix not in MATERIAL_SUFFIXES:
                    raise ArchiveError("Archive contains an unsupported material.")
                target = MATERIALS_DIR + "/" + clean
                limit = MAX_MATERIAL_BYTES
            else:
                raise ArchiveError("Archive contains an unexpected or unsafe path.")
            if target.casefold() in targets or member.file_size > limit:
                raise ArchiveError("Archive contains duplicate filenames or an oversized file.")
            targets.add(target.casefold())
        manifest = json.loads(archive.read(MANIFEST).decode("utf-8"))
        if not isinstance(manifest, dict) or manifest.get("format") != ARCHIVE_FORMAT:
            raise ArchiveError("This archive was made by an incompatible PrepCanvas version.")
        subject = manifest.get("subject")
        if not isinstance(subject, dict) or not isinstance(subject.get("id"), str) or not SLUG.fullmatch(subject["id"]):
            raise ArchiveError("Archive subject id must be a lowercase slug.")
        if subject["id"] == SAMPLE_ID:
            raise ArchiveError("The sample subject id is reserved; add the sample from the library.")
        if not isinstance(subject.get("name"), str) or not subject["name"].strip():
            raise ArchiveError("Archive subject needs a name.")
        if not isinstance(manifest.get("attempts", []), list):
            raise ArchiveError("Archive attempts must be a list.")
        return archive
    except Exception as error:
        if archive is not None:
            archive.close()
        if isinstance(error, ArchiveError):
            raise
        if isinstance(error, (zipfile.BadZipFile, KeyError, UnicodeDecodeError, ValueError, RuntimeError, NotImplementedError)):
            raise ArchiveError("This file is not a PrepCanvas subject archive.") from error
        raise


def inspect_archive(data: bytes) -> dict:
    """What an archive contains, for a confirmation before importing."""
    archive = _open(data)
    manifest = json.loads(archive.read(MANIFEST).decode("utf-8"))
    names = archive.namelist()
    archive.close()
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
    try:
        files.subject_dir(subject_id)
        files.materials_dir(subject_id)
        files.package_path(subject_id)
        files.brief_path(subject_id)
    except ValueError as error:
        archive.close()
        raise ArchiveError(str(error)) from error
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
    archive.close()
    return subject_id
