"""Core data structures for GEO audit context."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class Evidence:
    """Audit trail evidence."""
    id: str
    type: str
    source: str
    timestamp: str
    data: dict[str, Any]


@dataclass
class ContentBlock:
    """Extracted content block from page."""
    id: str
    type: str
    content: str
    xpath: str
    char_count: int
    visibility_layer: str


@dataclass
class ProductSchema:
    """Product JSON-LD schema data."""
    raw: dict[str, Any]
    product_id: str | None = None
    name: str | None = None
    description: str | None = None
    price: str | None = None
    currency: str | None = None
    availability: str | None = None


@dataclass
class SiblingProduct:
    """Sibling product for comparison."""
    url: str
    name: str
    product_id: str
    key_differences: list[str]


@dataclass
class Hallucination:
    """Detected hallucination in agent response."""
    type: str
    claim: str
    evidence_against: str
    severity: str


@dataclass
class RetrievalAnalysis:
    """Analysis of agent retrieval behavior."""
    retrieved_target: bool
    retrieved_urls: list[str]
    target_url_rank: int | None
    extracted_content: str
    extraction_quality: float
    content_used_in_response: bool
    content_usage_ratio: float
    usage_classification: str
    not_used_reason: str | None


@dataclass
class TrafficAnalysis:
    """Analysis of traffic impact."""
    cited_target: bool
    citation_format: str
    citation_placement: str
    click_likelihood: float
    answered_without_citation: bool
    cited_competitor: bool
    competitor_urls: list[str]
    traffic_verdict: str
    business_impact: str


@dataclass
class CompetitorAnalysis:
    """Auto-discovered competitor."""
    url: str
    domain: str
    citation_count: int
    citing_agents: list[str]
    classification: str


@dataclass
class ContentBlockValue:
    """Content block value ranking."""
    block_type: str
    extracted_by_agents: list[str]
    extraction_rate: float
    used_in_citations: list[str]
    usage_rate: float
    citation_correlation_score: float
    value_score: float
    value_tier: str


@dataclass
class PromptExecution:
    """Prompt execution details."""
    id: str
    dimension: str
    question: str
    prompt: str
    reference_content: dict[str, Any]
    sibling_context: list[SiblingProduct] | None
    pass_threshold: int


@dataclass
class AgentResult:
    """AI agent test result."""
    agent_name: str
    model_name: str
    prompt_id: str
    dimension: str

    # Training mode results
    training_response: str
    training_score: float
    training_hallucinations: list[Hallucination]
    training_evidence_id: str

    # Live mode results
    live_response: str
    live_score: float
    live_hallucinations: list[Hallucination]
    live_evidence_id: str

    # Retrieval analysis (live only)
    retrieval_analysis: RetrievalAnalysis | None = None

    # Traffic analysis (live only)
    traffic_analysis: TrafficAnalysis | None = None

    # Comparison
    improvement_from_live: float = 0.0


@dataclass
class RootCause:
    """Root cause of a failure."""
    type: str
    layer: str
    missing_content: list[str]
    contributing_factors: list[str]


@dataclass
class GapEntry:
    """Diagnosed gap."""
    dimension: str
    agent: str
    failure_type: str
    root_cause: RootCause
    fix_category: str
    evidence_ids: list[str]
    explanation: str
    geo_impact: str


@dataclass
class RemediationItem:
    """Remediation recommendation."""
    fix_category: str
    owner: str
    gaps_addressed: int
    dimensions_affected: list[str]
    agents_affected: list[str]
    effort_estimate: str
    impact_score: float
    priority_rank: int
    specific_actions: list[str]
    retest_condition: str
    evidence_ids: list[str]


@dataclass
class AgentRetrievalStatus:
    """Agent retrieval status for cross-agent matrix."""
    agent_name: str
    model: str
    searched: bool
    retrieved_target: bool
    target_rank: int | None
    cited_target: bool
    extraction_quality: float
    usage_classification: str


@dataclass
class CrossAgentRetrievalMatrix:
    """Cross-agent retrieval analysis."""
    url: str
    dimension: str
    retrieval_status: dict[str, AgentRetrievalStatus]
    retrieval_pattern: str
    citation_pattern: str
    diagnosis: str
    suggested_fix: str
    business_impact: str


@dataclass
class AuditContext:
    """Main audit context - flows through all stages."""

    # Input
    url: str

    # Stage 1: Fetch & Import
    http_responses: dict[str, dict[str, Any]] = field(default_factory=dict)
    powershell_cache: dict[str, Any] | None = None
    locale_valid: bool = False

    # Stage 2: Render
    lazy_loaded_content: str = ""
    js_rendered_diff: dict[str, Any] = field(default_factory=dict)

    # Stage 3: Extract & Classify
    content_blocks: list[ContentBlock] = field(default_factory=list)
    visibility_matrix: dict[str, dict[str, bool]] = field(default_factory=dict)
    product_schema: ProductSchema | None = None
    product_category: str = ""
    product_id: str | None = None
    crawler_coverage_scores: dict[str, float] = field(default_factory=dict)

    # Stage 4: AI Agent Prompting
    reference_facts: dict[str, Any] = field(default_factory=dict)
    siblings: list[SiblingProduct] = field(default_factory=list)
    prompts: list[PromptExecution] = field(default_factory=list)
    agent_results: list[AgentResult] = field(default_factory=list)

    # Stage 5: Gap Diagnosis
    gaps: list[GapEntry] = field(default_factory=list)
    remediations: list[RemediationItem] = field(default_factory=list)
    cross_agent_matrices: list[CrossAgentRetrievalMatrix] = field(default_factory=list)
    competitors: list[CompetitorAnalysis] = field(default_factory=list)
    content_value_rankings: list[ContentBlockValue] = field(default_factory=list)

    # Overall assessment
    overall_score: float = 0.0
    geo_risk_level: str = ""

    # Metadata
    audit_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    evidence_trail: list[Evidence] = field(default_factory=list)
    output_files: dict[str, str] = field(default_factory=dict)
