import subprocess
from pathlib import Path


FORBIDDEN_SUFFIXES = {".db", ".pdf", ".sqlite", ".sqlite3"}
FORBIDDEN_PREFIXES = (".private_backup/", "artifacts/", "data/private/", "data/uploads/")


def tracked_files(root: Path) -> list:
    output = subprocess.check_output(
        ["git", "ls-files"],
        cwd=root,
        text=True,
    )
    return [root / item for item in output.splitlines() if item]


def test_private_runtime_files_are_not_tracked():
    root = Path(__file__).resolve().parents[1]
    violations = []
    for path in tracked_files(root):
        relative = path.relative_to(root).as_posix()
        if relative.startswith(FORBIDDEN_PREFIXES) or path.suffix.lower() in FORBIDDEN_SUFFIXES:
            violations.append(relative)
    assert violations == []


def test_tracked_text_does_not_contain_absolute_user_paths():
    root = Path(__file__).resolve().parents[1]
    home_markers = ["/" + "Users" + "/", "C:" + "\\" + "Users" + "\\"]
    violations = []
    for path in tracked_files(root):
        if not path.exists():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if any(marker in text for marker in home_markers):
            violations.append(path.relative_to(root).as_posix())
    assert violations == []


def test_gitignore_covers_local_private_state():
    root = Path(__file__).resolve().parents[1]
    entries = set((root / ".gitignore").read_text(encoding="utf-8").splitlines())
    assert {".private_backup/", "data/private/", "data/uploads/", "data/local/", "artifacts/"} <= entries
