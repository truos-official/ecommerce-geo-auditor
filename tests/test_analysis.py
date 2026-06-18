import pytest
from stages.scoring import score_response
from stages.retrieval_analysis import analyze_retrieval
from stages.traffic_analysis import analyze_traffic, detect_citation_format
from agents.client import AgentResponse

def test_score_response():
    response = "Product TEST-001 costs $99.99"
    facts = {
        "core": {"product_id": "TEST-001"},
        "commercial": {"price": "99.99"}
    }

    score = score_response(response, facts)
    assert score > 50.0

def test_analyze_retrieval():
    response = AgentResponse(
        text="Product info here",
        mode="live",
        tool_calls=[],
        retrieved_urls=["https://example.com/product/test"],
        cost_usd=0.01
    )

    analysis = analyze_retrieval(response, "https://example.com/product/test", {})
    assert analysis.retrieved_target is True
    assert analysis.target_url_rank == 1

def test_detect_citation_format():
    text = "Buy at: https://example.com/product/test for best price"
    fmt = detect_citation_format(text, "https://example.com/product/test")
    assert fmt in ["prominent_link", "inline"]

def test_analyze_traffic():
    response = AgentResponse(
        text="Product available at https://example.com/product/test",
        mode="live",
        tool_calls=[],
        retrieved_urls=["https://example.com/product/test"],
        cost_usd=0.01
    )

    analysis = analyze_traffic(response, "https://example.com/product/test", "example.com")
    assert analysis.cited_target is True
    assert analysis.traffic_verdict in ["drives_traffic", "neutral"]
