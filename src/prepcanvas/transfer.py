"""Move a subject between computers: one zip with its record, progress, package, brief, and materials."""

import io
import json
import zipfile
import stat
import shutil
import sqlite3
import tempfile
from pathlib import Path
from pathlib import PurePosixPath
from datetime import datetime, timezone

from prepcanvas.packages import BRIEF_FILE, MATERIALS_DIR, PACKAGE_FILE, SubjectFiles, safe_material_name, SLUG, MATERIAL_SUFFIXES, MAX_MATERIAL_BYTES
from prepcanvas.storage import StudyStore
from prepcanvas.archive_payload import validate_payload


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


def _stage(archive, manifest, staged):
    subject_id = manifest["subject"]["id"]
    validate_payload(manifest)
    folder = staged.subject_dir(subject_id)
    folder.mkdir(parents=True)
    for name in archive.namelist():
        if name.startswith(MATERIALS_DIR + "/") and not name.endswith("/"):
            staged.save_material(subject_id, name.split("/", 1)[1], archive.read(name))
    if BRIEF_FILE in archive.namelist():
        raw = archive.read(BRIEF_FILE)
        brief = json.loads(raw.decode("utf-8"))
        if not isinstance(brief, dict) or brief.get("id") != subject_id or not isinstance(brief.get("name"), str):
            raise ValueError("The brief must describe the imported subject.")
        validate_payload({"subject": brief})
        staged.brief_path(subject_id).write_bytes(raw)
    if PACKAGE_FILE in archive.namelist():
        staged.save_package(subject_id, archive.read(PACKAGE_FILE))
    return folder


def import_subject(store: StudyStore, files: SubjectFiles, data: bytes, replace: bool = False) -> str:
    """Stage and validate everything, then promote files inside one DB transaction.

    On any promotion/commit failure the old folder is restored and SQLite rolls
    back. If filesystem recovery itself fails, the backup is retained for recovery.
    """
    work = None
    preserve_backup = False
    try:
        with _open(data) as archive:
            manifest = json.loads(archive.read(MANIFEST).decode("utf-8"))
            subject_id = manifest["subject"]["id"]
            folder = files.subject_dir(subject_id)
            files.materials_dir(subject_id)
            files.package_path(subject_id)
            files.brief_path(subject_id)
            if store.get_subject(subject_id) and not replace:
                raise SubjectExists(subject_id)
            # Existing orphaned materials are also protected from implicit replacement.
            if folder.exists() and not replace:
                raise SubjectExists(subject_id)
            files.private_dir.mkdir(parents=True, exist_ok=True)
            work = Path(tempfile.mkdtemp(prefix=".subject-import-", dir=files.private_dir))
            staged = SubjectFiles(work / "candidate")
            candidate = _stage(archive, manifest, staged)
            backup = work / "previous"
            moved_old = promoted = False
            try:
                with store.import_transaction(manifest, replace=replace):
                    folder.parent.mkdir(parents=True, exist_ok=True)
                    if folder.exists():
                        folder.rename(backup)
                        moved_old = True
                    candidate.rename(folder)
                    promoted = True
            except BaseException:
                try:
                    if promoted:
                        folder.rename(candidate)
                    if moved_old:
                        backup.rename(folder)
                except OSError as recovery_error:
                    preserve_backup = True
                    raise ArchiveError(f"Import failed. Recovery files are preserved in {work}; restore them before retrying.") from recovery_error
                raise
        return subject_id
    except SubjectExists:
        raise
    except (ValueError, OSError, sqlite3.Error, zipfile.BadZipFile, KeyError, RuntimeError, NotImplementedError) as error:
        if isinstance(error, ArchiveError):
            raise
        raise ArchiveError(f"Import failed; previous subject data is unchanged. {error}") from error
    finally:
        if work is not None and not preserve_backup:
            shutil.rmtree(work, ignore_errors=True)
