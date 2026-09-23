import re
from pathlib import Path


TASKS_DIR = Path(__file__).resolve().parents[1] / "tasks"
REQUIRED_FIELDS = {"id", "title", "type", "status", "priority", "area", "created"}
ALLOWED = {
    "type": {"feature", "fix", "refactor", "chore", "docs", "test"},
    "status": {"backlog", "in-progress", "done", "cancelled"},
    "priority": {"high", "medium", "low"},
}
BOARD_ROW = re.compile(
    r"^\| \[(?P<id>TASK-\d{3})\]\((?P<file>[^)]+)\) \| (?P<title>.+?) \| "
    r"(?P<type>\S+) \| (?P<priority>\S+) \| (?P<status>\S+) \|$"
)


def read_front_matter(path: Path) -> dict:
    lines = path.read_text(encoding="utf-8").splitlines()
    assert lines[0] == "---", f"{path.name} must start with front matter"
    end = lines.index("---", 1)
    fields = {}
    for line in lines[1:end]:
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip()
    return fields


def task_files() -> list:
    return sorted(TASKS_DIR.glob("TASK-*.md"))


def board_rows() -> dict:
    text = (TASKS_DIR / "README.md").read_text(encoding="utf-8")
    rows = {}
    for line in text.splitlines():
        match = BOARD_ROW.match(line)
        if match:
            assert match["id"] not in rows, f"{match['id']} is listed twice on the board"
            rows[match["id"]] = match.groupdict()
    return rows


def test_task_files_have_valid_front_matter():
    for path in task_files():
        fields = read_front_matter(path)
        assert REQUIRED_FIELDS <= set(fields), f"{path.name} is missing fields"
        assert path.name.startswith(fields["id"] + "-"), f"{path.name} does not match its id"
        for field, allowed in ALLOWED.items():
            assert fields[field] in allowed, f"{path.name}: invalid {field} '{fields[field]}'"
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", fields["created"])


def test_task_ids_are_unique():
    ids = [read_front_matter(path)["id"] for path in task_files()]
    assert len(ids) == len(set(ids))


def test_board_matches_task_files():
    rows = board_rows()
    files = {read_front_matter(path)["id"]: path for path in task_files()}
    assert set(rows) == set(files), "board and task files list different tasks"
    for task_id, path in files.items():
        fields = read_front_matter(path)
        row = rows[task_id]
        assert row["file"] == path.name
        for key in ("title", "type", "priority", "status"):
            assert row[key] == fields[key], f"{task_id}: board {key} is out of date"


def test_done_tasks_have_all_criteria_checked():
    for path in task_files():
        if read_front_matter(path)["status"] == "done":
            assert "- [ ]" not in path.read_text(encoding="utf-8"), f"{path.name} is done with open criteria"
