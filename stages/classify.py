"""Product category classification."""


def classify_product_category(product_name: str, description: str) -> tuple[str, float]:
    """Classify product category based on name and description.

    Returns: (category, confidence)
    """
    # Simple keyword-based classification
    text = (product_name + " " + description).lower()

    if any(word in text for word in ["culture", "medium", "media", "serum", "supplement"]):
        return ("cell_culture_media", 0.9)

    if any(word in text for word in ["reagent", "chemical", "buffer", "solution", "solvent"]):
        return ("chemical_reagent", 0.85)

    if any(word in text for word in ["antibody", "antibodies", "immunoglobulin"]):
        return ("antibody", 0.95)

    if any(word in text for word in ["instrument", "equipment", "analyzer", "machine"]):
        return ("analytical_instrument", 0.8)

    if any(word in text for word in ["tube", "plate", "flask", "dish", "consumable"]):
        return ("laboratory_consumable", 0.75)

    return ("other", 0.5)


def calculate_crawler_coverage(
    visibility_matrix: dict[str, dict[str, bool]],
    content_blocks: list,
    weights: dict[str, float]
) -> dict[str, float]:
    """Calculate crawler coverage score per agent."""
    scores = {}

    # Get all agent names from visibility matrix
    if not visibility_matrix:
        return scores

    first_block = next(iter(visibility_matrix.values()))
    agent_names = list(first_block.keys())

    for agent in agent_names:
        total_weight = 0.0
        visible_weight = 0.0

        for block in content_blocks:
            block_type = block.type
            weight = weights.get(block_type, 0.05)
            total_weight += weight

            if visibility_matrix.get(block.id, {}).get(agent, False):
                visible_weight += weight

        if total_weight > 0:
            scores[agent] = round(visible_weight / total_weight, 2)
        else:
            scores[agent] = 0.0

    return scores
