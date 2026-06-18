"""Retrieval analysis from agent responses."""

from core.context import RetrievalAnalysis
from agents.client import AgentResponse


def analyze_retrieval(
    response: AgentResponse,
    target_url: str,
    reference_facts: dict
) -> RetrievalAnalysis:
    """Analyze retrieval behavior from agent response."""
    retrieved_target = target_url in response.retrieved_urls
    target_rank = None

    if retrieved_target:
        target_rank = response.retrieved_urls.index(target_url) + 1

    extracted_content = response.text if retrieved_target else ""

    # Simple extraction quality based on fact coverage
    extraction_quality = 0.0
    if extracted_content:
        fact_count = sum(
            1 for cat in reference_facts.values()
            if isinstance(cat, dict)
            for val in cat.values()
            if val and str(val).lower() in extracted_content.lower()
        )
        total_facts = sum(
            1 for cat in reference_facts.values()
            if isinstance(cat, dict)
            for val in cat.values()
            if val
        )
        extraction_quality = fact_count / total_facts if total_facts > 0 else 0.0

    content_used = len(extracted_content) > 0
    usage_ratio = 0.8 if content_used else 0.0

    # Classify usage
    if not retrieved_target:
        usage_classification = "ignored"
    elif usage_ratio > 0.7:
        usage_classification = "primary_source"
    elif usage_ratio > 0.3:
        usage_classification = "supporting"
    else:
        usage_classification = "contradicted"

    not_used_reason = None
    if usage_classification == "ignored":
        not_used_reason = "not_retrieved"

    return RetrievalAnalysis(
        retrieved_target=retrieved_target,
        retrieved_urls=response.retrieved_urls,
        target_url_rank=target_rank,
        extracted_content=extracted_content[:500],
        extraction_quality=round(extraction_quality, 2),
        content_used_in_response=content_used,
        content_usage_ratio=round(usage_ratio, 2),
        usage_classification=usage_classification,
        not_used_reason=not_used_reason
    )
