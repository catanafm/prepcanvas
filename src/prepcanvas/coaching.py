def recommend_strategy(score_ratio: float, confidence: int) -> dict:
    """Choose a starting coaching style from diagnostic performance and confidence."""
    if score_ratio < 0.45 or confidence <= 2:
        return {
            "id": "guided_foundations",
            "name": "Guided foundations",
            "description": "Start with short explanations, worked examples, and low-stakes checks.",
        }
    if score_ratio < 0.8 or confidence <= 4:
        return {
            "id": "coach_and_recall",
            "name": "Coach + active recall",
            "description": "Alternate concise explanations with open recall and targeted feedback.",
        }
    return {
        "id": "exam_simulation",
        "name": "Exam simulation",
        "description": "Prioritize timed mixed practice and review only the gaps revealed by mistakes.",
    }
