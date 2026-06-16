# GEO Audit Tool - Design Specification

**Date:** 2026-06-16  
**Status:** Approved for implementation  
**Build Scope:** Full system (all 5 stages)

## Executive Summary

A Python-based CLI tool that audits product pages for Generative Engine Optimization (GEO) effectiveness. **Primary objective:** Identify whether AI agents CITE the target page (driving qualified traffic to your site) vs answer generically (no traffic) vs cite competitors (traffic diverted). Tests both training data and live web retrieval to measure citation rates and traffic-driving potential.

**Business Goals:**
- Maximize citation rate: agents should reference your product page with prominent links
- Minimize generic answers: agents should NOT answer without citing sources (zero traffic)
- Prevent competitor deflection: agents should NOT cite competitor products instead
- Optimize citation format: prominent inline links drive more clicks than footnotes

**Key capabilities:**
- 5-stage pipeline: Fetch → Render → Extract → AI Test → Report
- Tests 5 AI platforms: OpenAI, Anthropic, Perplexity, Google, Bing (via Azure)
- Dual-mode testing: training data (no web) vs live retrieval (with web)
- Cross-agent retrieval matrix: diagnostic showing which agents retrieve/cite target
- Traffic impact analysis: citation rate, format, placement, click likelihood
- Competitor deflection detection: identifies when competitors cited instead
- Evidence-linked gap diagnosis with traffic-focused remediation priorities

## Design Decisions

### Architecture: Monolithic Pipeline

**Chosen approach:** Single orchestrator with stage functions passing shared AuditContext.

**Rationale:** 
- Evidence traceability requires full context visibility
- Sequential processing already chosen - no concurrency complexity needed
- Simple debugging - entire state visible at any point
- Natural error boundaries per stage

**Key pattern:**
```python
context = AuditContext(url=url, config=config)
context = stage_1_fetch(context)
context = stage_2_render(context)
context = stage_3_extract(context)
context = stage_4_prompts(context)
context = stage_5_report(context)
```

### Reference Answers: Auto-Generated

Reference answers for scoring generated automatically from browser content + schema. No manual authoring required per URL.

### Hallucination Detection: Hybrid Checklist

Category-specific fact extraction (catalog number, storage temp, molecular weight) with exact + fuzzy matching. Generic claims flagged separately from factual hallucinations.

### Product Category: Content-Based Classification

LLM classifier (GPT-4o-mini or Haiku) auto-categorizes each product using name + description. Zero-shot prompt returns category + confidence. Determines which fact checklist applies.

### Prompt Construction: Adversarial

Tool generates comparison prompts by discovering sibling SKUs via search, extracting distinguishing features, constructing prompts that test agent differentiation capability.

### Sibling Discovery: Search-Based

Google/SerpAPI search with `site:domain "category" "brand"` query. Extracts top product results from same domain, filters to same category, fetches and parses for comparison data.

### Agent Scoring: Hybrid

Critical facts (catalog number, specs, price) scored via fact-checking pipeline. Qualitative dimensions (workflow understanding, evidence quality) scored via LLM-as-judge. Weighted combination.

### Batch Processing: Sequential

One URL at a time through all stages. Simple, debuggable. Stage 4 prompts within a URL sent agent-parallel with per-agent rate limiting.

### Error Handling: Skip-and-Continue

Failed URL logs error, continues to next. Successful URLs generate reports. At end, summary shows which failed and why. Stage 1-3 failures abort that URL. Stage 4 failures allow technical-only report.

### PowerShell Import: Cache Check

Stage 1 checks for cached PowerShell audit files before fetching. If present and fresh (<24h), uses cached data. Otherwise fetches live.

## System Architecture

### Project Structure

```
geo-audit/
├── geo_audit.py              # CLI entry point, orchestrates all stages
├── audit_config.yaml          # User config: weights, rate limits, thresholds
├── .env                       # API keys (gitignored)
├── .env.example               # Template for API keys
├── requirements.txt           # Python dependencies
├── README.md                  # User-facing documentation
├── core/
│   ├── context.py            # AuditContext dataclass, all state lives here
│   ├── config.py             # Config loader, schema validator
│   └── evidence.py           # Evidence linking helpers
├── stages/
│   ├── fetch.py              # Stage 1: HTTP fetching + PowerShell import
│   ├── render.py             # Stage 2: Playwright browser rendering
│   ├── extract.py            # Stage 3: Content/schema extraction + scoring
│   ├── classify.py           # Stage 3: Product category classification
│   ├── prompts.py            # Stage 4: AI agent prompting
│   ├── sibling_discovery.py  # Stage 4: Search-based sibling finding
│   ├── scoring.py            # Stage 4: Hybrid fact-check + LLM-judge
│   └── report.py             # Stage 5: Gap diagnosis + report generation
├── prompts/
│   └── templates.yaml        # Base prompt templates per dimension
├── reports/
│   └── templates/
│       ├── audit.html.j2     # Jinja2 template for HTML report
│       └── failures.html.j2  # Jinja2 template for failures report
└── output/                   # Generated files (gitignored)
```

### CLI Interface

```bash
# Single URL
python geo_audit.py --url https://www.sigmaaldrich.com/US/en/product/sigma/c22010

# Batch from file
python geo_audit.py --urls urls.txt

# Custom config
python geo_audit.py --urls urls.txt --config custom-config.yaml

# Custom output directory
python geo_audit.py --urls urls.txt --output ./results

# Technical audit only (no AI testing)
python geo_audit.py --urls urls.txt --no-ai-audit
```

## Data Model

### AuditContext

Core state container flowing through all stages:

```python
@dataclass
class AuditContext:
    # Input
    url: str
    config: dict
    
    # Stage 1: Fetch
    fetch_results: dict[str, FetchResult]  # keyed by agent name
    locale_check: LocaleResult
    powershell_imported: bool
    
    # Stage 2: Render
    browser_html: str
    browser_text: str
    browser_screenshots: list[str]
    nextjs_data: dict | None
    lazy_loaded_content: str
    
    # Stage 3: Extract
    content_blocks: list[ContentBlock]
    visibility_matrix: dict  # block_id -> visibility_layer mapping
    json_ld_blocks: list[dict]
    product_schema: dict | None
    visual_assets: list[VisualAsset]
    product_category: str
    category_confidence: float
    crawler_coverage_scores: dict[str, float]
    
    # Stage 4: Prompts
    reference_facts: dict  # auto-generated from browser content
    sibling_products: list[SiblingProduct]
    prompts_sent: list[PromptExecution]
    agent_responses: list[AgentResponse]
    retrieval_matrices: list[CrossAgentRetrievalMatrix]  # NEW: cross-agent retrieval analysis
    
    # Stage 5: Report
    dimension_scores: dict[str, DimensionScore]
    gap_entries: list[GapEntry]
    remediation_list: list[RemediationItem]
    overall_geo_risk: str  # "low" | "medium" | "high" | "critical"
    
    # Cross-stage
    errors: list[ErrorEntry]
    warnings: list[WarningEntry]
    evidence_links: dict[str, Evidence]  # UUID -> Evidence mapping
```

### Evidence Linking

Every finding stores evidence UUID. Evidence object contains source, location, and raw content:

```python
@dataclass
class Evidence:
    id: str  # UUID
    source_type: str  # "fetch" | "render" | "schema" | "agent_response"
    source_agent: str | None  # crawler name or AI agent name
    content_ref: str  # JSON path, line range, block ID
    raw_content: str  # actual text/HTML that supports claim
    timestamp: datetime
```

**Design principle:** Every score, gap, and remediation links back to specific observable evidence. No inferred claims.

### Supporting Data Structures

```python
@dataclass
class FetchResult:
    agent_name: str
    status_code: int
    headers: dict
    body: str
    body_hash: str
    body_bytes: int
    response_time_ms: int
    final_url: str
    evidence_id: str

@dataclass
class ContentBlock:
    id: str  # UUID
    type: str  # From extended taxonomy (see CONTENT_BLOCK_TYPES)
    content: str
    html_snippet: str
    xpath: str
    character_count: int
    evidence_id: str

# Extended content block taxonomy (auto-classified during extraction)
CONTENT_BLOCK_TYPES = {
    "product_id", "product_name", "brand",
    "description_marketing", "description_technical", "specifications",
    "features_benefits", "applications", "protocols",
    "citations_publications", "quality_certifications", "data_sheets", "safety_information",
    "reviews", "ratings", "testimonials", "case_studies",
    "pricing", "availability", "shipping", "ordering",
    "faqs", "support_docs", "comparison_table", "compatibility",
    "images_product", "images_diagrams", "videos", "downloads"
}

@dataclass
class ContentBlockValue:
    """Value analysis: which content drives citations."""
    block_type: str
    block_id: str
    content_preview: str
    extracted_by_agents: list[str]  # Which agents extracted
    extraction_rate: float  # % of agents that extracted
    used_in_citations: list[str]  # Which responses used it
    usage_rate: float  # % that used when extracted
    citation_correlation_score: float  # Correlation with citation decision
    value_score: float  # 0-100 overall value
    value_tier: str  # "critical" | "high" | "medium" | "low"

@dataclass
class TrafficAnalysis:
    """Traffic-driving analysis per agent response."""
    cited_target: bool
    citation_format: str  # "prominent_link" | "footnote" | "inline" | "none"
    citation_placement: str  # "top" | "middle" | "bottom" | "absent"
    click_likelihood: float  # 0-100
    answered_without_citation: bool  # Generic answer, no sources
    cited_competitor: bool
    competitor_urls: list[str]
    traffic_verdict: str  # "drives_traffic" | "neutral" | "diverts_traffic" | "no_traffic"
    business_impact: str

@dataclass
class CompetitorAnalysis:
    """Auto-discovered competitor analysis."""
    competitor_domain: str
    competitor_name: str | None  # Extracted from page
    is_product_page: bool
    product_name: str | None
    citation_count: int
    cited_by_agents: list[str]
    avg_rank: float
    beats_target: bool

@dataclass
class SiblingProduct:
    url: str
    name: str
    product_id: str
    key_differences: list[str]

@dataclass
class PromptExecution:
    id: str
    dimension: str
    question: str
    prompt: str
    reference_content: dict
    sibling_context: list[SiblingProduct] | None
    pass_threshold: int

@dataclass
class RetrievalAnalysis:
    retrieved_target: bool  # Did agent fetch target URL?
    retrieved_urls: list[str]  # All URLs fetched
    target_url_rank: int | None  # Position of target (1=first, None=not retrieved)
    extracted_content: str  # What agent extracted from target
    extraction_quality: float  # 0-100: coverage of critical facts
    content_used_in_response: bool  # Did response use target content?
    content_usage_ratio: float  # % of extracted content used
    usage_classification: str  # "primary_source" | "supporting" | "contradicted" | "ignored"
    not_used_reason: str | None  # Why retrieved content wasn't used

@dataclass
class AgentResponse:
    prompt_id: str
    agent_name: str
    model: str
    model_tier: str  # "reasoning" | "flagship" | "balanced" | "fast"
    
    # Training mode (no web access)
    training_response: str
    training_score: float
    training_hallucinations: list[Hallucination]
    training_evidence_id: str
    
    # Live mode (with web access)
    live_response: str
    live_score: float
    live_hallucinations: list[Hallucination]
    live_evidence_id: str
    
    # Retrieval analysis (live mode only)
    retrieval_analysis: RetrievalAnalysis
    
    # Traffic analysis (live mode only)
    traffic_analysis: TrafficAnalysis
    
    # Score comparison
    improvement_from_live: float  # live_score - training_score

@dataclass
class AgentRetrievalStatus:
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
    url: str
    dimension: str
    retrieval_status: dict[str, AgentRetrievalStatus]  # keyed by "agent/model"
    retrieval_pattern: str  # "all_retrieved" | "google_missing" | "none_retrieved" etc
    citation_pattern: str
    diagnosis: str
    suggested_fix: str
    business_impact: str

@dataclass
class GapEntry:
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
    fix_category: str
    owner: str
    gaps_addressed: int
    dimensions_affected: list[str]
    agents_affected: list[str]
    effort_estimate: str  # "small" | "medium" | "large"
    impact_score: float
    priority_rank: int
    specific_actions: list[str]
    retest_condition: str
    evidence_ids: list[str]
```

## Stage Specifications

### Stage 1: Fetch & Import

**Purpose:** Acquire raw HTML from 6 user-agent perspectives, validate locale, check PowerShell cache.

**Execution flow:**

1. Check for PowerShell audit cache in `Scripts/` directory
2. If cache present and fresh (<24h), import data and skip live fetch
3. Otherwise, fetch URL with 6 agents: browser, googlebot, bingbot, oai-searchbot, claude-searchbot, perplexitybot
4. Record HTTP status, headers, body, hash, size, response time
5. Validate locale against expected (Content-Language, html lang, og:locale, hreflang)
6. Flag locale mismatch as critical error
7. Store all fetch results in context with evidence links

**PowerShell import logic:**

Looks for files matching pattern:
- `{crawler}.headers.txt`
- `{crawler}.visible-text.txt`
- `{crawler}.product-schema.json`

If all files present for a crawler and age < 24h, use cached data.

**User agents:**

```python
USER_AGENTS = {
    "browser": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/148.0.0.0",
    "googlebot": "Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Mobile Safari/537.36 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "bingbot": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm) Chrome/148.0.0.0 Safari/537.36",
    "oai-searchbot": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36; compatible; OAI-SearchBot/1.3; +https://openai.com/searchbot",
    "claude-searchbot": "Claude-SearchBot/1.0 (+https://www.anthropic.com)",
    "perplexitybot": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; PerplexityBot/1.0; +https://perplexity.ai/perplexitybot)"
}
```

### Stage 2: Browser Rendering

**Purpose:** Capture post-hydration HTML, Next.js data, and lazy-loaded content via headless Chromium.

**Execution flow:**

1. Launch Playwright Chromium browser in headless mode
2. Navigate to URL and wait for `networkidle`
3. Wait additional 2 seconds for DOM stabilization
4. Extract post-hydration HTML
5. Extract visible text (excludes script/style/hidden elements)
6. Extract Next.js `__NEXT_DATA__` script block if present
7. Simulate scroll to bottom to trigger lazy loading
8. Wait 1 second after scroll completion
9. Capture lazy-loaded content (full HTML after scroll)
10. Take full-page screenshot
11. Close browser

**Scroll implementation:**

```python
async def scroll_to_bottom(page):
    await page.evaluate("""
        async () => {
            await new Promise((resolve) => {
                let totalHeight = 0;
                const distance = 100;
                const timer = setInterval(() => {
                    window.scrollBy(0, distance);
                    totalHeight += distance;
                    if (totalHeight >= document.body.scrollHeight) {
                        clearInterval(timer);
                        resolve();
                    }
                }, 100);
            });
        }
    """)
```

**Output:**
- `browser_html`: Initial hydrated state after networkidle
- `lazy_loaded_content`: After scroll triggers lazy components
- Diff between the two reveals what's lazy-loaded vs initially rendered

### Stage 3: Extract & Classify

**Purpose:** Parse content into semantic blocks, build visibility matrix, extract structured data, classify product category, score crawler coverage.

**Execution flow:**

1. **Content block extraction:** Parse HTML from all sources (browser, 6 crawlers, lazy-loaded) into semantic chunks: product ID, name, description, specifications, applications, storage conditions, packaging, pricing, availability. Tag each with type, content, XPath, character count.

2. **Visibility matrix:** For each content block, determine which agents can see it. Classify visibility layer:
   - `server-rendered`: All crawlers see it
   - `js-rendered-only`: Only browser sees it
   - `schema-only`: In JSON-LD but not visible text
   - `absent`: Not present anywhere

3. **JSON-LD extraction:** Parse all `<script type="application/ld+json">` blocks. Find Product schema. Validate against schema.org spec.

4. **Visual asset audit:** Extract images and videos. Check dimensions, alt text, format, schema linkage, filename quality.

5. **Product category classification:** Send product name + description + schema type to LLM (GPT-4o-mini or Haiku). Get category + confidence:
   - `chemical_reagent`
   - `cell_culture_media`
   - `laboratory_consumable`
   - `analytical_instrument`
   - `antibody`
   - `other`

6. **Crawler coverage scoring:** For each crawler, calculate weighted score based on which critical content blocks it can see. Weights from config:
   ```python
   weights = {
       "product_id": 0.20,
       "product_name": 0.15,
       "description": 0.15,
       "specifications": 0.15,
       "storage_conditions": 0.10,
       "applications": 0.10,
       "pricing": 0.10,
       "availability": 0.05
   }
   ```

**Visibility matrix example:**

```python
{
    "block_uuid_1": {
        "browser": True,
        "googlebot": True,
        "bingbot": True,
        "oai-searchbot": True,
        "claude-searchbot": True,
        "perplexitybot": True,
        "layer": "server-rendered"
    },
    "block_uuid_2": {
        "browser": True,
        "googlebot": False,
        "layer": "js-rendered-only"
    }
}
```

### Stage 4: AI Agent Prompting & Retrieval Analysis

**Purpose:** Test AI agent understanding across 6 dimensions via BOTH training data and live retrieval. Analyze retrieval behavior, content extraction, and usage patterns across multiple models per agent.

**Dual-Mode Testing:**

Each prompt sent TWICE per model (except Perplexity which is always live):
- **Training mode:** No web access. Tests product representation in training corpus, staleness.
- **Live mode:** With web access. Tests crawler accessibility, extraction quality, grounding accuracy.

**Execution flow:**

1. **Generate reference facts:** Extract critical facts from Stage 3 data based on product category. Category-specific extraction (molecular weight for chemicals, storage temp for cell culture, etc.). Include pricing and availability from schema.

2. **Discover sibling products:** Search Google with `site:domain "category" "brand"` query. Extract top 10 results. Filter to product pages on same domain. Fetch top 3 candidates. Extract product schema and distinguishing features.

3. **Generate unbranded queries:** Extract product characteristics to build generic queries:
   - From product schema: application, specifications, category
   - From content blocks: key requirements, unique features
   - Construct queries real users would search with (no brand, no catalog number)
   - Example: "I need cell culture medium for endothelial cells with high glucose and L-glutamine"

4. **Build unbranded prompts:** For each of 6 dimensions, construct prompts using generic queries:
   - **Specificity:** "What makes a good [product type] for [application]?"
   - **Entity understanding:** "I need [product type] with [requirements]. What are my options?"
   - **Workflow:** "I'm planning to use [product type] for [application]. What should I know?"
   - **Evidence:** "What are the key factors when choosing [product type] for [application]?"
   - **Comparison:** "Compare options for [product type] with [requirements]."
   - **Commercial:** "Where can I buy [product type] for [application]?"

5. **Send to agents with dual-mode testing:** For each unbranded prompt and each configured model:
   - **Training mode call:** Disable web tools. Capture response from training data only.
   - **Live mode call:** Enable web search/grounding. Capture:
     - Tool calls made (search queries issued)
     - URLs retrieved (with rank order)
     - Content extracted from each URL
     - Final response

6. **Analyze retrieval behavior (live mode only):**
   - Check if agent retrieved target URL (from tool_calls or grounding metadata)
   - Extract target_url_rank from search/retrieval list
   - Extract content retrieved from target (from tool call text or grounding snippets)
   - Compare extracted_content vs reference_facts to measure extraction quality (0.0-1.0)
   - Classify usage: primary_source | supporting | contradicted | ignored
   - Measure content_usage_ratio: fraction of extracted_content actually used in final response
   - Respect per-agent rate limits with token bucket. Retry on 429 with exponential backoff.

6. **Analyze retrieval behavior (live mode only):**
   - **Retrieved target?** Check if target URL in retrieved URLs.
   - **Target rank:** Position of target (1=first consulted).
   - **Extracted content:** Parse from tool results/grounding metadata.
   - **Extraction quality:** Compare vs Stage 3 content blocks. Score 0-100 based on critical fact coverage.
   - **Content used?** Check if extracted facts appear in final response.
   - **Usage ratio:** % of extracted facts used.
   - **Usage classification:**
     - `primary_source`: Target page main source
     - `supporting`: Used alongside other sources
     - `contradicted`: Retrieved but contradicted, agent chose other sources
     - `ignored`: Retrieved but deemed irrelevant
   - **Not used reason (if ignored/contradicted):**
     - `contradicts_training`: Conflicts with training data
     - `deemed_irrelevant`: Judged not relevant
     - `parsing_failure`: Extraction failed
     - `low_confidence`: Low confidence in quality
     - `preferred_other_source`: Used competitor instead

6. **Score responses (dual mode):** For both training and live:
   - **Fact-checking:** Extract critical facts from response. Check each against page content (exact, fuzzy, semantic match). Score = (matched / total) × 100.
   - **LLM-as-judge:** For qualitative dimensions (workflow, evidence), send response + reference + page content to judge LLM. Score 0-100.
   - **Combine:** `(fact_score × 0.6) + (judge_score × 0.4)`.
   - **Compare:** Calculate improvement from live retrieval = live_score - training_score.

7. **Detect hallucinations (dual mode):** Extract factual claims using NER. For each claim, check if supported by page content or schema. Flag as hallucination if:
   - Critical fact not found anywhere
   - Generic claim synthesized without page access
   - Contradicts page content
   
   Classify hallucination type:
   - Training mode: `training_staleness`, `generic_synthesis`, `wrong_catalog_number`
   - Live mode: `retrieval_failure`, `parsing_error`, `sibling_confusion`, `competitor_deflection`

8. **Build cross-agent retrieval matrix:** For each dimension, analyze retrieval patterns across all agents:
   - Which agents retrieved target?
   - Which agents cited target?
   - Ranking patterns across agents
   - Usage patterns
   
   Diagnose based on pattern:
   - **All retrieved:** Content quality issue if not used
   - **Perplexity/OpenAI/Claude yes, Gemini no:** Google Search visibility problem (traditional SEO)
   - **None retrieved:** Critical discoverability failure
   - **Mixed retrieval:** Search engine-specific visibility issue

**Reference fact structure:**

```python
{
    "core": {
        "product_id": "C-22010",
        "product_name": "Endothelial Cell Growth Medium",
        "canonical_url": "https://..."
    },
    "chemical": {  # if category == chemical_reagent
        "molecular_weight": "...",
        "cas_number": "...",
        "purity": "...",
        "formula": "..."
    },
    "culture": {  # if category == cell_culture_media
        "storage_temp": "-20°C",
        "sterility": "sterile filtered",
        "supplements": [...]
    },
    "commercial": {
        "price": "299.00",
        "currency": "USD",
        "availability": "InStock"
    }
}
```

**Category-specific checklists:**

```python
CATEGORY_CHECKLISTS = {
    "chemical_reagent": ["molecular_weight", "cas_number", "purity", "formula", "storage_temp"],
    "cell_culture_media": ["storage_temp", "sterility", "supplements", "shelf_life"],
    "laboratory_consumable": ["material", "dimensions", "packaging_quantity", "autoclavable"],
    "antibody": ["host_species", "clonality", "target_species", "applications", "storage_temp"]
}
```

### Stage 5: Gap Diagnosis & Report Generation

**Purpose:** Trace failures to root causes, classify gaps, generate prioritized remediation list, produce all output files.

**Execution flow:**

1. **Score dimensions:** For each dimension, aggregate agent results. Calculate pass rate (% agents that scored >= threshold). Calculate average score across agents.

2. **Diagnose gaps:** For each failing agent response, trace root cause:
   - **generic_synthesis:** Check if unique facts exist on page. If not → `content_gap`.
   - **sibling_confusion:** Check if distinguishing features visible to crawlers. If not → `js_rendering_gap`.
   - **hallucination:** Check what content was missing. If fact exists nowhere → `content_gap`. If in schema but not HTML → `infrastructure_gap`.
   - **js_content_gap:** Visibility matrix shows JS-only blocks → `js_rendering_gap`.
   - **wrong_url/wrong_catalog_number:** Check if correct info in schema. If missing → `infrastructure_gap`.

3. **Map to fix categories:**
   - `infrastructure_gap`: Add Product JSON-LD, fix canonical, enable crawler access
   - `js_rendering_gap`: Server-render critical content, move specs to HTML
   - `content_gap`: Add storage conditions, write application guide, add contraindications
   - `selection_logic_gap`: Add comparison table, document SKU differences
   - `document_format_gap`: Structure as sections, add semantic HTML
   - `description_rewrite_gap`: Rewrite description, add specificity
   - `visual_gap`: Add product images, add alt text, add schema imageObject

4. **Prioritize remediations:** Group gaps by fix category. For each category:
   - Count gaps addressed
   - Identify dimensions affected
   - Identify agents affected
   - Estimate effort (small/medium/large)
   - Calculate impact score: `sum(dimension_weight × affected) × agents_affected`
   - Rank by impact/effort ratio
   - Generate specific actions per gap
   - Define re-test condition

5. **Calculate GEO risk:**
   ```python
   dim_pass_rate = avg(dimension_scores.pass_rate)
   avg_coverage = avg(crawler_coverage_scores)
   combined = (dim_pass_rate × 0.7) + (avg_coverage × 0.3)
   
   if combined >= 0.90: risk = "low"
   elif combined >= 0.75: risk = "medium"
   elif combined >= 0.50: risk = "high"
   else: risk = "critical"
   ```

6. **Generate outputs:**
   - `geo-audit-{product-id}-{timestamp}.json`: Full audit with crawl data, prompts, findings
   - `geo-audit-failures-{product-id}-{timestamp}.json`: Failed prompts with gap diagnosis
   - `geo-audit-report-{product-id}-{timestamp}.html`: Human-readable report
   - `geo-audit-report-{product-id}-{timestamp}.pdf`: PDF version via WeasyPrint

**Fix category owners:**

```python
FIX_CATEGORIES = {
    "infrastructure_gap": {
        "owner": "DevOps / Web Engineering",
        "examples": ["Add Product JSON-LD", "Fix canonical URL", "Enable crawler access"]
    },
    "js_rendering_gap": {
        "owner": "Frontend Engineering",
        "examples": ["Server-render critical content", "Move specs to HTML", "Add static fallback"]
    },
    "content_gap": {
        "owner": "Content / Product Management",
        "examples": ["Add storage conditions", "Write application guide", "Add contraindications"]
    },
    "selection_logic_gap": {
        "owner": "Content / Product Management",
        "examples": ["Add comparison table", "Document SKU differences", "Add selection guide"]
    },
    "document_format_gap": {
        "owner": "Content / Frontend Engineering",
        "examples": ["Structure as sections", "Add semantic HTML", "Improve heading hierarchy"]
    },
    "description_rewrite_gap": {
        "owner": "Content / Marketing",
        "examples": ["Rewrite product description", "Add specificity", "Remove jargon"]
    },
    "visual_gap": {
        "owner": "Content / Design",
        "examples": ["Add product images", "Add alt text", "Add schema imageObject"]
    }
}
```

## Configuration

### audit-config.yaml

```yaml
# Scoring weights
coverage_weights:
  product_id: 0.20
  product_name: 0.15
  description: 0.15
  specifications: 0.15
  storage_conditions: 0.10
  applications: 0.10
  pricing: 0.10
  availability: 0.05

impact_weights:
  specificity: 0.15
  entity_understanding: 0.20
  workflow_understanding: 0.20
  evidence_trust: 0.15
  comparison_selection: 0.20
  commercial_bridge: 0.10

# Pass threshold
pass_threshold: 70

# Rate limits per agent
rate_limits:
  openai:
    max_requests_per_minute: 50
    delay_between_requests: 1.5
    retry_attempts: 3
    backoff_multiplier: 2
    max_wait_time: 30
  
  anthropic:
    max_requests_per_minute: 50
    delay_between_requests: 1.5
    retry_attempts: 3
    backoff_multiplier: 2
    max_wait_time: 30
  
  perplexity:
    max_requests_per_minute: 20
    delay_between_requests: 3
    retry_attempts: 3
    backoff_multiplier: 2
    max_wait_time: 30
  
  google:
    max_requests_per_minute: 60
    delay_between_requests: 1
    retry_attempts: 3
    backoff_multiplier: 2
    max_wait_time: 30

# Testing scope
testing_scope: "flagship_only"  # "flagship_only" | "multi_model" | "minimal"

# Agent configurations
agents:
  openai:
    enabled: true
    test_training_mode: true
    models:
      # Flagship tier (always tested)
      - name: "gpt-4o"
        tier: "flagship"
        use_responses_api: true
        force_web_search: true
      - name: "o3-mini"
        tier: "reasoning"
        use_responses_api: true
        force_web_search: true
      
      # Additional models (only if testing_scope="multi_model")
      - name: "gpt-4o-mini"
        tier: "fast"
        use_responses_api: true
        force_web_search: true
      - name: "o1"
        tier: "reasoning"
        use_responses_api: true
        force_web_search: true
      - name: "chatgpt-4o-latest"
        tier: "flagship"
        use_responses_api: true
        force_web_search: true
  
  anthropic:
    enabled: true
    test_training_mode: true
    models:
      # Flagship tier
      - name: "claude-opus-4"
        tier: "flagship"
        tools: ["web_search"]
      
      # Additional models
      - name: "claude-sonnet-4"
        tier: "balanced"
        tools: ["web_search"]
      - name: "claude-sonnet-3-7"
        tier: "balanced"
        tools: ["web_search"]
      - name: "claude-haiku-4"
        tier: "fast"
        tools: ["web_search"]
  
  perplexity:
    enabled: true
    test_training_mode: false  # Always uses live search
    models:
      # Flagship tier
      - name: "sonar-pro"
        tier: "flagship"
      
      # Additional models
      - name: "sonar"
        tier: "standard"
      - name: "sonar-reasoning"
        tier: "reasoning"
  
  google:
    enabled: true
    test_training_mode: true
    models:
      # Flagship tier
      - name: "gemini-2.0-flash-exp"
        tier: "flagship"
        grounding: "google_search"
      
      # Additional models
      - name: "gemini-1.5-pro-latest"
        tier: "flagship"
        grounding: "google_search"
      - name: "gemini-1.5-flash"
        tier: "fast"
        grounding: "google_search"
  
  bing:
    enabled: true  # Systematic testing via Azure
    note: "Azure OpenAI + Bing Search (proxy for Copilot/Edge)"
    test_training_mode: true
    models:
      - name: "gpt-4o"
        tier: "flagship"
        deployment: "azure"
        bing_grounding: true

# Competitor monitoring (auto-discovery)
competitor_monitoring:
  enabled: true
  target_domain: "sigmaaldrich.com"  # Your domain
  
  # Optional: Known generic sources (non-competitive)
  known_generic_sources:
    - "wikipedia.org"
    - "protocols.io"
    - "addgene.org"
    - "nih.gov"
    - "ncbi.nlm.nih.gov"
    - "pubmed.gov"
  
  # Auto-classify all other cited product pages as competitors
  auto_discover_competitors: true

# Sibling discovery
sibling_discovery:
  max_siblings: 3
  search_provider: "serpapi"

# PowerShell import
powershell_import:
  enabled: true
  cache_directory: "./Scripts"
  max_age_hours: 24

# Browser rendering
rendering:
  headless: true
  viewport_width: 1920
  viewport_height: 1080
  network_idle_timeout: 5000
  screenshot: true

# Category checklists
category_checklists:
  chemical_reagent:
    - molecular_weight
    - cas_number
    - purity
    - formula
    - storage_temp
  
  cell_culture_media:
    - storage_temp
    - sterility
    - supplements
    - shelf_life
  
  laboratory_consumable:
    - material
    - dimensions
    - packaging_quantity
    - autoclavable
  
  antibody:
    - host_species
    - clonality
    - target_species
    - applications
    - storage_temp
```

### .env

```bash
# OpenAI
OPENAI_API_KEY=sk-...

# Anthropic
ANTHROPIC_API_KEY=sk-ant-...

# Perplexity
PERPLEXITY_API_KEY=pplx-...

# Google AI
GOOGLE_API_KEY=AIza...

# SerpAPI (for sibling discovery)
SERPAPI_KEY=...

# Optional: LLM-as-judge model
JUDGE_MODEL=gpt-4o-mini
JUDGE_API_KEY=sk-...

# Optional: Category classifier
CLASSIFIER_MODEL=gpt-4o-mini
CLASSIFIER_API_KEY=sk-...
```

## Dependencies

### requirements.txt

```txt
# Core
python>=3.11

# HTTP & async
httpx>=0.27.0
aiohttp>=3.9.0
asyncio>=3.4.3

# Browser automation
playwright>=1.40.0

# HTML parsing
beautifulsoup4>=4.12.0
lxml>=5.1.0

# AI agents
openai>=1.12.0
anthropic>=0.18.0
google-generativeai>=0.4.0

# Search
serpapi>=2.4.0

# Data processing
pydantic>=2.6.0
pyyaml>=6.0

# NLP & text processing
spacy>=3.7.0
sentence-transformers>=2.3.0
rapidfuzz>=3.6.0

# Report generation
jinja2>=3.1.3
weasyprint>=60.2
markdown>=3.5.0

# Utilities
python-dotenv>=1.0.0
tenacity>=8.2.0
```

### Post-install

```bash
# Install Playwright browsers
python -m playwright install chromium

# Download spaCy model for NER
python -m spacy download en_core_web_sm
```

## Error Handling & Logging

### Skip-and-Continue Pattern

```python
def process_url(url: str, config: dict) -> tuple[AuditContext | None, list[ErrorEntry]]:
    context = AuditContext(url=url, config=config, errors=[], warnings=[])
    
    # Stage 1-3: Fatal errors abort this URL
    try:
        context = stage_1_fetch(context)
        context = asyncio.run(stage_2_render(context))
        context = stage_3_extract(context)
    except Exception as e:
        context.errors.append(ErrorEntry(
            stage=..., type=..., message=..., fatal=True
        ))
        return None, context.errors
    
    # Stage 4: Non-fatal, can still generate technical report
    try:
        context = asyncio.run(stage_4_prompts(context))
    except Exception as e:
        context.errors.append(ErrorEntry(
            stage="prompts", type=..., message=..., fatal=False
        ))
    
    # Stage 5: Always runs if we got this far
    context = stage_5_report(context)
    
    return context, context.errors
```

### Logging Strategy

Structured logging to both console (INFO, human-readable) and file (DEBUG, JSON):

```python
logger.info("Stage 1: Fetching URL", extra={"url": context.url, "agents": [...]})
logger.debug("Crawler fetch complete", extra={"agent": "googlebot", "status": 200, "bytes": 416960})
logger.warning("Content visibility gap", extra={"block_id": "...", "visible_to": ["browser"], "missing_from": [...]})
logger.error("Agent API call failed", extra={"agent": "openai", "error": "RateLimitError", "retry_attempt": 2})
```

### Batch Orchestration

```python
def main():
    args = parse_args()
    config = load_config(args.config)
    urls = load_urls(args.url, args.urls)
    
    results = []
    failed_urls = []
    
    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] Processing: {url}")
        context, errors = process_url(url, config)
        
        if context:
            results.append(context)
            print(f"✓ Completed: {context.overall_geo_risk} risk")
        else:
            failed_urls.append((url, errors))
            print(f"✗ Failed: {errors[0].message}")
    
    # Generate cross-URL summary if batch
    if len(results) > 1:
        generate_summary_report(results)
    
    # Final summary
    print(f"\nProcessed: {len(results)}/{len(urls)} URLs")
    if failed_urls:
        print(f"\nFailed URLs:")
        for url, errors in failed_urls:
            print(f"  - {url}: {errors[0].message}")
    
    sys.exit(0 if not failed_urls else 1)
```

### Cross-URL Summary

Generated when batch contains multiple URLs:

```python
{
    "metadata": {
        "timestamp": "...",
        "total_urls": 15
    },
    "risk_distribution": {
        "low": 3,
        "medium": 7,
        "high": 4,
        "critical": 1
    },
    "coverage_stats": {
        "googlebot": {"mean": 71.4, "min": 50.6, "max": 100},
        "bingbot": {"mean": 71.4, "min": 50.6, "max": 100},
        ...
    },
    "common_failures": {
        "failure_type_distribution": {...},
        "systemic_fix_categories": {...},
        "most_affected_dimension": "entity_understanding",
        "agent_performance": [...]
    },
    "highest_risk_urls": [...],
    "fix_category_aggregation": {...}
}
```

## Output Files

### Per URL (5 files)

1. **geo-audit-{product-id}-{timestamp}.json**  
   Complete audit file with three sections:
   - `crawl`: Stage 1-3 data (fetch results, visibility matrix, structured data, coverage scores)
   - `prompts`: Stage 4 data (prompt text, dual-mode responses per model, retrieval analysis, scores)
   - `retrieval_matrices`: Cross-agent retrieval analysis per dimension
   - `findings`: Stage 5 data (dimension scores, gap diagnosis, prioritized remediation list)

2. **geo-audit-failures-{product-id}-{timestamp}.json**  
   Failed prompts only. Each entry contains:
   - Prompt text and dimension
   - Failing agent/model details with both training and live mode results
   - Retrieval status (retrieved? cited? used?)
   - Failure type classification
   - Plain-English explanation
   - GEO impact statement
   - Passing agents for contrast

3. **geo-audit-retrieval-{product-id}-{timestamp}.json**  
   Cross-agent retrieval matrices. For each dimension:
   - Retrieval status table (agent × model matrix)
   - Retrieval pattern diagnosis
   - Root cause classification
   - Recommended fixes

4. **geo-audit-content-value-{product-id}-{timestamp}.json**  
   Content block value rankings:
   - Value score per block (0-100)
   - Extraction rate, usage rate, citation correlation
   - Highest-value content (drives citations)
   - Lowest-value content (doesn't drive citations)
   - Aggregated scores by content type
   - Competitor content gap analysis

5. **geo-audit-competitors-{product-id}-{timestamp}.json**  
   Auto-discovered competitor analysis:
   - All competitors cited across all agents
   - Citation counts and ranks
   - Product pages identified
   - Traffic share analysis (target vs competitors)
   - Business impact assessment

6. **geo-audit-report-{product-id}-{timestamp}.html**  
   Human-readable report with expanded sections:
   - Page identity header
   - Executive summary (overall risk, citation rates, traffic verdicts)
   - Locale and delivery result
   - Crawler access and technical health
   - Content visibility matrix
   - Structured data audit
   - Visual asset audit
   - **Cross-Agent Retrieval Analysis** (primary diagnostic)
   - **Traffic Impact Analysis** (citation rates, formats, click likelihood)
   - **Competitor Discovery & Deflection** (auto-discovered competitors)
   - **Content Value Rankings** (what content drives citations)
   - Training vs Live Comparison per agent/model
   - Six dimension sections with dual-mode scores and unbranded prompts
   - Prioritized remediation list

7. **geo-audit-report-{product-id}-{timestamp}.pdf**  
   PDF version of HTML report via WeasyPrint.

### Cross-URL (1 file)

**geo-audit-summary-{timestamp}.json**  
Generated only when multiple URLs processed. Contains:
- Risk distribution across batch
- Coverage score statistics per crawler
- **Cross-URL retrieval pattern analysis:**
  - Which URLs consistently retrieved by all agents
  - Which URLs have Google-specific visibility problems  
  - Which URLs have universal discoverability issues
- Training vs live score improvements aggregated
- Common failure patterns per agent/model
- Highest-risk URLs ranked
- Catalogue-level content gap analysis
- Fix category aggregation (which fixes affect most URLs)

### Unbranded Prompts Template

**unbranded-prompts-{product-id}-{timestamp}.yaml**

Auto-generated unbranded prompts used in audit:
- Generic queries constructed from product characteristics
- No brand names, no catalog numbers
- Based on application, specifications, requirements
- Same prompts user would actually search with
- Allows reproduction of audit results

## Testing Strategy

### Unit Tests

```
tests/
├── test_fetch.py           # Mock HTTP responses, test PowerShell import
├── test_render.py          # Mock Playwright, test extraction
├── test_extract.py         # Test visibility matrix, scoring
├── test_classify.py        # Test category detection with fixtures
├── test_prompts.py         # Mock agent APIs, test prompt construction
├── test_scoring.py         # Test fact-check and LLM-judge logic
├── test_hallucination.py   # Test detection with known cases
├── test_report.py          # Test gap diagnosis and prioritization
└── fixtures/
    ├── sample_product_page.html
    ├── sample_crawler_responses/
    ├── sample_agent_responses.json
    └── expected_outputs.json
```

### Integration Tests

```
tests/integration/
├── test_full_pipeline.py   # End-to-end with real product URL
└── test_error_handling.py  # Force failures at each stage
```

### Run Tests

```bash
pytest tests/ -v --cov=geo_audit --cov-report=html
```

## Implementation Notes

### Evidence Traceability

Every finding must link to observable evidence. No inferred scores. Pattern:

1. Create evidence object when capturing data (fetch, render, extract, agent response)
2. Store evidence UUID in finding (gap entry, remediation item)
3. Evidence object contains source type, agent name, content reference, raw content
4. Report can always show "this finding came from this exact piece of data"

### Rate Limiting

Token bucket per agent with configurable refill rate. Async await on token acquisition. Retry logic with exponential backoff on 429. Max wait time prevents infinite hangs.

### Category Classification

Zero-shot LLM prompt with product name + description. Returns JSON with category + confidence. Determines which fact checklist to apply. Falls back to `other` category with generic checklist if confidence < 0.6.

### Sibling Discovery

Search-based to minimize manual config. Query: `site:{domain} "{category}" "{brand}"`. Filter results to product pages on same domain. Fetch top 3, parse schemas, extract distinguishing features. Used to build comparison prompts that test agent differentiation.

### Hallucination Detection

Extract factual claims using spaCy NER. Check each claim against page content and schema. Match methods: exact string match, fuzzy match (edit distance), semantic similarity (embeddings). Flag as hallucination only if no match method succeeds. Classify hallucination type for remediation mapping.

### Hybrid Scoring

Critical facts (catalog number, storage temp, molecular weight) scored via fact-checking pipeline with category-specific checklist. Qualitative dimensions (workflow understanding, evidence quality) scored via LLM-as-judge with reference answer + page content. Combine with 60/40 weight. Defensible because fact-check is deterministic and judge prompt includes evidence.

### Gap Diagnosis

Every failing agent response traced to root cause via decision tree:
- Is the content missing from page? → `content_gap`
- Is the content only in JS-rendered HTML? → `js_rendering_gap`
- Is the content in schema but not HTML? → `infrastructure_gap`
- Is distinguishing info missing for comparison? → `selection_logic_gap`
- Is the content present but poorly formatted? → `document_format_gap`

Each root cause maps to fix category with owner, effort estimate, and specific re-test condition.

### Remediation Prioritization

Group gaps by fix category. Calculate impact score: `sum(dimension_weight × is_affected) × count(affected_agents)`. Estimate effort based on category and gap count. Rank by impact/effort ratio. Generate specific actions from gap details. Define re-test condition: "After this fix is deployed, this dimension should score >= 70 for these agents."

### PowerShell Import

Checks for cached files at Stage 1 start. If present and age < 24h, skips live fetch for that crawler. Reduces load on target site during iterative debugging. Files must match naming pattern exactly. Missing files for any crawler triggers live fetch for that crawler.

## Cost Analysis

### Flagship-Only Mode (Default)

**Models tested per URL:**
- OpenAI: gpt-4o, o3-mini (2 models)
- Anthropic: claude-opus-4 (1 model)
- Google: gemini-2.0-flash-exp (1 model)
- Perplexity: sonar-pro (1 model)

**API calls per URL:**
- OpenAI: 2 models × 2 modes × 6 dimensions = 24 calls
- Anthropic: 1 model × 2 modes × 6 dimensions = 12 calls
- Google: 1 model × 2 modes × 6 dimensions = 12 calls
- Perplexity: 1 model × 1 mode × 6 dimensions = 6 calls
- Other (SerpAPI, classifier, judge): ~3 calls
- **Total: ~57 calls per URL**

**Cost per URL:**
| Service | Calls | Rate | Total |
|---------|-------|------|-------|
| OpenAI (with search) | 24 | $0.02 | $0.48 |
| Anthropic (with tools) | 12 | $0.03 | $0.36 |
| Google (with grounding) | 12 | $0.02 | $0.24 |
| Perplexity | 6 | $0.01 | $0.06 |
| Other | 3 | $0.01 | $0.02 |
| **Total** | | | **$1.16** |

**10 URLs = ~$12**  
**50 URLs = ~$58**

### Multi-Model Mode

All model tiers tested (5 OpenAI, 5 Anthropic, 4 Google, 3 Perplexity).

**API calls per URL:** ~186 calls  
**Cost per URL:** ~$3.28  
**10 URLs = ~$33**

### Minimal Mode

Single model per agent (gpt-4o, claude-sonnet-4, sonar-pro). Skip Gemini.

**API calls per URL:** ~30 calls  
**Cost per URL:** ~$0.60  
**10 URLs = ~$6**

## Risks & Mitigations

### Risk: API Rate Limits

**Mitigation:** Per-agent token bucket rate limiter. Configurable delays. Exponential backoff on 429. Max wait timeout prevents infinite hangs. Stage 4 failures don't abort - tool still generates technical report.

### Risk: High API Costs in Multi-Model Mode

**Mitigation:** Default to flagship-only mode ($1.16/URL). User must explicitly enable multi-model. Cost estimate shown before run starts. Confirm prompt if total > $50.

### Risk: Category Misclassification

**Mitigation:** Classifier returns confidence score. Fall back to `other` category with generic checklist if confidence < 0.6. User can inspect category in output and re-run with manual override if needed.

### Risk: Sibling Discovery Noise

**Mitigation:** Filter search results to same domain. Parse product schema to confirm it's a product page. Extract distinguishing features to verify it's comparable. Limit to top 3 siblings. Skip comparison dimension if no siblings found.

### Risk: Retrieval Analysis False Positives

**Mitigation:** Use explicit tool call logs from APIs (not inference). OpenAI Responses API, Anthropic tool_use blocks, Gemini grounding_metadata all provide structured retrieval data. Only flag "not retrieved" if explicitly absent from API response.

### Risk: Large Batch Slowness

**Mitigation:** Sequential processing. Stage 1-3 fast (< 1 min/URL). Stage 4 is 2-5 min/URL with dual-mode testing. Progress bar shows completion. For 50+ URLs, run overnight.

### Risk: PowerShell Cache Staleness

**Mitigation:** 24h age limit. Tool notes in report whether data was imported or fetched live. User can disable cache with `--skip-powershell-import` flag if testing recent changes.

## Success Criteria

### Functional Requirements

- [x] Tool processes single URL and batch URLs from file
- [x] All 5 stages execute sequentially per URL
- [x] PowerShell import works when cache present
- [x] Browser rendering captures lazy-loaded content
- [x] Content blocks extracted with visibility matrix
- [x] Product category auto-classified
- [x] Crawler coverage scored with weighted metrics
- [x] Reference facts auto-generated from page content
- [x] Sibling products discovered via search
- [x] Adversarial prompts generated per dimension
- [x] Agent responses scored with hybrid approach
- [x] Hallucinations detected with category-specific checklists
- [x] Gap diagnosis traces failures to root causes
- [x] Remediation list prioritized by impact/effort
- [x] All output files generated per specification
- [x] Cross-URL summary generated for batches
- [x] Skip-and-continue error handling works
- [x] Logging to console and file

### Non-Functional Requirements

- Performance: < 1 min for Stage 1-3, 2-5 min for Stage 4-5 per URL
- Reliability: Skip-and-continue allows batch completion despite individual failures
- Evidence: Every finding links to observable source data
- Configurability: Weights, thresholds, rate limits externalized to config
- Extensibility: Add new dimensions by updating prompt templates
- Debuggability: Structured logs with context per stage

### Validation Tests

1. Run tool on test product URL from existing PowerShell audit
2. Verify PowerShell import works (Stage 1 uses cached data)
3. Run tool with `--skip-powershell-import` to test live fetch
4. Verify browser rendering captures Next.js data
5. Verify content blocks extracted with correct visibility layer
6. Verify product category classified correctly
7. Verify sibling products discovered and parsed
8. Verify prompts constructed with sibling context
9. Verify agent responses scored correctly
10. Verify hallucinations flagged appropriately
11. Verify gap diagnosis traces to correct root cause
12. Verify remediation list prioritized correctly
13. Run batch of 5 URLs, verify cross-URL summary generated
14. Force Stage 1 error, verify skip-and-continue works
15. Force Stage 4 error, verify technical report still generated

## Future Enhancements

Not in scope for initial build, but documented for future consideration:

1. **Parallel batch processing:** URL-parallel execution with shared rate limiter pool. Reduces batch time but increases complexity.

2. **Manual reference answers:** Allow user to provide reference answers per URL in config. Override auto-generated answers for higher accuracy.

3. **Schema-based sibling discovery:** Extract related product links from `Product.isVariantOf` or `Product.isSimilarTo` schema properties instead of search.

4. **Resume capability:** Save intermediate results after each stage. Allow restart from last successful stage if tool crashes.

5. **Custom dimensions:** Allow user to define additional test dimensions beyond the core 6 in config.

6. **Competitor testing:** Extend sibling discovery to find competitor products on other domains. Test whether agents recommend correct brand.

7. **Temporal testing:** Re-run audit on same URL over time. Track GEO score trends. Alert on regressions.

8. **CI/CD integration:** GitHub Action or GitLab CI template. Run audit on deploy preview URLs. Block merge if GEO risk increases.

9. **Interactive mode:** CLI prompts user for missing config values instead of failing. Wizard-style setup for first run.

10. **Agent response caching:** Cache agent responses for same prompt + model + content hash. Reduce API calls when iterating on scoring logic.
