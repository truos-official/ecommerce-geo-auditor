"""Response scoring logic."""


def score_response(response_text: str, reference_facts: dict) -> float:
    """Score agent response against reference facts.

    Returns: Score 0-100
    """
    if not response_text or not reference_facts:
        return 0.0

    # Flatten reference facts
    fact_values = []
    for category_dict in reference_facts.values():
        if isinstance(category_dict, dict):
            for value in category_dict.values():
                if value and str(value).strip():
                    fact_values.append(str(value).lower())

    if not fact_values:
        return 50.0  # No facts to check

    # Check how many facts appear in response
    response_lower = response_text.lower()
    matched = sum(1 for fact in fact_values if fact in response_lower)

    score = (matched / len(fact_values)) * 100
    return round(min(score, 100.0), 1)
