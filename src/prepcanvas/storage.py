import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path


SUBJECT_STATUSES = ("active", "completed")


class StudyStore:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    @contextmanager
    def _connect(self):
        """Open a connection, commit on success, and always close it."""
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def _initialize(self):
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS subjects (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL DEFAULT '',
                    exam_date TEXT,
                    target_score INTEGER NOT NULL DEFAULT 80,
                    materials_json TEXT NOT NULL,
                    is_demo INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS attempts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    subject_id TEXT NOT NULL,
                    mode TEXT NOT NULL,
                    topic_id TEXT,
                    question_id TEXT,
                    score INTEGER NOT NULL,
                    max_score INTEGER NOT NULL,
                    is_answered INTEGER NOT NULL DEFAULT 1,
                    confidence INTEGER,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(subject_id) REFERENCES subjects(id)
                );

                CREATE TABLE IF NOT EXISTS app_settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS coaching_profiles (
                    subject_id TEXT PRIMARY KEY,
                    strategy_id TEXT NOT NULL,
                    strategy_name TEXT NOT NULL,
                    description TEXT NOT NULL,
                    diagnostic_score REAL NOT NULL,
                    confidence INTEGER NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY(subject_id) REFERENCES subjects(id)
                );
                """
            )
            columns = {
                row[1]
                for row in connection.execute("PRAGMA table_info(attempts)").fetchall()
            }
            if "is_answered" not in columns:
                connection.execute(
                    "ALTER TABLE attempts ADD COLUMN is_answered INTEGER NOT NULL DEFAULT 1"
                )
            for column, definition in (
                ("sitting", "TEXT"),
                ("exam_set", "TEXT"),
                ("exam_variant", "INTEGER"),
                ("time_limit_seconds", "INTEGER"),
                ("time_used_seconds", "INTEGER"),
            ):
                if column not in columns:
                    connection.execute(f"ALTER TABLE attempts ADD COLUMN {column} {definition}")
            subject_columns = {
                row[1]
                for row in connection.execute("PRAGMA table_info(subjects)").fetchall()
            }
            if "status" not in subject_columns:
                connection.execute(
                    "ALTER TABLE subjects ADD COLUMN status TEXT NOT NULL DEFAULT 'active'"
                )

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def _get_setting(self, key: str, default: str = "") -> str:
        with self._connect() as connection:
            row = connection.execute("SELECT value FROM app_settings WHERE key = ?", (key,)).fetchone()
        return row["value"] if row else default

    def _set_setting(self, key: str, value: str):
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO app_settings (key, value) VALUES (?, ?) "
                "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                (key, value),
            )

    def sample_removed(self) -> bool:
        return self._get_setting("sample_removed") == "1"

    def ensure_sample_subject(self, subject: dict):
        """Seed or refresh the sample subject unless the learner removed it."""
        if not self.sample_removed():
            self.seed_demo_subject(subject)

    def remove_sample_subject(self, subject_id: str):
        """Remove the sample subject and its progress, and keep it removed across restarts."""
        with self._connect() as connection:
            connection.execute("DELETE FROM attempts WHERE subject_id = ?", (subject_id,))
            connection.execute("DELETE FROM coaching_profiles WHERE subject_id = ?", (subject_id,))
            connection.execute("DELETE FROM subjects WHERE id = ? AND is_demo = 1", (subject_id,))
        self._set_setting("sample_removed", "1")

    def restore_sample_subject(self, subject: dict):
        self._set_setting("sample_removed", "0")
        self.seed_demo_subject(subject)

    def seed_demo_subject(self, subject: dict):
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO subjects (
                    id, name, description, exam_date, target_score,
                    materials_json, is_demo, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, 1, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name = excluded.name,
                    description = excluded.description,
                    target_score = excluded.target_score,
                    materials_json = excluded.materials_json,
                    is_demo = 1
                """,
                (
                    subject["id"],
                    subject["name"],
                    subject["description"],
                    subject.get("exam_date"),
                    subject.get("target_score", 80),
                    json.dumps(subject.get("materials", {})),
                    self._now(),
                ),
            )

    def create_subject(self, subject_id: str, name: str, exam_date: str, target_score: int, materials: dict):
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO subjects (
                    id, name, description, exam_date, target_score,
                    materials_json, is_demo, created_at
                ) VALUES (?, ?, '', ?, ?, ?, 0, ?)
                """,
                (subject_id, name, exam_date or None, target_score, json.dumps(materials), self._now()),
            )

    def list_subjects(self) -> list:
        with self._connect() as connection:
            rows = connection.execute("SELECT * FROM subjects ORDER BY is_demo DESC, created_at").fetchall()
        return [self._subject_from_row(row) for row in rows]

    def get_subject(self, subject_id: str):
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM subjects WHERE id = ?", (subject_id,)).fetchone()
        return self._subject_from_row(row) if row else None

    @staticmethod
    def _subject_from_row(row):
        item = dict(row)
        item["materials"] = json.loads(item.pop("materials_json"))
        item["is_demo"] = bool(item["is_demo"])
        return item

    def set_status(self, subject_id: str, status: str):
        """Mark a subject as `active` (in progress) or `completed`."""
        if status not in SUBJECT_STATUSES:
            raise ValueError(f"Unknown subject status '{status}'")
        with self._connect() as connection:
            updated = connection.execute(
                "UPDATE subjects SET status = ? WHERE id = ?", (status, subject_id)
            ).rowcount
        if not updated:
            raise KeyError(f"Unknown subject '{subject_id}'")

    def reset_progress(self, subject_id: str):
        """Remove every saved answer and the coaching profile for a subject."""
        with self._connect() as connection:
            connection.execute("DELETE FROM attempts WHERE subject_id = ?", (subject_id,))
            connection.execute("DELETE FROM coaching_profiles WHERE subject_id = ?", (subject_id,))

    def delete_subject(self, subject_id: str):
        """Delete a user subject together with its progress. The demo subject is protected."""
        subject = self.get_subject(subject_id)
        if subject is None:
            raise KeyError(f"Unknown subject '{subject_id}'")
        if subject["is_demo"]:
            raise ValueError("Use remove_sample_subject for the sample subject.")
        with self._connect() as connection:
            connection.execute("DELETE FROM attempts WHERE subject_id = ?", (subject_id,))
            connection.execute("DELETE FROM coaching_profiles WHERE subject_id = ?", (subject_id,))
            connection.execute("DELETE FROM subjects WHERE id = ?", (subject_id,))

    def save_attempt(
        self, subject_id: str, mode: str, result: dict, confidence=None,
        sitting=None, exam_set=None, exam_variant=None, time_limit_seconds=None, time_used_seconds=None,
    ):
        """Save one answer; mock-exam answers share a `sitting` id so a whole exam can be listed later."""
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO attempts (
                    subject_id, mode, topic_id, question_id,
                    score, max_score, is_answered, confidence, created_at,
                    sitting, exam_set, exam_variant, time_limit_seconds, time_used_seconds
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    subject_id,
                    mode,
                    result.get("topic_id"),
                    result.get("question_id"),
                    result["score"],
                    result["max_score"],
                    int(result.get("is_answered", True)),
                    confidence,
                    self._now(),
                    sitting,
                    exam_set,
                    exam_variant,
                    time_limit_seconds,
                    time_used_seconds,
                ),
            )

    def list_sittings(self, subject_id: str) -> list:
        """Mock-exam submissions, newest first: exam set, variant, date, and total score."""
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT sitting, exam_set, exam_variant, MIN(created_at) AS created_at,
                       SUM(score) AS score, SUM(max_score) AS max_score, COUNT(*) AS questions,
                       MAX(time_limit_seconds) AS time_limit_seconds, MAX(time_used_seconds) AS time_used_seconds
                FROM attempts
                WHERE subject_id = ? AND mode = 'mock_exam' AND sitting IS NOT NULL
                GROUP BY sitting
                ORDER BY created_at DESC
                """,
                (subject_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def export_subject(self, subject_id: str) -> dict:
        """Everything the database knows about a subject, ready to be written to an archive."""
        subject = self.get_subject(subject_id)
        if subject is None:
            raise KeyError(f"Unknown subject '{subject_id}'")
        attempts = [
            {key: value for key, value in row.items() if key not in ("id", "subject_id")}
            for row in reversed(self.list_attempts(subject_id))
        ]
        return {"subject": subject, "profile": self.get_profile(subject_id), "attempts": attempts}

    def import_subject(self, payload: dict):
        """Insert a subject exported by `export_subject`, always as a user subject."""
        subject = payload["subject"]
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO subjects (id, name, description, exam_date, target_score, materials_json, is_demo, created_at, status)
                VALUES (?, ?, ?, ?, ?, ?, 0, ?, ?)
                """,
                (
                    subject["id"],
                    subject["name"],
                    subject.get("description", ""),
                    subject.get("exam_date"),
                    subject.get("target_score", 80),
                    json.dumps(subject.get("materials", {})),
                    subject.get("created_at") or self._now(),
                    subject.get("status", "active"),
                ),
            )
            for row in payload.get("attempts", []):
                connection.execute(
                    """
                    INSERT INTO attempts (subject_id, mode, topic_id, question_id, score, max_score, is_answered,
                                          confidence, created_at, sitting, exam_set, exam_variant,
                                          time_limit_seconds, time_used_seconds)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        subject["id"],
                        row["mode"],
                        row.get("topic_id"),
                        row.get("question_id"),
                        row["score"],
                        row["max_score"],
                        int(row.get("is_answered", 1)),
                        row.get("confidence"),
                        row.get("created_at") or self._now(),
                        row.get("sitting"),
                        row.get("exam_set"),
                        row.get("exam_variant"),
                        row.get("time_limit_seconds"),
                        row.get("time_used_seconds"),
                    ),
                )
        profile = payload.get("profile")
        if profile:
            self.save_profile(
                subject["id"],
                {"id": profile["strategy_id"], "name": profile["strategy_name"], "description": profile["description"]},
                profile["diagnostic_score"],
                profile["confidence"],
            )

    def list_attempts(self, subject_id: str) -> list:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM attempts WHERE subject_id = ? ORDER BY id DESC",
                (subject_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def save_profile(self, subject_id: str, strategy: dict, diagnostic_score: float, confidence: int):
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO coaching_profiles (
                    subject_id, strategy_id, strategy_name, description,
                    diagnostic_score, confidence, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(subject_id) DO UPDATE SET
                    strategy_id = excluded.strategy_id,
                    strategy_name = excluded.strategy_name,
                    description = excluded.description,
                    diagnostic_score = excluded.diagnostic_score,
                    confidence = excluded.confidence,
                    updated_at = excluded.updated_at
                """,
                (
                    subject_id,
                    strategy["id"],
                    strategy["name"],
                    strategy["description"],
                    diagnostic_score,
                    confidence,
                    self._now(),
                ),
            )

    def get_profile(self, subject_id: str):
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM coaching_profiles WHERE subject_id = ?",
                (subject_id,),
            ).fetchone()
        return dict(row) if row else None
