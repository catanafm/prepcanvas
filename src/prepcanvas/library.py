"""Presentation helpers for the subject library home screen."""

from datetime import date, datetime
from typing import Optional


def exam_countdown(exam_date: Optional[str], today: date) -> str:
    if not exam_date:
        return "No exam date"
    days = (date.fromisoformat(exam_date) - today).days
    if days > 1:
        return f"Exam in {days} days"
    if days == 1:
        return "Exam tomorrow"
    if days == 0:
        return "Exam today"
    if days == -1:
        return "Exam was yesterday"
    return f"Exam was {-days} days ago"


def last_activity(attempts: list, now: datetime) -> str:
    """Describe the newest attempt; `attempts` arrive newest first."""
    if not attempts:
        return "Not started"
    moment = datetime.fromisoformat(attempts[0]["created_at"])
    days = (now.astimezone(moment.tzinfo).date() - moment.date()).days
    if days <= 0:
        return "Studied today"
    if days == 1:
        return "Studied yesterday"
    return f"Studied {days} days ago"


def group_subjects(subjects: list) -> dict:
    """Split subjects into in-progress and completed, soonest exam first."""

    def sort_key(subject):
        return (subject.get("exam_date") or "9999-12-31", subject["name"].casefold())

    return {
        "active": sorted((s for s in subjects if s.get("status", "active") != "completed"), key=sort_key),
        "completed": sorted((s for s in subjects if s.get("status") == "completed"), key=sort_key),
    }
