"""Validate database payloads before staging an archive replacement."""

from datetime import date, datetime
from math import isfinite


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def _integer(value, minimum=0, maximum=2**63 - 1):
    return type(value) is int and minimum <= value <= maximum


def _timestamp(value):
    if value is not None:
        _require(_text(value), "Timestamps must be ISO strings.")
        datetime.fromisoformat(value)


def validate_payload(payload):
    subject = payload["subject"]
    _require(isinstance(subject.get("description", ""), str), "Description must be text.")
    if subject.get("exam_date") is not None:
        _require(_text(subject["exam_date"]), "Exam date must be an ISO date.")
        date.fromisoformat(subject["exam_date"])
    _require(_integer(subject.get("target_score", 80), 1, 100), "Target must be between 1 and 100.")
    _require(subject.get("status", "active") in ("active", "completed"), "Unknown subject status.")
    materials = subject.get("materials", {})
    _require(isinstance(materials, dict) and all(type(v) is bool for v in materials.values()), "Material flags must be booleans.")
    _timestamp(subject.get("created_at"))
    attempts = payload.get("attempts", [])
    _require(isinstance(attempts, list) and len(attempts) <= 100000, "Invalid attempt list.")
    for row in attempts:
        _require(isinstance(row, dict), "Each attempt must be an object.")
        _require(row.get("mode") in ("diagnostic", "practice", "coaching", "mock_exam"), "Unknown attempt mode.")
        _require(_integer(row.get("max_score"), 1), "Attempt maximum must be positive.")
        _require(_integer(row.get("score"), 0, row["max_score"]), "Attempt score is out of range.")
        _require(type(row.get("is_answered", 1)) in (int, bool) and row.get("is_answered", 1) in (0, 1), "Invalid answer flag.")
        for field in ("topic_id", "question_id", "sitting"):
            _require(row.get(field) is None or _text(row[field]), f"Invalid {field}.")
        for field in ("time_limit_seconds", "time_used_seconds"):
            _require(row.get(field) is None or _integer(row[field]), f"Invalid {field}.")
        _require(row.get("confidence") is None or _integer(row["confidence"], 1, 5), "Invalid confidence.")
        _require(row.get("exam_variant") is None or _integer(row["exam_variant"], 1), "Invalid variant.")
        _require(row.get("exam_set") in (None, "source", "variant", "all"), "Invalid exam set.")
        _timestamp(row.get("created_at"))
    profile = payload.get("profile")
    if profile is not None:
        _require(isinstance(profile, dict), "Profile must be an object.")
        for field in ("strategy_id", "strategy_name", "description"):
            _require(_text(profile.get(field)), f"Profile needs {field}.")
        score = profile.get("diagnostic_score")
        _require(type(score) in (int, float) and isfinite(score) and 0 <= score <= 1, "Invalid diagnostic score.")
        _require(_integer(profile.get("confidence"), 1, 5), "Invalid profile confidence.")
        _timestamp(profile.get("updated_at"))
