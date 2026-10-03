"""Identity for a selected exam, including the content it will grade against."""

import hashlib
import json


def exam_identity(subject: dict, exam_set: str, variant) -> str:
    content = {key: subject.get(key) for key in ("topics", "questions", "exam_blueprint")}
    revision = hashlib.sha256(json.dumps(content, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()
    return f"{subject['id']}:{revision}:{exam_set}:{variant or 0}"
