"""Traffic impact analysis."""

from urllib.parse import urlparse
from core.context import TrafficAnalysis
from agents.client import AgentResponse


def detect_citation_format(text: str, target_url: str) -> str:
    """Detect how URL is cited."""
    if target_url not in text:
        return "none"

    url_pos = text.find(target_url)

    if url_pos < 100:
        return "prominent_link"
    elif url_pos > len(text) - 100:
        return "footnote"
    else:
        return "inline"


def detect_competitors(retrieved_urls: list[str], target_domain: str) -> list[str]:
    """Detect competitor URLs."""
    competitors = []

    generic_sources = ["wikipedia.org", "protocols.io", "nih.gov"]

    for url in retrieved_urls:
        domain = urlparse(url).netloc

        if domain == target_domain:
            continue

        if any(gs in domain for gs in generic_sources):
            continue

        if "/product/" in url or "/catalog/" in url:
            competitors.append(url)

    return competitors


def analyze_traffic(
    response: AgentResponse,
    target_url: str,
    target_domain: str
) -> TrafficAnalysis:
    """Analyze traffic impact from response."""
    cited_target = target_url in response.text
    citation_format = detect_citation_format(response.text, target_url)

    citation_placement = "none"
    if citation_format != "none":
        url_pos = response.text.find(target_url)
        if url_pos < len(response.text) / 3:
            citation_placement = "beginning"
        else:
            citation_placement = "middle"

    click_likelihood = {
        "prominent_link": 0.9,
        "inline": 0.7,
        "footnote": 0.3,
        "none": 0.0
    }.get(citation_format, 0.0)

    answered_without_citation = len(response.text) > 100 and not cited_target

    competitor_urls = detect_competitors(response.retrieved_urls, target_domain)
    cited_competitor = any(comp in response.text for comp in competitor_urls)

    # Determine verdict
    if cited_target and not cited_competitor:
        traffic_verdict = "drives_traffic"
        business_impact = "positive"
    elif cited_competitor:
        traffic_verdict = "diverts_traffic"
        business_impact = "negative_high"
    elif answered_without_citation:
        traffic_verdict = "no_traffic"
        business_impact = "negative_medium"
    else:
        traffic_verdict = "neutral"
        business_impact = "neutral"

    return TrafficAnalysis(
        cited_target=cited_target,
        citation_format=citation_format,
        citation_placement=citation_placement,
        click_likelihood=click_likelihood,
        answered_without_citation=answered_without_citation,
        cited_competitor=cited_competitor,
        competitor_urls=competitor_urls,
        traffic_verdict=traffic_verdict,
        business_impact=business_impact
    )
