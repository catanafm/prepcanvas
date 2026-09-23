import re


NEGATIONS = {"no", "not", "never"}
NUMBER_WORDS = {
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
    "ten": "10",
}
# Words that appear in almost any written sentence. A clause without them reads
# as a bare keyword list rather than an explanation.
FUNCTION_WORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "it", "its",
    "they", "them", "their", "this", "that", "these", "those", "of", "to", "in",
    "on", "for", "with", "by", "from", "how", "what", "why", "who", "which",
    "when", "can", "could", "should", "would", "will", "must", "has", "have",
    "had", "do", "does", "we", "you", "i", "if", "so", "as", "than", "much",
    "more", "less", "very", "too", "about",
}
KEYWORD_LIST_MIN_WORDS = 4
# Ordered so that longer suffixes win; replacements keep related forms aligned,
# e.g. durable / durability -> "durabl", repairable / repairability -> "repair".
SUFFIXES = (
    ("abilities", "abl"),
    ("ability", "abl"),
    ("ables", "abl"),
    ("able", "abl"),
    ("ities", ""),
    ("ity", ""),
    ("ies", "y"),
    ("ings", ""),
    ("ing", ""),
    ("ness", ""),
    ("ly", ""),
    ("ed", ""),
    ("s", ""),
)
CLAUSE_BREAK = re.compile(r"[.!?;,\n]+|\b(?:and|but|while|whereas)\b", re.IGNORECASE)
NOT_ONLY = re.compile(r"\bnot\s+(?:only|just|merely)\b", re.IGNORECASE)


def normalize_text(value: str) -> str:
    lowered = (value or "").lower()
    lowered = re.sub(r"n['’]t\b", " not", lowered)
    return " ".join(re.sub(r"[^a-z0-9\s-]", " ", lowered).split())


def _words(normalized: str) -> list:
    return [word for word in re.split(r"[\s-]+", normalized) if word]


def stem(word: str) -> str:
    """Reduce a word to a crude stem so inflected forms compare equal."""
    word = NUMBER_WORDS.get(word, word)
    if word.isdigit():
        return word
    for _ in range(2):
        for suffix, replacement in SUFFIXES:
            if suffix == "s" and word.endswith("ss"):
                continue
            if word.endswith(suffix) and len(word) - len(suffix) >= 3:
                word = word[: -len(suffix)] + replacement
                break
        else:
            break
    if word.endswith("abl") and len(word) >= 7:
        word = word[:-3]
    if word.endswith("e") and len(word) > 4:
        word = word[:-1]
    return word


def _term(text: str) -> tuple:
    """A rubric keyword or phrase as stemmed parts plus its joined spelling."""
    words = _words(normalize_text(text))
    return tuple(stem(word) for word in words), stem("".join(words))


def _contains(tokens: list, term: tuple) -> bool:
    parts, joined = term
    if not parts:
        return False
    width = len(parts)
    if any(tuple(tokens[index:index + width]) == parts for index in range(len(tokens) - width + 1)):
        return True
    return joined in tokens


def _clauses(answer: str) -> list:
    text = NOT_ONLY.sub(" ", answer or "")
    clauses = []
    for part in CLAUSE_BREAK.split(text):
        words = _words(normalize_text(part))
        if not words:
            continue
        clauses.append(
            {
                "tokens": [stem(word) for word in words],
                "negated": bool(set(words) & NEGATIONS),
                "keyword_list": len(words) >= KEYWORD_LIST_MIN_WORDS and not set(words) & FUNCTION_WORDS,
            }
        )
    return clauses


def _match_rubric_points(answer: str, points: list) -> list:
    """Return which rubric points the answer demonstrates.

    A point is matched in a single non-negated clause that contains its required
    keywords and either an accepted phrase or enough keywords. A clause that is
    only a keyword list can support at most one keyword-based point.
    """
    clauses = _clauses(answer)
    matched = [False] * len(points)
    list_candidates = {}
    for position, point in enumerate(points):
        phrases = [_term(item) for item in point.get("accepted_phrases", [])]
        keywords = [_term(item) for item in point.get("keywords", []) if normalize_text(item)]
        required = [_term(item) for item in point.get("required_keywords", []) if normalize_text(item)]
        minimum = point.get("minimum_keyword_matches", len(keywords))
        for index, clause in enumerate(clauses):
            tokens = clause["tokens"]
            if clause["negated"] or not all(_contains(tokens, term) for term in required):
                continue
            if any(_contains(tokens, phrase) for phrase in phrases):
                matched[position] = True
                break
            if keywords and sum(_contains(tokens, term) for term in keywords) >= minimum:
                if not clause["keyword_list"]:
                    matched[position] = True
                    break
                list_candidates.setdefault(position, []).append(index)

    used = set()
    for position, indexes in list_candidates.items():
        if matched[position]:
            continue
        free = next((index for index in indexes if index not in used), None)
        if free is not None:
            used.add(free)
            matched[position] = True
    return matched


def grade_question(question: dict, answer: str) -> dict:
    """Grade one demo question without an external AI service."""
    is_answered = bool(normalize_text(answer))
    if question["type"] == "multiple_choice":
        is_correct = normalize_text(answer) == normalize_text(question["correct_answer"])
        awarded = question["points"] if is_correct else 0
        return {
            "question_id": question["id"],
            "topic_id": question["topic_id"],
            "score": awarded,
            "max_score": question["points"],
            "is_answered": is_answered,
            "is_correct": is_correct,
            "matched_points": [],
            "missing_points": [] if is_correct else [question["correct_answer"]],
            "feedback": question["explanation"],
        }

    matched = []
    missing = []
    score = 0
    points = question["rubric_points"]
    for point, is_matched in zip(points, _match_rubric_points(answer, points)):
        if is_matched:
            matched.append(point["label"])
            score += point["points"]
        else:
            missing.append(point["label"])
    score = min(score, question["points"])
    return {
        "question_id": question["id"],
        "topic_id": question["topic_id"],
        "score": score,
        "max_score": question["points"],
        "is_answered": is_answered,
        "is_correct": score == question["points"],
        "matched_points": matched,
        "missing_points": missing,
        "feedback": question["explanation"],
    }


def grade_questions(questions: list, answers: dict) -> dict:
    results = [grade_question(question, answers.get(question["id"], "")) for question in questions]
    return {
        "results": results,
        "score": sum(item["score"] for item in results),
        "max_score": sum(item["max_score"] for item in results),
    }
