import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


class StudyStore:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self):
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

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

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

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

    def save_attempt(self, subject_id: str, mode: str, result: dict, confidence=None):
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO attempts (
                    subject_id, mode, topic_id, question_id,
                    score, max_score, is_answered, confidence, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                ),
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
