"""Mock-exam sets: the original practice exam, numbered variants from the pool, or everything.

A variant is composed deterministically from the package's `exam_blueprint`, so
variant 4 is always the same exam and can be retaken until it is mastered, while
variant 5 draws a different sample. Questions may recur across variants.
"""

import random


EXAM_SETS = ("source", "variant", "all")


def blueprint(package: dict):
    return package.get("exam_blueprint")


def source_questions(package: dict) -> list:
    return [question for question in package["questions"] if question.get("origin") == "source"]


def pool_for(package: dict, section: dict) -> list:
    return [
        question
        for question in package["questions"]
        if question["type"] == section["type"] and question["points"] == section["points"]
    ]


def shortfalls(package: dict) -> list:
    """Sections the pool cannot fill; empty when every variant can be composed."""
    plan = blueprint(package)
    if not plan:
        return []
    return [
        {"section": section, "available": len(pool_for(package, section))}
        for section in plan["sections"]
        if len(pool_for(package, section)) < section["count"]
    ]


def compose_variant(package: dict, variant: int) -> list:
    """Draw one exam from the pool by the blueprint, spread across topics, seeded by the variant number."""
    plan = blueprint(package)
    if not plan or variant < 1:
        return []
    rng = random.Random(f'{package["id"]}:{variant}')
    topic_order = {topic["id"]: index for index, topic in enumerate(package["topics"])}
    used = set()
    exam = []
    for section in plan["sections"]:
        by_topic = {}
        for question in pool_for(package, section):
            if question["id"] not in used:
                by_topic.setdefault(question["topic_id"], []).append(question)
        for candidates in by_topic.values():
            rng.shuffle(candidates)
        topics = sorted(by_topic)
        rng.shuffle(topics)
        picked = []
        while len(picked) < section["count"] and any(by_topic.values()):
            for topic_id in topics:
                if by_topic[topic_id] and len(picked) < section["count"]:
                    picked.append(by_topic[topic_id].pop())
        # Present each section in course order so the exam reads like the syllabus.
        picked.sort(key=lambda question: topic_order.get(question["topic_id"], 0))
        exam.extend(picked)
        used.update(question["id"] for question in picked)
    return exam


def exam_questions(package: dict, exam_set: str, variant: int = 1) -> list:
    if exam_set == "source":
        return source_questions(package)
    if exam_set == "variant":
        return compose_variant(package, variant)
    return list(package["questions"])


def describe(questions: list) -> str:
    """One line such as '14 multiple choice · 6 short answer · 90 points'."""
    counts = {"multiple_choice": 0, "short_answer": 0}
    for question in questions:
        counts[question["type"]] = counts.get(question["type"], 0) + 1
    parts = []
    if counts["multiple_choice"]:
        parts.append(f'{counts["multiple_choice"]} multiple choice')
    if counts["short_answer"]:
        parts.append(f'{counts["short_answer"]} short answer')
    parts.append(f'{sum(question["points"] for question in questions)} points')
    return " · ".join(parts)


def available_sets(package: dict) -> list:
    """Which exam sets this package supports, in display order."""
    sets = []
    if source_questions(package) and len(source_questions(package)) < len(package["questions"]):
        sets.append("source")
    if blueprint(package) and not shortfalls(package):
        sets.append("variant")
    sets.append("all")
    return sets


def next_variant(sat_variants) -> int:
    """The lowest variant number the learner has not sat yet."""
    sat = set(sat_variants)
    candidate = 1
    while candidate in sat:
        candidate += 1
    return candidate
