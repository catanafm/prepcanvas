"""Subject packages: the study content of a subject as one validated JSON file.

The bundled sample subject and every user subject share this format. A package
is produced outside the app, by the learner's own AI agent or by hand, and the
app only loads it after validation. See docs/subject-package.md for the schema.
"""

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from prepcanvas.grading import grade_question


SCHEMA_VERSION = 1
QUESTION_TYPES = ("multiple_choice", "short_answer")
QUESTION_ORIGINS = ("source", "generated")
SOURCE_ROLES = ("workbook", "practice_exam", "answer_key", "notes", "transcript", "other")
# Full topic evidence in the readiness heuristic needs this many distinct questions.
RECOMMENDED_QUESTIONS_PER_TOPIC = 3
MATERIAL_SUFFIXES = (".pdf", ".txt", ".md", ".markdown", ".docx")
MAX_MATERIAL_BYTES = 25 * 1024 * 1024
PACKAGE_FILE = "package.json"
BRIEF_FILE = "brief.json"
MATERIALS_DIR = "materials"

SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class PackageError(ValueError):
    """Raised when a package cannot be read or fails validation."""

    def __init__(self, issues: list):
        self.issues = issues
        super().__init__("; ".join(issue["message"] for issue in issues if issue["level"] == "error"))


def _issue(level: str, path: str, message: str) -> dict:
    return {"level": level, "path": path, "message": message}


def _text(value) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _text_list(value) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) for item in value)


def _positive_int(value) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def _check_fields(item: dict, path: str, required: dict, issues: list) -> bool:
    """Append one issue per missing or malformed field; return True when all pass."""
    ok = True
    for field, (check, expectation) in required.items():
        if field not in item:
            issues.append(_issue("error", f"{path}.{field}", f"Missing required field '{field}'."))
            ok = False
        elif not check(item[field]):
            issues.append(_issue("error", f"{path}.{field}", f"'{field}' must be {expectation}."))
            ok = False
    return ok


def _validate_topic(topic, path: str, issues: list) -> Optional[str]:
    if not isinstance(topic, dict):
        issues.append(_issue("error", path, "Each topic must be an object."))
        return None
    _check_fields(
        topic,
        path,
        {
            "id": (lambda v: _text(v) and bool(SLUG.match(v)), "a lowercase slug such as 'systems-thinking'"),
            "title": (_text, "a non-empty string"),
            "summary": (_text, "a non-empty string"),
            "key_concepts": (lambda v: _text_list(v) and len(v) > 0, "a non-empty list of strings"),
            "worked_example": (_text, "a non-empty string"),
            "common_mistake": (_text, "a non-empty string"),
            "coach_question": (_text, "a non-empty string"),
            "source": (_text, "a non-empty source label"),
        },
        issues,
    )
    return topic.get("id") if _text(topic.get("id")) else None


def _validate_rubric(question: dict, path: str, issues: list) -> bool:
    points = question.get("rubric_points")
    if not isinstance(points, list) or not points:
        issues.append(_issue("error", f"{path}.rubric_points", "Short-answer questions need a non-empty 'rubric_points' list."))
        return False
    ok = True
    total = 0
    for index, point in enumerate(points):
        point_path = f"{path}.rubric_points[{index}]"
        if not isinstance(point, dict):
            issues.append(_issue("error", point_path, "Each rubric point must be an object."))
            ok = False
            continue
        ok &= _check_fields(
            point,
            point_path,
            {"label": (_text, "a non-empty string"), "points": (_positive_int, "a positive integer")},
            issues,
        )
        for field in ("accepted_phrases", "keywords", "required_keywords"):
            if field in point and not _text_list(point[field]):
                issues.append(_issue("error", f"{point_path}.{field}", f"'{field}' must be a list of strings."))
                ok = False
        if not point.get("accepted_phrases") and not point.get("keywords"):
            issues.append(_issue("error", point_path, "A rubric point needs 'accepted_phrases' or 'keywords' so it can be matched."))
            ok = False
        minimum = point.get("minimum_keyword_matches")
        if minimum is not None and not _positive_int(minimum):
            issues.append(_issue("error", f"{point_path}.minimum_keyword_matches", "'minimum_keyword_matches' must be a positive integer."))
            ok = False
        if _positive_int(point.get("points")):
            total += point["points"]
    if ok and _positive_int(question.get("points")):
        if total < question["points"]:
            issues.append(_issue("error", f"{path}.rubric_points", f"Rubric points add up to {total} but the question is worth {question['points']}; full marks are unreachable."))
            ok = False
        elif total > question["points"]:
            issues.append(_issue("warning", f"{path}.rubric_points", f"Rubric points add up to {total} for a {question['points']}-point question; the score is capped."))
    return ok


def _validate_question(question, path: str, topic_ids: set, issues: list) -> Optional[dict]:
    if not isinstance(question, dict):
        issues.append(_issue("error", path, "Each question must be an object."))
        return None
    ok = _check_fields(
        question,
        path,
        {
            "id": (lambda v: _text(v) and bool(SLUG.match(v)), "a lowercase slug such as 'sys-1'"),
            "topic_id": (_text, "a topic id"),
            "type": (lambda v: v in QUESTION_TYPES, "one of " + ", ".join(QUESTION_TYPES)),
            "points": (_positive_int, "a positive integer"),
            "prompt": (_text, "a non-empty string"),
            "explanation": (_text, "a non-empty string"),
            "source": (_text, "a non-empty source label"),
            "origin": (lambda v: v in QUESTION_ORIGINS, "'source' (taken from the materials) or 'generated' (a new similar question)"),
        },
        issues,
    )
    if _text(question.get("topic_id")) and question["topic_id"] not in topic_ids:
        issues.append(_issue("error", f"{path}.topic_id", f"Unknown topic '{question['topic_id']}'."))
        ok = False
    if question.get("type") == "multiple_choice":
        options = question.get("options")
        if not _text_list(options) or len(options) < 2 or len(set(options)) != len(options):
            issues.append(_issue("error", f"{path}.options", "Multiple-choice questions need at least two distinct string options."))
            ok = False
        elif question.get("correct_answer") not in options:
            issues.append(_issue("error", f"{path}.correct_answer", "'correct_answer' must be exactly one of the options."))
            ok = False
    elif question.get("type") == "short_answer":
        if not _text(question.get("model_answer")):
            issues.append(_issue("error", f"{path}.model_answer", "Short-answer questions need a 'model_answer'."))
            ok = False
        ok &= _validate_rubric(question, path, issues)
        if ok:
            result = grade_question(question, question["model_answer"])
            if result["score"] < result["max_score"]:
                missing = "; ".join(result["missing_points"])
                issues.append(
                    _issue(
                        "error",
                        f"{path}.rubric_points",
                        f"The model answer scores {result['score']}/{result['max_score']} against its own rubric. "
                        f"Unmatched: {missing}. Rewrite the accepted phrases or keywords so the model answer earns full marks.",
                    )
                )
                ok = False
    return question if ok else None


def _validate_blueprint(data: dict, issues: list):
    """An optional exam blueprint must be well-formed and fillable from the question pool."""
    plan = data.get("exam_blueprint")
    if plan is None:
        return
    if not isinstance(plan, dict) or not isinstance(plan.get("sections"), list) or not plan["sections"]:
        issues.append(_issue("error", "$.exam_blueprint", "'exam_blueprint' must be an object with a non-empty 'sections' list."))
        return
    if "title" in plan and not _text(plan["title"]):
        issues.append(_issue("error", "$.exam_blueprint.title", "'title' must be a non-empty string."))
    questions = [q for q in data.get("questions") or [] if isinstance(q, dict)]
    for index, section in enumerate(plan["sections"]):
        path = f"$.exam_blueprint.sections[{index}]"
        if not isinstance(section, dict):
            issues.append(_issue("error", path, "Each section must be an object."))
            continue
        ok = _check_fields(
            section,
            path,
            {
                "type": (lambda v: v in QUESTION_TYPES, "one of " + ", ".join(QUESTION_TYPES)),
                "count": (_positive_int, "a positive integer"),
                "points": (_positive_int, "a positive integer"),
            },
            issues,
        )
        if not ok:
            continue
        available = sum(1 for q in questions if q.get("type") == section["type"] and q.get("points") == section["points"])
        if available < section["count"]:
            issues.append(
                _issue(
                    "error",
                    path,
                    f"The blueprint needs {section['count']} {section['type']} question(s) worth {section['points']} point(s) "
                    f"but the pool has {available}; add questions with exactly these points.",
                )
            )


def validate_package(data, expected_id: Optional[str] = None, base_dir: Optional[Path] = None) -> list:
    """Return a list of issues; the package is usable when none has level 'error'.

    `base_dir` is the folder holding the package; when given, source files are checked to exist.
    """
    issues = []
    if not isinstance(data, dict):
        return [_issue("error", "$", "The package must be a JSON object.")]
    if data.get("schema_version") != SCHEMA_VERSION:
        issues.append(_issue("error", "$.schema_version", f"'schema_version' must be {SCHEMA_VERSION}."))
    _check_fields(
        data,
        "$",
        {
            "id": (lambda v: _text(v) and bool(SLUG.match(v)), "a lowercase slug"),
            "name": (_text, "a non-empty string"),
            "topics": (lambda v: isinstance(v, list) and len(v) > 0, "a non-empty list"),
            "questions": (lambda v: isinstance(v, list) and len(v) > 0, "a non-empty list"),
        },
        issues,
    )
    if expected_id and _text(data.get("id")) and data["id"] != expected_id:
        issues.append(_issue("error", "$.id", f"The package id is '{data['id']}' but this subject is '{expected_id}'."))
    if "description" in data and not isinstance(data["description"], str):
        issues.append(_issue("error", "$.description", "'description' must be a string."))
    if "target_score" in data and not (isinstance(data["target_score"], int) and 1 <= data["target_score"] <= 100):
        issues.append(_issue("error", "$.target_score", "'target_score' must be an integer from 1 to 100."))
    if "materials" in data and not (isinstance(data["materials"], dict) and all(isinstance(v, bool) for v in data["materials"].values())):
        issues.append(_issue("error", "$.materials", "'materials' must map material names to true/false."))
    sources = data.get("sources", [])
    if not isinstance(sources, list):
        issues.append(_issue("error", "$.sources", "'sources' must be a list."))
    else:
        for index, source in enumerate(sources):
            source_path = f"$.sources[{index}]"
            if not isinstance(source, dict):
                issues.append(_issue("error", source_path, "Each source must be an object."))
                continue
            _check_fields(
                source,
                source_path,
                {
                    "id": (_text, "a non-empty string"),
                    "role": (lambda v: v in SOURCE_ROLES, "one of " + ", ".join(SOURCE_ROLES)),
                    "title": (_text, "a non-empty string"),
                },
                issues,
            )
            file = source.get("file")
            if file is not None and not _text(file):
                issues.append(_issue("error", f"{source_path}.file", "'file' must be a non-empty relative path."))
            elif file and base_dir is not None and not (Path(base_dir) / file).is_file():
                issues.append(_issue("warning", f"{source_path}.file", f"Source file '{file}' was not found next to the package; list only the files the content was built from."))

    _validate_blueprint(data, issues)

    topic_ids = []
    for index, topic in enumerate(data.get("topics") or []):
        topic_id = _validate_topic(topic, f"$.topics[{index}]", issues)
        if topic_id in topic_ids:
            issues.append(_issue("error", f"$.topics[{index}].id", f"Duplicate topic id '{topic_id}'."))
        elif topic_id:
            topic_ids.append(topic_id)

    question_ids = set()
    per_topic = {topic_id: {"total": 0, "multiple_choice": 0} for topic_id in topic_ids}
    for index, question in enumerate(data.get("questions") or []):
        _validate_question(question, f"$.questions[{index}]", set(topic_ids), issues)
        if not isinstance(question, dict):
            continue
        if _text(question.get("id")):
            if question["id"] in question_ids:
                issues.append(_issue("error", f"$.questions[{index}].id", f"Duplicate question id '{question['id']}'."))
            question_ids.add(question["id"])
        # Coverage counts every question that names a topic, so one broken
        # question does not also report its topic as empty.
        if question.get("topic_id") in per_topic:
            counts = per_topic[question["topic_id"]]
            counts["total"] += 1
            counts["multiple_choice"] += question.get("type") == "multiple_choice"

    for topic_id, counts in per_topic.items():
        if not counts["total"]:
            issues.append(_issue("error", f"$.topics[{topic_id}]", f"Topic '{topic_id}' has no questions, so it could never show progress."))
            continue
        if not counts["multiple_choice"]:
            issues.append(_issue("warning", f"$.topics[{topic_id}]", f"Topic '{topic_id}' has no multiple-choice question and is skipped by the diagnostic."))
        if counts["total"] < RECOMMENDED_QUESTIONS_PER_TOPIC:
            issues.append(
                _issue(
                    "warning",
                    f"$.topics[{topic_id}]",
                    f"Topic '{topic_id}' has {counts['total']} question(s); readiness needs {RECOMMENDED_QUESTIONS_PER_TOPIC} distinct questions for full evidence.",
                )
            )
    return issues


def has_errors(issues: list) -> bool:
    return any(issue["level"] == "error" for issue in issues)


def read_package(path: Path, expected_id: Optional[str] = None) -> dict:
    """Load and validate a package file; raise PackageError with every issue found."""
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise PackageError([_issue("error", "$", f"No package found at {path}.")])
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise PackageError([_issue("error", "$", f"The package is not valid JSON: {error}")])
    issues = validate_package(data, expected_id, base_dir=Path(path).parent)
    if has_errors(issues):
        raise PackageError(issues)
    data["_warnings"] = issues
    return data


def content_summary(package: dict) -> dict:
    questions = package.get("questions", [])
    return {
        "topics": len(package.get("topics", [])),
        "questions": len(questions),
        "source": sum(1 for q in questions if q.get("origin") == "source"),
        "generated": sum(1 for q in questions if q.get("origin") == "generated"),
    }


def safe_material_name(name: str) -> str:
    """Reduce an uploaded file name to a plain, single-segment name."""
    base = Path(name or "").name
    stem = re.sub(r"[^A-Za-z0-9._-]+", "-", Path(base).stem).strip("-.") or "material"
    return f"{stem}{Path(base).suffix.lower()}"


class SubjectFiles:
    """Per-subject private folder: materials, the brief for an agent, and the package."""

    def __init__(self, private_dir: Path):
        self.private_dir = Path(private_dir)

    def subject_dir(self, subject_id: str) -> Path:
        return self.private_dir / "subjects" / subject_id

    def materials_dir(self, subject_id: str) -> Path:
        return self.subject_dir(subject_id) / MATERIALS_DIR

    def package_path(self, subject_id: str) -> Path:
        return self.subject_dir(subject_id) / PACKAGE_FILE

    def brief_path(self, subject_id: str) -> Path:
        return self.subject_dir(subject_id) / BRIEF_FILE

    def list_materials(self, subject_id: str) -> list:
        folder = self.materials_dir(subject_id)
        if not folder.is_dir():
            return []
        return sorted(
            ({"name": item.name, "bytes": item.stat().st_size} for item in folder.iterdir() if item.is_file() and not item.name.startswith(".")),
            key=lambda item: item["name"].casefold(),
        )

    def save_material(self, subject_id: str, name: str, content: bytes) -> Path:
        clean = safe_material_name(name)
        if Path(clean).suffix not in MATERIAL_SUFFIXES:
            raise ValueError(f"Unsupported file type '{Path(clean).suffix or 'none'}'. Use {', '.join(MATERIAL_SUFFIXES)}.")
        if len(content) > MAX_MATERIAL_BYTES:
            raise ValueError(f"'{clean}' is larger than {MAX_MATERIAL_BYTES // (1024 * 1024)} MB.")
        folder = self.materials_dir(subject_id)
        folder.mkdir(parents=True, exist_ok=True)
        target = folder / clean
        target.write_bytes(content)
        return target

    def remove_material(self, subject_id: str, name: str):
        target = self.materials_dir(subject_id) / safe_material_name(name)
        if target.is_file():
            target.unlink()

    def write_brief(self, subject: dict) -> Path:
        """Record what an agent needs to know about the subject next to its materials."""
        folder = self.subject_dir(subject["id"])
        folder.mkdir(parents=True, exist_ok=True)
        brief = {
            "id": subject["id"],
            "name": subject["name"],
            "exam_date": subject.get("exam_date"),
            "target_score": subject.get("target_score", 80),
            "materials_dir": MATERIALS_DIR,
            "package_file": PACKAGE_FILE,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        path = self.brief_path(subject["id"])
        path.write_text(json.dumps(brief, indent=2) + "\n", encoding="utf-8")
        return path

    def read_brief(self, subject_id: str) -> Optional[dict]:
        path = self.brief_path(subject_id)
        if not path.is_file():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None

    def save_package(self, subject_id: str, content: bytes) -> Path:
        folder = self.subject_dir(subject_id)
        folder.mkdir(parents=True, exist_ok=True)
        path = self.package_path(subject_id)
        path.write_bytes(content)
        return path

    def load_package(self, subject_id: str) -> dict:
        """Describe the package state: missing, invalid (with issues), or valid (with content)."""
        path = self.package_path(subject_id)
        if not path.is_file():
            return {"state": "missing", "package": None, "issues": [], "path": path}
        try:
            package = read_package(path, expected_id=subject_id)
        except PackageError as error:
            return {"state": "invalid", "package": None, "issues": error.issues, "path": path}
        return {"state": "valid", "package": package, "issues": package.pop("_warnings"), "path": path}

    def delete_subject(self, subject_id: str):
        """Remove the subject folder with its materials and package."""
        folder = self.subject_dir(subject_id)
        if not folder.is_dir():
            return
        for item in sorted(folder.rglob("*"), reverse=True):
            if item.is_file() or item.is_symlink():
                item.unlink()
            else:
                item.rmdir()
        folder.rmdir()
