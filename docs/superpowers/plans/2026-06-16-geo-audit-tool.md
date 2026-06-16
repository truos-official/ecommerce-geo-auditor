# GEO Audit Tool Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build Python CLI tool that audits product pages for GEO effectiveness by testing AI agent understanding across 6 dimensions with evidence-based gap diagnosis.

**Architecture:** Monolithic pipeline with shared AuditContext flowing through 5 sequential stages (Fetch → Render → Extract → AI Test → Report). Each stage is pure function returning modified context. Skip-and-continue error handling for batch processing.

**Tech Stack:** Python 3.11+, Playwright (browser automation), httpx (HTTP), BeautifulSoup (HTML parsing), OpenAI/Anthropic/Google/Perplexity APIs, spaCy (NER), Jinja2 (templating), WeasyPrint (PDF)

---

## File Structure

### Created Files

**Root:**
- `geo_audit.py` - CLI entry point, orchestrates all stages
- `audit-config.yaml` - Default configuration (weights, rate limits, thresholds)
- `.env.example` - Template for API keys
- `requirements.txt` - Python dependencies
- `urls.txt` - Example URL list

**core/** (shared data structures and utilities):
- `core/__init__.py`
- `core/context.py` - AuditContext dataclass, all state
- `core/config.py` - Config loader and validator
- `core/evidence.py` - Evidence linking helpers

**stages/** (5 pipeline stages):
- `stages/__init__.py`
- `stages/fetch.py` - Stage 1: HTTP fetching + PowerShell import
- `stages/render.py` - Stage 2: Playwright browser rendering
- `stages/extract.py` - Stage 3: Content extraction + visibility matrix
- `stages/classify.py` - Stage 3: Product category classification
- `stages/scoring.py` - Stage 3: Crawler coverage scoring
- `stages/prompts.py` - Stage 4: AI agent prompting
- `stages/sibling_discovery.py` - Stage 4: Search-based sibling finding
- `stages/fact_check.py` - Stage 4: Fact-checking + hallucination detection
- `stages/judge.py` - Stage 4: LLM-as-judge scoring
- `stages/report.py` - Stage 5: Gap diagnosis + report generation

**prompts/**:
- `prompts/templates.yaml` - Prompt templates per dimension

**reports/templates/**:
- `reports/templates/audit.html.j2` - Main HTML report template
- `reports/templates/failures.html.j2` - Failures report template

**tests/**:
- `tests/__init__.py`
- `tests/test_context.py`
- `tests/test_config.py`
- `tests/test_fetch.py`
- `tests/test_render.py`
- `tests/test_extract.py`
- `tests/test_classify.py`
- `tests/test_scoring.py`
- `tests/test_prompts.py`
- `tests/test_sibling_discovery.py`
- `tests/test_fact_check.py`
- `tests/test_judge.py`
- `tests/test_report.py`
- `tests/test_cli.py`
- `tests/integration/test_full_pipeline.py`
- `tests/fixtures/sample_product_page.html`
- `tests/fixtures/sample_crawler_responses/googlebot.html`
- `tests/fixtures/sample_schema.json`

**output/** (gitignored, created at runtime):
- Created by tool during execution

---

## Task 1: Project Scaffolding

**Files:**
- Create: `requirements.txt`
- Create: `.env.example`
- Create: `.gitignore`
- Create: `audit-config.yaml`
- Create: `urls.txt`
- Create: `README.md`

- [ ] **Step 1: Create requirements.txt**

```txt
# Core
httpx>=0.27.0
aiohttp>=3.9.0

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

# NLP
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

# Testing
pytest>=7.4.0
pytest-asyncio>=0.21.0
pytest-cov>=4.1.0
```

- [ ] **Step 2: Create .env.example**

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

# Optional: LLM-as-judge model (defaults to gpt-4o-mini)
JUDGE_MODEL=gpt-4o-mini
JUDGE_API_KEY=sk-...

# Optional: Category classifier (defaults to gpt-4o-mini)
CLASSIFIER_MODEL=gpt-4o-mini
CLASSIFIER_API_KEY=sk-...
```

- [ ] **Step 3: Create .gitignore**

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv
*.egg-info/
dist/
build/

# Environment
.env

# IDE
.vscode/
.idea/
*.swp
*.swo

# Output
output/

# Logs
*.log

# OS
.DS_Store
Thumbs.db

# Playwright
playwright/.ms-playwright/

# Coverage
.coverage
htmlcov/
```

- [ ] **Step 4: Create audit-config.yaml**

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

# Agent configurations
agents:
  openai:
    enabled: true
    models:
      - name: "gpt-4o"
        mode: "search"
      - name: "o3-mini"
        mode: "search"
  
  anthropic:
    enabled: true
    models:
      - name: "claude-sonnet-4"
        tools: ["web_search"]
  
  perplexity:
    enabled: true
    models:
      - name: "sonar-pro"
  
  google:
    enabled: true
    models:
      - name: "gemini-2.0-flash-exp"
        grounding: "google_search"

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

- [ ] **Step 5: Create urls.txt example**

```
# Example URLs for testing
https://www.sigmaaldrich.com/US/en/product/sigma/c22010
```

- [ ] **Step 6: Create basic README.md**

```markdown
# GEO Audit Tool

Python CLI tool for auditing product pages for Generative Engine Optimization effectiveness.

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
python -m playwright install chromium

# Install spaCy model
python -m spacy download en_core_web_sm

# Configure API keys
cp .env.example .env
# Edit .env with your API keys
```

## Usage

```bash
# Single URL
python geo_audit.py --url https://www.example.com/product/123

# Batch from file
python geo_audit.py --urls urls.txt

# Interactive mode
python geo_audit.py

# Technical audit only (no AI testing)
python geo_audit.py --urls urls.txt --no-ai-audit
```

## Output

Reports saved to `output/` directory:
- `geo-audit-{product-id}-{timestamp}.json` - Full audit data
- `geo-audit-failures-{product-id}-{timestamp}.json` - Failed prompts only
- `geo-audit-report-{product-id}-{timestamp}.html` - Human-readable report
- `geo-audit-report-{product-id}-{timestamp}.pdf` - PDF version
```

- [ ] **Step 7: Create directory structure**

Run:
```bash
mkdir -p core stages prompts reports/templates tests/integration tests/fixtures/sample_crawler_responses output
touch core/__init__.py stages/__init__.py tests/__init__.py
```

- [ ] **Step 8: Commit**

```bash
git add requirements.txt .env.example .gitignore audit-config.yaml urls.txt README.md
git add core/ stages/ prompts/ reports/ tests/
git commit -m "chore: project scaffolding and configuration"
```

---

## Task 2: Core Data Structures

**Files:**
- Create: `core/context.py`
- Create: `core/evidence.py`
- Create: `tests/test_context.py`

- [ ] **Step 1: Write failing test for AuditContext**

Create `tests/test_context.py`:

```python
import pytest
from datetime import datetime
from core.context import AuditContext, FetchResult, ContentBlock, Evidence

def test_audit_context_initialization():
    ctx = AuditContext(
        url="https://example.com/product/123",
        config={"pass_threshold": 70}
    )
    
    assert ctx.url == "https://example.com/product/123"
    assert ctx.config == {"pass_threshold": 70}
    assert ctx.fetch_results == {}
    assert ctx.errors == []
    assert ctx.evidence_links == {}

def test_fetch_result_creation():
    result = FetchResult(
        agent_name="googlebot",
        status_code=200,
        headers={"content-type": "text/html"},
        body="<html></html>",
        body_hash="abc123",
        body_bytes=13,
        response_time_ms=234,
        final_url="https://example.com/product/123",
        evidence_id="ev-001"
    )
    
    assert result.agent_name == "googlebot"
    assert result.status_code == 200
    assert result.body_bytes == 13

def test_evidence_creation():
    ev = Evidence(
        id="ev-001",
        source_type="fetch",
        source_agent="googlebot",
        content_ref="response.body",
        raw_content="<html></html>",
        timestamp=datetime.now()
    )
    
    assert ev.id == "ev-001"
    assert ev.source_type == "fetch"
    assert ev.source_agent == "googlebot"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_context.py -v`  
Expected: FAIL with "ModuleNotFoundError: No module named 'core.context'"

- [ ] **Step 3: Implement core/context.py**

Create `core/context.py`:

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class Evidence:
    id: str
    source_type: str  # "fetch" | "render" | "schema" | "agent_response"
    source_agent: Optional[str]
    content_ref: str
    raw_content: str
    timestamp: datetime

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
class LocaleResult:
    expected_locale: str
    content_language: Optional[str] = None
    html_lang: Optional[str] = None
    og_locale: Optional[str] = None
    hreflang: list[str] = field(default_factory=list)
    matches: bool = False
    critical_error: bool = False

@dataclass
class ContentBlock:
    id: str
    type: str
    content: str
    html_snippet: str
    xpath: str
    character_count: int
    evidence_id: str

@dataclass
class VisualAsset:
    id: str
    asset_type: str  # "image" | "video"
    url: str
    alt_text: Optional[str]
    width: Optional[int]
    height: Optional[int]
    format: Optional[str]
    in_schema: bool
    filename_quality: str  # "good" | "poor"
    evidence_id: str

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
    sibling_context: Optional[list[SiblingProduct]]
    pass_threshold: int

@dataclass
class Hallucination:
    claim: str
    type: str
    severity: str

@dataclass
class AgentResponse:
    prompt_id: str
    agent_name: str
    model: str
    mode: str
    raw_response: str
    cited_urls: list[str]
    score: float
    hallucinations: list[Hallucination]
    evidence_id: str

@dataclass
class DimensionScore:
    dimension: str
    agent_results: dict
    pass_rate: float
    avg_score: float

@dataclass
class RootCause:
    type: str
    detail: str
    evidence_ids: list[str]

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
    effort_estimate: str
    impact_score: float
    priority_rank: int
    specific_actions: list[str]
    retest_condition: str
    evidence_ids: list[str]

@dataclass
class ErrorEntry:
    stage: str
    type: str
    message: str
    fatal: bool

@dataclass
class WarningEntry:
    stage: str
    message: str

@dataclass
class AuditContext:
    url: str
    config: dict
    
    # Stage 1: Fetch
    fetch_results: dict[str, FetchResult] = field(default_factory=dict)
    locale_check: Optional[LocaleResult] = None
    powershell_imported: bool = False
    
    # Stage 2: Render
    browser_html: str = ""
    browser_text: str = ""
    browser_screenshots: list[str] = field(default_factory=list)
    nextjs_data: Optional[dict] = None
    lazy_loaded_content: str = ""
    
    # Stage 3: Extract
    content_blocks: list[ContentBlock] = field(default_factory=list)
    visibility_matrix: dict = field(default_factory=dict)
    json_ld_blocks: list[dict] = field(default_factory=list)
    product_schema: Optional[dict] = None
    visual_assets: list[VisualAsset] = field(default_factory=list)
    product_category: str = ""
    category_confidence: float = 0.0
    crawler_coverage_scores: dict[str, float] = field(default_factory=dict)
    
    # Stage 4: Prompts
    reference_facts: dict = field(default_factory=dict)
    sibling_products: list[SiblingProduct] = field(default_factory=list)
    prompts_sent: list[PromptExecution] = field(default_factory=list)
    agent_responses: list[AgentResponse] = field(default_factory=list)
    
    # Stage 5: Report
    dimension_scores: dict[str, DimensionScore] = field(default_factory=dict)
    gap_entries: list[GapEntry] = field(default_factory=list)
    remediation_list: list[RemediationItem] = field(default_factory=list)
    overall_geo_risk: str = ""
    
    # Cross-stage
    errors: list[ErrorEntry] = field(default_factory=list)
    warnings: list[WarningEntry] = field(default_factory=list)
    evidence_links: dict[str, Evidence] = field(default_factory=dict)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_context.py -v`  
Expected: PASS (all 3 tests)

- [ ] **Step 5: Write failing test for Evidence helpers**

Add to `tests/test_context.py`:

```python
from core.evidence import create_evidence, link_evidence

def test_create_evidence():
    ev = create_evidence(
        source_type="fetch",
        source_agent="googlebot",
        content_ref="response.body",
        raw_content="<html></html>"
    )
    
    assert ev.id.startswith("ev-")
    assert ev.source_type == "fetch"
    assert ev.source_agent == "googlebot"
    assert isinstance(ev.timestamp, datetime)

def test_link_evidence():
    ctx = AuditContext(url="https://example.com", config={})
    
    ev = link_evidence(
        ctx,
        source_type="fetch",
        source_agent="googlebot",
        content_ref="response.body",
        raw_content="<html></html>"
    )
    
    assert ev.id in ctx.evidence_links
    assert ctx.evidence_links[ev.id] == ev
```

- [ ] **Step 6: Run test to verify it fails**

Run: `pytest tests/test_context.py::test_create_evidence -v`  
Expected: FAIL with "ImportError: cannot import name 'create_evidence'"

- [ ] **Step 7: Implement core/evidence.py**

Create `core/evidence.py`:

```python
import uuid
from datetime import datetime
from typing import Optional
from core.context import Evidence, AuditContext

def create_evidence(
    source_type: str,
    source_agent: Optional[str],
    content_ref: str,
    raw_content: str
) -> Evidence:
    """Create Evidence object with generated UUID and timestamp."""
    return Evidence(
        id=f"ev-{uuid.uuid4().hex[:8]}",
        source_type=source_type,
        source_agent=source_agent,
        content_ref=content_ref,
        raw_content=raw_content,
        timestamp=datetime.now()
    )

def link_evidence(
    context: AuditContext,
    source_type: str,
    source_agent: Optional[str],
    content_ref: str,
    raw_content: str
) -> Evidence:
    """Create Evidence and add to context.evidence_links."""
    ev = create_evidence(source_type, source_agent, content_ref, raw_content)
    context.evidence_links[ev.id] = ev
    return ev
```

- [ ] **Step 8: Run test to verify it passes**

Run: `pytest tests/test_context.py -v`  
Expected: PASS (all 5 tests)

- [ ] **Step 9: Commit**

```bash
git add core/context.py core/evidence.py tests/test_context.py
git commit -m "feat: core data structures (AuditContext, Evidence)"
```

---

## Task 3: Configuration Loader

**Files:**
- Create: `core/config.py`
- Create: `tests/test_config.py`

- [ ] **Step 1: Write failing test for config loading**

Create `tests/test_config.py`:

```python
import pytest
import yaml
from pathlib import Path
from core.config import load_config, validate_config

def test_load_config_default():
    config = load_config("audit-config.yaml")
    
    assert "coverage_weights" in config
    assert "impact_weights" in config
    assert "pass_threshold" in config
    assert config["pass_threshold"] == 70

def test_validate_config_valid():
    config = {
        "coverage_weights": {"product_id": 0.20},
        "impact_weights": {"specificity": 0.15},
        "pass_threshold": 70,
        "rate_limits": {},
        "agents": {},
        "category_checklists": {}
    }
    
    validate_config(config)  # Should not raise

def test_validate_config_missing_key():
    config = {"coverage_weights": {}}
    
    with pytest.raises(ValueError, match="Missing required key"):
        validate_config(config)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_config.py -v`  
Expected: FAIL with "ImportError: cannot import name 'load_config'"

- [ ] **Step 3: Implement core/config.py**

Create `core/config.py`:

```python
import yaml
from pathlib import Path
from typing import Any

REQUIRED_KEYS = [
    "coverage_weights",
    "impact_weights",
    "pass_threshold",
    "rate_limits",
    "agents",
    "category_checklists"
]

def load_config(config_path: str) -> dict:
    """Load YAML configuration file."""
    path = Path(config_path)
    
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    validate_config(config)
    return config

def validate_config(config: dict) -> None:
    """Validate configuration has required keys."""
    for key in REQUIRED_KEYS:
        if key not in config:
            raise ValueError(f"Missing required key in config: {key}")
    
    # Validate pass_threshold is int between 0-100
    threshold = config.get("pass_threshold")
    if not isinstance(threshold, int) or not 0 <= threshold <= 100:
        raise ValueError(f"pass_threshold must be integer 0-100, got: {threshold}")

def get_enabled_agents(config: dict) -> list[str]:
    """Get list of enabled agent names from config."""
    agents = []
    for agent_name, agent_config in config.get("agents", {}).items():
        if agent_config.get("enabled", False):
            agents.append(agent_name)
    return agents
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_config.py -v`  
Expected: PASS (all 3 tests)

- [ ] **Step 5: Commit**

```bash
git add core/config.py tests/test_config.py
git commit -m "feat: configuration loader and validator"
```

---

## Task 4: Stage 1 - HTTP Fetching

**Files:**
- Create: `stages/fetch.py`
- Create: `tests/test_fetch.py`

- [ ] **Step 1: Write failing test for HTTP fetch**

Create `tests/test_fetch.py`:

```python
import pytest
from unittest.mock import Mock, patch
from core.context import AuditContext
from stages.fetch import stage_1_fetch, get_user_agent, fetch_url

def test_get_user_agent():
    ua = get_user_agent("googlebot")
    assert "Googlebot" in ua
    
    ua = get_user_agent("browser")
    assert "Chrome" in ua

def test_fetch_url():
    with patch('httpx.get') as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "text/html"}
        mock_response.text = "<html>test</html>"
        mock_response.url = "https://example.com/product"
        mock_response.elapsed.total_seconds.return_value = 0.234
        mock_get.return_value = mock_response
        
        result = fetch_url("https://example.com/product", "test-agent")
        
        assert result.status_code == 200
        assert result.body == "<html>test</html>"
        assert result.body_bytes == 18
        assert result.response_time_ms == 234

def test_stage_1_fetch():
    config = {
        "powershell_import": {"enabled": False}
    }
    ctx = AuditContext(url="https://example.com/product", config=config)
    
    with patch('stages.fetch.fetch_url') as mock_fetch:
        mock_fetch.return_value = Mock(
            agent_name="browser",
            status_code=200,
            body="<html></html>",
            body_bytes=13,
            evidence_id="ev-001"
        )
        
        ctx = stage_1_fetch(ctx)
        
        assert "browser" in ctx.fetch_results
        assert "googlebot" in ctx.fetch_results
        assert len(ctx.fetch_results) == 6  # All 6 agents
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_fetch.py -v`  
Expected: FAIL with "ImportError: cannot import name 'stage_1_fetch'"

- [ ] **Step 3: Implement stages/fetch.py (basic)**

Create `stages/fetch.py`:

```python
import httpx
import hashlib
from typing import Optional
from core.context import AuditContext, FetchResult
from core.evidence import link_evidence

USER_AGENTS = {
    "browser": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/148.0.0.0",
    "googlebot": "Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Mobile Safari/537.36 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "bingbot": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm) Chrome/148.0.0.0 Safari/537.36",
    "oai-searchbot": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36; compatible; OAI-SearchBot/1.3; +https://openai.com/searchbot",
    "claude-searchbot": "Claude-SearchBot/1.0 (+https://www.anthropic.com)",
    "perplexitybot": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; PerplexityBot/1.0; +https://perplexity.ai/perplexitybot)"
}

def get_user_agent(agent_name: str) -> str:
    """Get user-agent string for agent name."""
    return USER_AGENTS.get(agent_name, USER_AGENTS["browser"])

def fetch_url(url: str, agent_name: str, timeout: int = 30) -> FetchResult:
    """Fetch URL with specified user agent."""
    user_agent = get_user_agent(agent_name)
    headers = {"User-Agent": user_agent}
    
    response = httpx.get(url, headers=headers, timeout=timeout, follow_redirects=True)
    
    body = response.text
    body_hash = hashlib.sha256(body.encode()).hexdigest()[:12]
    response_time_ms = int(response.elapsed.total_seconds() * 1000)
    
    return FetchResult(
        agent_name=agent_name,
        status_code=response.status_code,
        headers=dict(response.headers),
        body=body,
        body_hash=body_hash,
        body_bytes=len(body),
        response_time_ms=response_time_ms,
        final_url=str(response.url),
        evidence_id=""  # Will be set when linked
    )

def stage_1_fetch(context: AuditContext) -> AuditContext:
    """Stage 1: Fetch URL with all crawler agents."""
    # Check PowerShell import (will implement later)
    if context.config.get("powershell_import", {}).get("enabled", False):
        # TODO: Try PowerShell import
        pass
    
    # Fetch with all agents
    agent_names = ["browser", "googlebot", "bingbot", "oai-searchbot", 
                   "claude-searchbot", "perplexitybot"]
    
    for agent_name in agent_names:
        result = fetch_url(context.url, agent_name)
        
        # Create evidence
        ev = link_evidence(
            context,
            source_type="fetch",
            source_agent=agent_name,
            content_ref=f"{agent_name}.response",
            raw_content=result.body[:500]  # First 500 chars
        )
        result.evidence_id = ev.id
        
        context.fetch_results[agent_name] = result
    
    return context
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_fetch.py -v`  
Expected: PASS (all 3 tests)

- [ ] **Step 5: Commit**

```bash
git add stages/fetch.py tests/test_fetch.py
git commit -m "feat(stage1): HTTP fetching with crawler user agents"
```

---

## Task 5: PowerShell Import Logic

**Files:**
- Modify: `stages/fetch.py`
- Modify: `tests/test_fetch.py`

- [ ] **Step 1: Write failing test for PowerShell import**

Add to `tests/test_fetch.py`:

```python
from pathlib import Path
from stages.fetch import check_powershell_cache, convert_ps_to_fetch_results

def test_check_powershell_cache_found(tmp_path):
    # Create mock PowerShell files
    scripts_dir = tmp_path / "Scripts"
    scripts_dir.mkdir()
    
    (scripts_dir / "googlebot.headers.txt").write_text("HTTP/1.1 200 OK\nContent-Type: text/html")
    (scripts_dir / "googlebot.visible-text.txt").write_text("Product text")
    (scripts_dir / "googlebot.product-schema.json").write_text('{"name": "Product"}')
    
    config = {
        "powershell_import": {
            "enabled": True,
            "cache_directory": str(scripts_dir),
            "max_age_hours": 24
        }
    }
    
    result = check_powershell_cache("https://example.com", config)
    
    assert result is not None
    assert "googlebot" in result

def test_check_powershell_cache_not_found():
    config = {
        "powershell_import": {
            "enabled": True,
            "cache_directory": "./nonexistent",
            "max_age_hours": 24
        }
    }
    
    result = check_powershell_cache("https://example.com", config)
    
    assert result is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_fetch.py::test_check_powershell_cache_found -v`  
Expected: FAIL with "ImportError: cannot import name 'check_powershell_cache'"

- [ ] **Step 3: Implement PowerShell import in stages/fetch.py**

Add to `stages/fetch.py`:

```python
import os
import json
from pathlib import Path
from datetime import datetime, timedelta

def check_powershell_cache(url: str, config: dict) -> Optional[dict]:
    """Check for cached PowerShell audit files. Returns dict of agent->data or None."""
    ps_config = config.get("powershell_import", {})
    
    if not ps_config.get("enabled", False):
        return None
    
    cache_dir = Path(ps_config.get("cache_directory", "./Scripts"))
    if not cache_dir.exists():
        return None
    
    max_age = timedelta(hours=ps_config.get("max_age_hours", 24))
    
    agents = ["googlebot", "bingbot", "oai-searchbot", "claude-searchbot", "perplexitybot"]
    cached_data = {}
    
    for agent in agents:
        # Check all required files exist
        headers_file = cache_dir / f"{agent}.headers.txt"
        text_file = cache_dir / f"{agent}.visible-text.txt"
        schema_file = cache_dir / f"{agent}.product-schema.json"
        
        if not all([headers_file.exists(), text_file.exists(), schema_file.exists()]):
            continue
        
        # Check age
        file_age = datetime.now() - datetime.fromtimestamp(headers_file.stat().st_mtime)
        if file_age > max_age:
            continue
        
        # Load files
        cached_data[agent] = {
            "headers": headers_file.read_text(encoding='utf-8'),
            "text": text_file.read_text(encoding='utf-8'),
            "schema": json.loads(schema_file.read_text(encoding='utf-8'))
        }
    
    return cached_data if cached_data else None

def convert_ps_to_fetch_results(cached_data: dict, url: str) -> dict[str, FetchResult]:
    """Convert PowerShell cached data to FetchResult objects."""
    results = {}
    
    for agent_name, data in cached_data.items():
        # Parse headers to get status code
        headers_text = data["headers"]
        status_line = headers_text.split('\n')[0]
        status_code = int(status_line.split()[1]) if len(status_line.split()) > 1 else 200
        
        # Build FetchResult
        body = data["text"]
        body_hash = hashlib.sha256(body.encode()).hexdigest()[:12]
        
        results[agent_name] = FetchResult(
            agent_name=agent_name,
            status_code=status_code,
            headers={},  # PowerShell doesn't parse all headers
            body=body,
            body_hash=body_hash,
            body_bytes=len(body),
            response_time_ms=0,  # Unknown from cache
            final_url=url,
            evidence_id=""
        )
    
    return results
```

Update `stage_1_fetch` function in `stages/fetch.py`:

```python
def stage_1_fetch(context: AuditContext) -> AuditContext:
    """Stage 1: Fetch URL with all crawler agents."""
    # Check PowerShell import
    cached_data = check_powershell_cache(context.url, context.config)
    
    if cached_data:
        context.fetch_results = convert_ps_to_fetch_results(cached_data, context.url)
        context.powershell_imported = True
        
        # Create evidence for cached data
        for agent_name, result in context.fetch_results.items():
            ev = link_evidence(
                context,
                source_type="fetch",
                source_agent=agent_name,
                content_ref=f"{agent_name}.cached",
                raw_content=result.body[:500]
            )
            result.evidence_id = ev.id
        
        return context
    
    # Fetch with all agents (existing code)
    agent_names = ["browser", "googlebot", "bingbot", "oai-searchbot", 
                   "claude-searchbot", "perplexitybot"]
    
    for agent_name in agent_names:
        result = fetch_url(context.url, agent_name)
        
        ev = link_evidence(
            context,
            source_type="fetch",
            source_agent=agent_name,
            content_ref=f"{agent_name}.response",
            raw_content=result.body[:500]
        )
        result.evidence_id = ev.id
        
        context.fetch_results[agent_name] = result
    
    return context
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_fetch.py -v`  
Expected: PASS (all tests including new PowerShell import tests)

- [ ] **Step 5: Commit**

```bash
git add stages/fetch.py tests/test_fetch.py
git commit -m "feat(stage1): PowerShell cache import"
```

---

## Task 6: Locale Validation

**Files:**
- Modify: `stages/fetch.py`
- Modify: `tests/test_fetch.py`

- [ ] **Step 1: Write failing test for locale validation**

Add to `tests/test_fetch.py`:

```python
from stages.fetch import validate_locale

def test_validate_locale_matches():
    html = '''
    <html lang="en-US">
    <head>
        <meta property="og:locale" content="en_US">
    </head>
    </html>
    '''
    headers = {"content-language": "en-US"}
    
    result = validate_locale(html, headers, "en-US")
    
    assert result.matches is True
    assert result.critical_error is False
    assert result.html_lang == "en-US"

def test_validate_locale_mismatch():
    html = '<html lang="de-DE"></html>'
    headers = {"content-language": "de-DE"}
    
    result = validate_locale(html, headers, "en-US")
    
    assert result.matches is False
    assert result.critical_error is True
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_fetch.py::test_validate_locale_matches -v`  
Expected: FAIL with "ImportError: cannot import name 'validate_locale'"

- [ ] **Step 3: Implement locale validation in stages/fetch.py**

Add to `stages/fetch.py`:

```python
from bs4 import BeautifulSoup
from core.context import LocaleResult

def validate_locale(html: str, headers: dict, expected_locale: str) -> LocaleResult:
    """Validate locale delivery against expected locale."""
    soup = BeautifulSoup(html, 'lxml')
    
    # Extract locale indicators
    content_language = headers.get("content-language")
    html_lang = soup.find('html').get('lang') if soup.find('html') else None
    
    og_locale = None
    og_meta = soup.find('meta', property='og:locale')
    if og_meta:
        og_locale = og_meta.get('content')
    
    hreflang = []
    for link in soup.find_all('link', rel='alternate'):
        if link.get('hreflang'):
            hreflang.append(link.get('hreflang'))
    
    # Normalize for comparison (en-US == en_US)
    def normalize(locale_str):
        if not locale_str:
            return None
        return locale_str.replace('_', '-').lower()
    
    expected_norm = normalize(expected_locale)
    
    # Check if any indicator matches
    matches = False
    if normalize(content_language) == expected_norm:
        matches = True
    if normalize(html_lang) == expected_norm:
        matches = True
    if normalize(og_locale) == expected_norm:
        matches = True
    
    return LocaleResult(
        expected_locale=expected_locale,
        content_language=content_language,
        html_lang=html_lang,
        og_locale=og_locale,
        hreflang=hreflang,
        matches=matches,
        critical_error=not matches
    )
```

Update `stage_1_fetch` to add locale check:

```python
def stage_1_fetch(context: AuditContext) -> AuditContext:
    """Stage 1: Fetch URL with all crawler agents."""
    # ... existing code ...
    
    # Locale validation (using browser response)
    if "browser" in context.fetch_results:
        browser_result = context.fetch_results["browser"]
        expected_locale = context.config.get("expected_locale", "en-US")
        
        context.locale_check = validate_locale(
            browser_result.body,
            browser_result.headers,
            expected_locale
        )
    
    return context
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_fetch.py -v`  
Expected: PASS (all tests)

- [ ] **Step 5: Commit**

```bash
git add stages/fetch.py tests/test_fetch.py
git commit -m "feat(stage1): locale validation"
```

---

## Task 7: Stage 2 - Playwright Rendering

**Files:**
- Create: `stages/render.py`
- Create: `tests/test_render.py`

- [ ] **Step 1: Write failing test for browser rendering**

Create `tests/test_render.py`:

```python
import pytest
from unittest.mock import Mock, patch, AsyncMock
from core.context import AuditContext
from stages.render import stage_2_render, scroll_to_bottom

@pytest.mark.asyncio
async def test_scroll_to_bottom():
    mock_page = AsyncMock()
    
    await scroll_to_bottom(mock_page)
    
    mock_page.evaluate.assert_called_once()

@pytest.mark.asyncio
async def test_stage_2_render():
    config = {
        "rendering": {
            "headless": True,
            "viewport_width": 1920,
            "viewport_height": 1080,
            "screenshot": True
        }
    }
    ctx = AuditContext(url="https://example.com/product", config=config)
    
    with patch('stages.render.async_playwright') as mock_playwright:
        mock_browser = AsyncMock()
        mock_page = AsyncMock()
        mock_page.content.return_value = "<html>rendered</html>"
        mock_page.evaluate.return_value = "Rendered text"
        mock_page.query_selector.return_value = None
        
        mock_browser.new_page.return_value = mock_page
        mock_playwright.return_value.__aenter__.return_value.chromium.launch.return_value = mock_browser
        
        ctx = await stage_2_render(ctx)
        
        assert ctx.browser_html == "<html>rendered</html>"
        assert ctx.browser_text == "Rendered text"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_render.py -v`  
Expected: FAIL with "ImportError: cannot import name 'stage_2_render'"

- [ ] **Step 3: Implement stages/render.py**

Create `stages/render.py`:

```python
import asyncio
import json
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright, Page
from core.context import AuditContext

async def scroll_to_bottom(page: Page):
    """Scroll page to bottom to trigger lazy loading."""
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

async def stage_2_render(context: AuditContext) -> AuditContext:
    """Stage 2: Render page with Playwright to capture JS content."""
    render_config = context.config.get("rendering", {})
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=render_config.get("headless", True)
        )
        
        page = await browser.new_page(
            viewport={
                "width": render_config.get("viewport_width", 1920),
                "height": render_config.get("viewport_height", 1080)
            }
        )
        
        # Load page and wait for network idle
        await page.goto(context.url)
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(2)  # Additional settle time
        
        # Extract post-hydration HTML
        context.browser_html = await page.content()
        
        # Extract visible text
        context.browser_text = await page.evaluate("() => document.body.innerText")
        
        # Extract Next.js data if present
        nextjs_script = await page.query_selector('script#__NEXT_DATA__')
        if nextjs_script:
            json_content = await nextjs_script.inner_text()
            try:
                context.nextjs_data = json.loads(json_content)
            except json.JSONDecodeError:
                pass
        
        # Simulate scroll for lazy loading
        await scroll_to_bottom(page)
        await asyncio.sleep(1)
        
        # Capture lazy-loaded content
        context.lazy_loaded_content = await page.content()
        
        # Screenshot
        if render_config.get("screenshot", True):
            output_dir = Path("output")
            output_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            screenshot_path = str(output_dir / f"screenshot-{timestamp}.png")
            await page.screenshot(path=screenshot_path, full_page=True)
            context.browser_screenshots.append(screenshot_path)
        
        await browser.close()
    
    return context
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_render.py -v`  
Expected: PASS (all tests)

- [ ] **Step 5: Commit**

```bash
git add stages/render.py tests/test_render.py
git commit -m "feat(stage2): Playwright browser rendering"
```

---

## Task 8: Stage 3 - Content Block Extraction

**Files:**
- Create: `stages/extract.py`
- Create: `tests/test_extract.py`
- Create: `tests/fixtures/sample_product_page.html`

- [ ] **Step 1: Create test fixture**

Create `tests/fixtures/sample_product_page.html`:

```html
<!DOCTYPE html>
<html lang="en-US">
<head>
    <title>Test Product</title>
    <script type="application/ld+json">
    {
        "@context": "https://schema.org/",
        "@type": "Product",
        "name": "Test Product",
        "sku": "TEST-001",
        "description": "A test product for GEO audit"
    }
    </script>
</head>
<body>
    <div class="product-id">Catalog: TEST-001</div>
    <h1 class="product-name">Test Product</h1>
    <div class="description">A test product for GEO audit</div>
    <div class="specifications">
        <h2>Specifications</h2>
        <ul>
            <li>Weight: 100g</li>
            <li>Dimensions: 10x10x10cm</li>
        </ul>
    </div>
</body>
</html>
```

- [ ] **Step 2: Write failing test for content extraction**

Create `tests/test_extract.py`:

```python
import pytest
from pathlib import Path
from core.context import AuditContext
from stages.extract import extract_content_blocks, extract_json_ld, find_product_schema

def load_fixture(filename):
    return Path(f"tests/fixtures/{filename}").read_text()

def test_extract_json_ld():
    html = load_fixture("sample_product_page.html")
    
    blocks = extract_json_ld(html)
    
    assert len(blocks) == 1
    assert blocks[0]["@type"] == "Product"
    assert blocks[0]["name"] == "Test Product"

def test_find_product_schema():
    html = load_fixture("sample_product_page.html")
    blocks = extract_json_ld(html)
    
    schema = find_product_schema(blocks)
    
    assert schema is not None
    assert schema["@type"] == "Product"
    assert schema["sku"] == "TEST-001"

def test_extract_content_blocks():
    html = load_fixture("sample_product_page.html")
    
    blocks = extract_content_blocks(html)
    
    assert len(blocks) > 0
    
    # Find product ID block
    product_id_block = next((b for b in blocks if b.type == "product_id"), None)
    assert product_id_block is not None
    assert "TEST-001" in product_id_block.content
```

- [ ] **Step 3: Run test to verify it fails**

Run: `pytest tests/test_extract.py -v`  
Expected: FAIL with "ImportError: cannot import name 'extract_content_blocks'"

- [ ] **Step 4: Implement stages/extract.py**

Create `stages/extract.py`:

```python
import json
import uuid
from bs4 import BeautifulSoup
from core.context import AuditContext, ContentBlock
from core.evidence import link_evidence

def extract_json_ld(html: str) -> list[dict]:
    """Extract all JSON-LD blocks from HTML."""
    soup = BeautifulSoup(html, 'lxml')
    
    blocks = []
    for script in soup.find_all('script', type='application/ld+json'):
        try:
            data = json.loads(script.string)
            blocks.append(data)
        except (json.JSONDecodeError, AttributeError):
            continue
    
    return blocks

def find_product_schema(json_ld_blocks: list[dict]) -> dict | None:
    """Find Product schema from JSON-LD blocks."""
    for block in json_ld_blocks:
        if isinstance(block, dict) and block.get("@type") == "Product":
            return block
        
        # Check if it's a graph with Product
        if isinstance(block, dict) and "@graph" in block:
            for item in block["@graph"]:
                if isinstance(item, dict) and item.get("@type") == "Product":
                    return item
    
    return None

def extract_content_blocks(html: str) -> list[ContentBlock]:
    """Extract semantic content blocks from HTML."""
    soup = BeautifulSoup(html, 'lxml')
    blocks = []
    
    # Product ID
    product_id_selectors = [
        ('class', 'product-id'),
        ('class', 'catalog-number'),
        ('class', 'sku'),
        ('id', 'product-id')
    ]
    for attr, value in product_id_selectors:
        elem = soup.find(attrs={attr: value})
        if elem:
            blocks.append(ContentBlock(
                id=f"block-{uuid.uuid4().hex[:8]}",
                type="product_id",
                content=elem.get_text(strip=True),
                html_snippet=str(elem)[:200],
                xpath=f"//{elem.name}[@{attr}='{value}']",
                character_count=len(elem.get_text()),
                evidence_id=""
            ))
            break
    
    # Product Name
    h1 = soup.find('h1')
    if h1:
        blocks.append(ContentBlock(
            id=f"block-{uuid.uuid4().hex[:8]}",
            type="product_name",
            content=h1.get_text(strip=True),
            html_snippet=str(h1)[:200],
            xpath="//h1",
            character_count=len(h1.get_text()),
            evidence_id=""
        ))
    
    # Description
    desc_selectors = [
        ('class', 'description'),
        ('class', 'product-description'),
        ('id', 'description')
    ]
    for attr, value in desc_selectors:
        elem = soup.find(attrs={attr: value})
        if elem:
            blocks.append(ContentBlock(
                id=f"block-{uuid.uuid4().hex[:8]}",
                type="description",
                content=elem.get_text(strip=True),
                html_snippet=str(elem)[:200],
                xpath=f"//{elem.name}[@{attr}='{value}']",
                character_count=len(elem.get_text()),
                evidence_id=""
            ))
            break
    
    # Specifications
    spec_selectors = [
        ('class', 'specifications'),
        ('class', 'specs'),
        ('id', 'specifications')
    ]
    for attr, value in spec_selectors:
        elem = soup.find(attrs={attr: value})
        if elem:
            blocks.append(ContentBlock(
                id=f"block-{uuid.uuid4().hex[:8]}",
                type="specifications",
                content=elem.get_text(strip=True),
                html_snippet=str(elem)[:200],
                xpath=f"//{elem.name}[@{attr}='{value}']",
                character_count=len(elem.get_text()),
                evidence_id=""
            ))
            break
    
    return blocks

def stage_3_extract(context: AuditContext) -> AuditContext:
    """Stage 3: Extract content blocks and structured data."""
    # Extract content blocks from browser HTML
    context.content_blocks = extract_content_blocks(context.browser_html)
    
    # Link evidence for each block
    for block in context.content_blocks:
        ev = link_evidence(
            context,
            source_type="render",
            source_agent=None,
            content_ref=f"content_block.{block.type}",
            raw_content=block.content
        )
        block.evidence_id = ev.id
    
    # Extract JSON-LD
    context.json_ld_blocks = extract_json_ld(context.browser_html)
    
    # Find product schema
    context.product_schema = find_product_schema(context.json_ld_blocks)
    
    return context
```

- [ ] **Step 5: Run test to verify it passes**

Run: `pytest tests/test_extract.py -v`  
Expected: PASS (all tests)

- [ ] **Step 6: Commit**

```bash
git add stages/extract.py tests/test_extract.py tests/fixtures/
git commit -m "feat(stage3): content block extraction and JSON-LD parsing"
```

---

## Task 9: Visibility Matrix

**Files:**
- Modify: `stages/extract.py`
- Modify: `tests/test_extract.py`

- [ ] **Step 1: Write failing test for visibility matrix**

Add to `tests/test_extract.py`:

```python
from stages.extract import build_visibility_matrix

def test_build_visibility_matrix():
    content_blocks = [
        ContentBlock(
            id="block-001",
            type="product_id",
            content="TEST-001",
            html_snippet="<div>TEST-001</div>",
            xpath="//div",
            character_count=8,
            evidence_id="ev-001"
        )
    ]
    
    browser_html = "<html><body><div>TEST-001</div></body></html>"
    crawler_htmls = {
        "googlebot": "<html><body><div>TEST-001</div></body></html>",
        "bingbot": "<html><body></body></html>"  # Missing content
    }
    
    matrix = build_visibility_matrix(content_blocks, browser_html, crawler_htmls)
    
    assert "block-001" in matrix
    assert matrix["block-001"]["browser"] is True
    assert matrix["block-001"]["googlebot"] is True
    assert matrix["block-001"]["bingbot"] is False
    assert matrix["block-001"]["layer"] == "server-rendered"  # visible to some crawlers
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_extract.py::test_build_visibility_matrix -v`  
Expected: FAIL with "ImportError: cannot import name 'build_visibility_matrix'"

- [ ] **Step 3: Implement visibility matrix in stages/extract.py**

Add to `stages/extract.py`:

```python
def build_visibility_matrix(
    content_blocks: list[ContentBlock],
    browser_html: str,
    crawler_htmls: dict[str, str]
) -> dict:
    """Build visibility matrix showing which agents can see which content blocks."""
    matrix = {}
    
    for block in content_blocks:
        block_content = block.content
        
        visibility = {
            "browser": block_content in browser_html
        }
        
        # Check each crawler
        for agent_name, html in crawler_htmls.items():
            visibility[agent_name] = block_content in html
        
        # Determine visibility layer
        crawler_count = sum(1 for k, v in visibility.items() if k != "browser" and v)
        
        if visibility["browser"] and crawler_count == len(crawler_htmls):
            layer = "server-rendered"
        elif visibility["browser"] and crawler_count == 0:
            layer = "js-rendered-only"
        elif not visibility["browser"] and crawler_count > 0:
            layer = "schema-only"
        elif visibility["browser"] and crawler_count > 0:
            layer = "server-rendered"  # Some crawlers see it
        else:
            layer = "absent"
        
        visibility["layer"] = layer
        matrix[block.id] = visibility
    
    return matrix
```

Update `stage_3_extract` to build visibility matrix:

```python
def stage_3_extract(context: AuditContext) -> AuditContext:
    """Stage 3: Extract content blocks and structured data."""
    # ... existing code ...
    
    # Build visibility matrix
    crawler_htmls = {
        agent: result.body
        for agent, result in context.fetch_results.items()
        if agent != "browser"
    }
    
    context.visibility_matrix = build_visibility_matrix(
        context.content_blocks,
        context.browser_html,
        crawler_htmls
    )
    
    return context
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_extract.py -v`  
Expected: PASS (all tests)

- [ ] **Step 5: Commit**

```bash
git add stages/extract.py tests/test_extract.py
git commit -m "feat(stage3): visibility matrix for content blocks"
```

---

## Task 10: Product Category Classification

**Files:**
- Create: `stages/classify.py`
- Create: `tests/test_classify.py`

- [ ] **Step 1: Write failing test for classification**

Create `tests/test_classify.py`:

```python
import pytest
from unittest.mock import patch, Mock
from stages.classify import classify_product_category

def test_classify_product_category():
    with patch('openai.OpenAI') as mock_openai:
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '{"category": "chemical_reagent", "confidence": 0.95}'
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        result = classify_product_category(
            product_name="Sodium Chloride",
            description="High purity NaCl",
            schema_type="Product"
        )
        
        assert result["category"] == "chemical_reagent"
        assert result["confidence"] == 0.95
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_classify.py -v`  
Expected: FAIL with "ImportError: cannot import name 'classify_product_category'"

- [ ] **Step 3: Implement stages/classify.py**

Create `stages/classify.py`:

```python
import os
import json
from openai import OpenAI

CATEGORIES = [
    "chemical_reagent",
    "cell_culture_media",
    "laboratory_consumable",
    "analytical_instrument",
    "antibody",
    "other"
]

def classify_product_category(
    product_name: str,
    description: str,
    schema_type: str
) -> dict:
    """Classify product into category using LLM."""
    api_key = os.getenv("CLASSIFIER_API_KEY") or os.getenv("OPENAI_API_KEY")
    model = os.getenv("CLASSIFIER_MODEL", "gpt-4o-mini")
    
    if not api_key:
        return {"category": "other", "confidence": 0.0}
    
    client = OpenAI(api_key=api_key)
    
    prompt = f"""Classify this product into ONE category:
- chemical_reagent
- cell_culture_media
- laboratory_consumable
- analytical_instrument
- antibody
- other

Product: {product_name}
Description: {description[:500]}
Schema type: {schema_type}

Return JSON: {{"category": "...", "confidence": 0.0-1.0}}"""
    
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    
    try:
        result = json.loads(response.choices[0].message.content)
        return result
    except (json.JSONDecodeError, KeyError):
        return {"category": "other", "confidence": 0.0}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_classify.py -v`  
Expected: PASS

- [ ] **Step 5: Add to stage_3_extract**

Modify `stages/extract.py`:

```python
from stages.classify import classify_product_category

def stage_3_extract(context: AuditContext) -> AuditContext:
    """Stage 3: Extract content blocks and structured data."""
    # ... existing code ...
    
    # Classify product category
    if context.product_schema:
        classification = classify_product_category(
            product_name=context.product_schema.get("name", ""),
            description=context.product_schema.get("description", ""),
            schema_type=context.product_schema.get("@type", "")
        )
        context.product_category = classification.get("category", "other")
        context.category_confidence = classification.get("confidence", 0.0)
    
    return context
```

- [ ] **Step 6: Commit**

```bash
git add stages/classify.py tests/test_classify.py stages/extract.py
git commit -m "feat(stage3): product category classification"
```

---

## Task 11: Crawler Coverage Scoring

**Files:**
- Create: `stages/scoring.py`
- Create: `tests/test_scoring.py`

- [ ] **Step 1: Write failing test for coverage scoring**

Create `tests/test_scoring.py`:

```python
import pytest
from stages.scoring import score_crawler_coverage

def test_score_crawler_coverage():
    visibility_matrix = {
        "block-001": {
            "browser": True,
            "googlebot": True,
            "bingbot": True,
            "layer": "server-rendered"
        },
        "block-002": {
            "browser": True,
            "googlebot": False,
            "bingbot": False,
            "layer": "js-rendered-only"
        }
    }
    
    content_blocks = [
        Mock(id="block-001", type="product_id"),
        Mock(id="block-002", type="description")
    ]
    
    weights = {
        "product_id": 0.5,
        "description": 0.5
    }
    
    scores = score_crawler_coverage(visibility_matrix, content_blocks, weights)
    
    assert "googlebot" in scores
    assert scores["googlebot"] == 50.0  # Only sees product_id (50% weight)
    assert scores["bingbot"] == 50.0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_scoring.py -v`  
Expected: FAIL with "ImportError: cannot import name 'score_crawler_coverage'"

- [ ] **Step 3: Implement stages/scoring.py**

Create `stages/scoring.py`:

```python
from core.context import ContentBlock

def score_crawler_coverage(
    visibility_matrix: dict,
    content_blocks: list[ContentBlock],
    weights: dict
) -> dict[str, float]:
    """Score crawler coverage based on visibility of weighted content blocks."""
    # Build block type map
    block_types = {block.id: block.type for block in content_blocks}
    
    # Get all crawler names (exclude "browser" and "layer")
    all_keys = set()
    for block_vis in visibility_matrix.values():
        all_keys.update(block_vis.keys())
    
    crawler_names = [k for k in all_keys if k not in ["browser", "layer"]]
    
    # Score each crawler
    scores = {}
    
    for crawler in crawler_names:
        total_weight = 0.0
        matched_weight = 0.0
        
        for block_id, visibility in visibility_matrix.items():
            block_type = block_types.get(block_id)
            weight = weights.get(block_type, 0.0)
            
            total_weight += weight
            if visibility.get(crawler, False):
                matched_weight += weight
        
        if total_weight > 0:
            scores[crawler] = (matched_weight / total_weight) * 100
        else:
            scores[crawler] = 0.0
    
    return scores
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_scoring.py -v`  
Expected: PASS

- [ ] **Step 5: Add to stage_3_extract**

Modify `stages/extract.py`:

```python
from stages.scoring import score_crawler_coverage

def stage_3_extract(context: AuditContext) -> AuditContext:
    """Stage 3: Extract content blocks and structured data."""
    # ... existing code ...
    
    # Score crawler coverage
    coverage_weights = context.config.get("coverage_weights", {})
    context.crawler_coverage_scores = score_crawler_coverage(
        context.visibility_matrix,
        context.content_blocks,
        coverage_weights
    )
    
    return context
```

- [ ] **Step 6: Commit**

```bash
git add stages/scoring.py tests/test_scoring.py stages/extract.py
git commit -m "feat(stage3): crawler coverage scoring"
```

---

## Task 12: Prompt Templates

**Files:**
- Create: `prompts/templates.yaml`

- [ ] **Step 1: Create prompt templates**

Create `prompts/templates.yaml`:

```yaml
specificity:
  question: "What is unique about this specific product that cannot be inferred from general knowledge?"
  template: |
    Describe {product_name} (catalog {product_id}). Focus on what makes this specific product distinct from general knowledge about {category} products.
    
    URL: {url}

entity_understanding:
  question: "Can you distinguish this product from similar ones?"
  template: |
    I'm deciding between {product_name} (catalog {product_id}) and these alternatives:
    {sibling_list}
    
    What are the key differences? Which should I choose for {use_case}?
    
    URL: {url}

workflow_understanding:
  question: "When should a researcher use this product? Any contraindications?"
  template: |
    I'm planning to use {product_name} for {typical_application}. Is this the right choice? 
    
    Are there any conditions where I should NOT use this product? Any contraindications or limitations I should know about?
    
    URL: {url}

evidence_trust:
  question: "Can you provide specific, verifiable facts about this product?"
  template: |
    Give me 5 specific, verifiable facts about {product_name} that I can confirm on the product page. Include storage conditions, specifications, or regulatory information.
    
    For each fact, cite the source on the page where I can verify it.
    
    URL: {url}

comparison_selection:
  question: "Can you recommend the correct variant for a stated need?"
  template: |
    I need a {category} with the following requirements:
    {requirements}
    
    Should I use {product_name} (catalog {product_id}) or one of the alternatives you know about? Explain your recommendation.
    
    URL: {url}

commercial_bridge:
  question: "Can you complete the journey from need to purchase?"
  template: |
    I want to order {product_name}. What's the correct catalog number and where can I buy it?
    
    Provide specific ordering information including price if available.
    
    URL: {url}
```

- [ ] **Step 2: Commit**

```bash
git add prompts/templates.yaml
git commit -m "feat(stage4): prompt templates for 6 dimensions"
```

---

## Task 13: Reference Facts Generation

**Files:**
- Create: `stages/prompts.py`
- Create: `tests/test_prompts.py`

- [ ] **Step 1: Write failing test for reference facts**

Create `tests/test_prompts.py`:

```python
import pytest
from stages.prompts import generate_reference_facts

def test_generate_reference_facts():
    product_schema = {
        "@type": "Product",
        "name": "Test Product",
        "sku": "TEST-001",
        "description": "A test product",
        "offers": {
            "price": "299.00",
            "priceCurrency": "USD",
            "availability": "InStock"
        }
    }
    
    content_blocks = [
        Mock(type="storage_temp", content="-20°C"),
        Mock(type="purity", content="99.5%")
    ]
    
    category = "chemical_reagent"
    
    facts = generate_reference_facts(product_schema, content_blocks, category)
    
    assert "core" in facts
    assert facts["core"]["product_id"] == "TEST-001"
    assert facts["core"]["product_name"] == "Test Product"
    assert "commercial" in facts
    assert facts["commercial"]["price"] == "299.00"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_prompts.py -v`  
Expected: FAIL with "ImportError: cannot import name 'generate_reference_facts'"

- [ ] **Step 3: Implement stages/prompts.py (reference facts)**

Create `stages/prompts.py`:

```python
from core.context import ContentBlock

def generate_reference_facts(
    product_schema: dict,
    content_blocks: list[ContentBlock],
    category: str
) -> dict:
    """Generate reference facts from product schema and content blocks."""
    facts = {
        "core": {
            "product_id": product_schema.get("sku", ""),
            "product_name": product_schema.get("name", ""),
            "canonical_url": product_schema.get("url", "")
        }
    }
    
    # Category-specific facts
    if category == "chemical_reagent":
        facts["chemical"] = {}
        for field in ["molecular_weight", "cas_number", "purity", "formula"]:
            block = next((b for b in content_blocks if b.type == field), None)
            if block:
                facts["chemical"][field] = block.content
    
    elif category == "cell_culture_media":
        facts["culture"] = {}
        for field in ["storage_temp", "sterility", "supplements", "shelf_life"]:
            block = next((b for b in content_blocks if b.type == field), None)
            if block:
                facts["culture"][field] = block.content
    
    elif category == "laboratory_consumable":
        facts["consumable"] = {}
        for field in ["material", "dimensions", "packaging_quantity", "autoclavable"]:
            block = next((b for b in content_blocks if b.type == field), None)
            if block:
                facts["consumable"][field] = block.content
    
    elif category == "antibody":
        facts["antibody"] = {}
        for field in ["host_species", "clonality", "target_species", "applications"]:
            block = next((b for b in content_blocks if b.type == field), None)
            if block:
                facts["antibody"][field] = block.content
    
    # Common fields
    storage_block = next((b for b in content_blocks if b.type == "storage_temp"), None)
    if storage_block:
        facts.setdefault(category, {})["storage_temp"] = storage_block.content
    
    # Commercial info from schema
    if product_schema.get("offers"):
        offers = product_schema["offers"]
        facts["commercial"] = {
            "price": offers.get("price"),
            "currency": offers.get("priceCurrency"),
            "availability": offers.get("availability")
        }
    
    return facts
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_prompts.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add stages/prompts.py tests/test_prompts.py
git commit -m "feat(stage4): unbranded prompt construction"
```

---

## Task 16: Dual-Mode Agent API Integration

**Files:**
- Create: `agents/client.py`
- Create: `tests/test_agent_client.py`

- [ ] **Step 1: Write failing test for dual-mode agent calls**

Create `tests/test_agent_client.py`:

```python
import pytest
from unittest.mock import AsyncMock, patch
from agents.client import AgentClient, ModelConfig

@pytest.mark.asyncio
async def test_call_agent_training_mode():
    client = AgentClient()
    model = ModelConfig(name="gpt-4o", provider="openai", tier="flagship")
    
    with patch('openai.AsyncOpenAI') as mock_openai:
        mock_completion = AsyncMock()
        mock_completion.choices = [AsyncMock(message=AsyncMock(content="Training response"))]
        mock_openai.return_value.chat.completions.create = AsyncMock(return_value=mock_completion)
        
        response = await client.call_agent(
            agent="openai",
            model=model,
            prompt="Test prompt",
            mode="training"
        )
        
        assert response.text == "Training response"
        assert response.mode == "training"
        assert response.tool_calls == []

@pytest.mark.asyncio
async def test_call_agent_live_mode():
    client = AgentClient()
    model = ModelConfig(name="gpt-4o", provider="openai", tier="flagship")
    
    with patch('openai.AsyncOpenAI') as mock_openai:
        mock_completion = AsyncMock()
        mock_completion.choices = [AsyncMock(
            message=AsyncMock(
                content="Live response",
                tool_calls=[
                    AsyncMock(function=AsyncMock(name="web_search", arguments='{"query":"test"}'))
                ]
            )
        )]
        mock_openai.return_value.chat.completions.create = AsyncMock(return_value=mock_completion)
        
        response = await client.call_agent(
            agent="openai",
            model=model,
            prompt="Test prompt",
            mode="live"
        )
        
        assert response.text == "Live response"
        assert response.mode == "live"
        assert len(response.tool_calls) > 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_agent_client.py -v`  
Expected: FAIL with "ImportError: cannot import name 'AgentClient'"

- [ ] **Step 3: Implement agents/client.py**

Create `agents/client.py`:

```python
import os
import asyncio
from dataclasses import dataclass
from typing import Literal
import httpx
import openai
import anthropic
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

@dataclass
class ModelConfig:
    name: str
    provider: str
    tier: str

@dataclass
class AgentResponse:
    text: str
    mode: Literal["training", "live"]
    tool_calls: list[dict]
    retrieved_urls: list[str]
    cost_usd: float

class AgentClient:
    """Client for calling AI agents in training and live modes."""
    
    def __init__(self):
        self.openai_client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.anthropic_client = anthropic.AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.perplexity_key = os.getenv("PERPLEXITY_API_KEY")
    
    async def call_agent(
        self,
        agent: str,
        model: ModelConfig,
        prompt: str,
        mode: Literal["training", "live"]
    ) -> AgentResponse:
        """Call agent in specified mode."""
        if agent == "openai":
            return await self._call_openai(model, prompt, mode)
        elif agent == "anthropic":
            return await self._call_anthropic(model, prompt, mode)
        elif agent == "google":
            return await self._call_google(model, prompt, mode)
        elif agent == "perplexity":
            return await self._call_perplexity(model, prompt)  # Always live
        elif agent == "bing":
            return await self._call_bing(model, prompt, mode)
        else:
            raise ValueError(f"Unknown agent: {agent}")
    
    async def _call_openai(
        self,
        model: ModelConfig,
        prompt: str,
        mode: Literal["training", "live"]
    ) -> AgentResponse:
        """Call OpenAI API."""
        messages = [{"role": "user", "content": prompt}]
        
        if mode == "training":
            # No tools - training data only
            completion = await self.openai_client.chat.completions.create(
                model=model.name,
                messages=messages
            )
            return AgentResponse(
                text=completion.choices[0].message.content,
                mode="training",
                tool_calls=[],
                retrieved_urls=[],
                cost_usd=self._estimate_openai_cost(model.name, completion.usage)
            )
        else:
            # With web search tools
            tools = [{
                "type": "function",
                "function": {
                    "name": "web_search",
                    "description": "Search the web",
                    "parameters": {
                        "type": "object",
                        "properties": {"query": {"type": "string"}},
                        "required": ["query"]
                    }
                }
            }]
            
            completion = await self.openai_client.chat.completions.create(
                model=model.name,
                messages=messages,
                tools=tools
            )
            
            tool_calls = []
            retrieved_urls = []
            message = completion.choices[0].message
            
            if message.tool_calls:
                tool_calls = [
                    {"name": tc.function.name, "arguments": tc.function.arguments}
                    for tc in message.tool_calls
                ]
            
            return AgentResponse(
                text=message.content or "",
                mode="live",
                tool_calls=tool_calls,
                retrieved_urls=retrieved_urls,
                cost_usd=self._estimate_openai_cost(model.name, completion.usage)
            )
    
    async def _call_anthropic(
        self,
        model: ModelConfig,
        prompt: str,
        mode: Literal["training", "live"]
    ) -> AgentResponse:
        """Call Anthropic API."""
        if mode == "training":
            # No tools
            message = await self.anthropic_client.messages.create(
                model=model.name,
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}]
            )
            return AgentResponse(
                text=message.content[0].text,
                mode="training",
                tool_calls=[],
                retrieved_urls=[],
                cost_usd=self._estimate_anthropic_cost(model.name, message.usage)
            )
        else:
            # With web search tools
            tools = [{
                "name": "web_search",
                "description": "Search the web",
                "input_schema": {
                    "type": "object",
                    "properties": {"query": {"type": "string"}},
                    "required": ["query"]
                }
            }]
            
            message = await self.anthropic_client.messages.create(
                model=model.name,
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}],
                tools=tools
            )
            
            tool_calls = []
            if message.stop_reason == "tool_use":
                for block in message.content:
                    if block.type == "tool_use":
                        tool_calls.append({"name": block.name, "input": block.input})
            
            text = "".join(block.text for block in message.content if hasattr(block, "text"))
            
            return AgentResponse(
                text=text,
                mode="live",
                tool_calls=tool_calls,
                retrieved_urls=[],
                cost_usd=self._estimate_anthropic_cost(model.name, message.usage)
            )
    
    async def _call_google(
        self,
        model: ModelConfig,
        prompt: str,
        mode: Literal["training", "live"]
    ) -> AgentResponse:
        """Call Google Gemini API."""
        gm = genai.GenerativeModel(
            model_name=model.name,
            safety_settings={
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
        )
        
        if mode == "training":
            # Disable grounding
            response = await gm.generate_content_async(prompt)
            return AgentResponse(
                text=response.text,
                mode="training",
                tool_calls=[],
                retrieved_urls=[],
                cost_usd=0.0  # Estimate separately
            )
        else:
            # With Google Search grounding
            response = await gm.generate_content_async(
                prompt,
                tools="google_search_retrieval"
            )
            
            # Extract grounding metadata
            retrieved_urls = []
            if hasattr(response, "grounding_metadata") and response.grounding_metadata:
                for chunk in response.grounding_metadata.grounding_chunks:
                    if hasattr(chunk, "web") and chunk.web.uri:
                        retrieved_urls.append(chunk.web.uri)
            
            return AgentResponse(
                text=response.text,
                mode="live",
                tool_calls=[],  # Gemini uses grounding metadata, not tool calls
                retrieved_urls=retrieved_urls,
                cost_usd=0.0
            )
    
    async def _call_perplexity(
        self,
        model: ModelConfig,
        prompt: str
    ) -> AgentResponse:
        """Call Perplexity API - always live mode."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.perplexity.ai/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.perplexity_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model.name,
                    "messages": [{"role": "user", "content": prompt}]
                },
                timeout=60.0
            )
            data = response.json()
            
            # Extract citations
            retrieved_urls = []
            if "citations" in data:
                retrieved_urls = data["citations"]
            
            return AgentResponse(
                text=data["choices"][0]["message"]["content"],
                mode="live",
                tool_calls=[],
                retrieved_urls=retrieved_urls,
                cost_usd=0.0
            )
    
    async def _call_bing(
        self,
        model: ModelConfig,
        prompt: str,
        mode: Literal["training", "live"]
    ) -> AgentResponse:
        """Call Azure OpenAI with optional Bing grounding."""
        # Azure OpenAI setup
        azure_client = openai.AsyncAzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version="2024-02-01",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        
        messages = [{"role": "user", "content": prompt}]
        
        if mode == "training":
            # No grounding
            completion = await azure_client.chat.completions.create(
                model=model.name,
                messages=messages
            )
            return AgentResponse(
                text=completion.choices[0].message.content,
                mode="training",
                tool_calls=[],
                retrieved_urls=[],
                cost_usd=self._estimate_openai_cost(model.name, completion.usage)
            )
        else:
            # With Bing Search grounding
            data_sources = [{
                "type": "bing_search",
                "parameters": {"endpoint": os.getenv("BING_SEARCH_ENDPOINT")}
            }]
            
            completion = await azure_client.chat.completions.create(
                model=model.name,
                messages=messages,
                extra_body={"data_sources": data_sources}
            )
            
            # Extract Bing grounding metadata
            retrieved_urls = []
            message = completion.choices[0].message
            if hasattr(message, "context") and message.context:
                for citation in message.context.get("citations", []):
                    retrieved_urls.append(citation.get("url", ""))
            
            return AgentResponse(
                text=message.content,
                mode="live",
                tool_calls=[],
                retrieved_urls=retrieved_urls,
                cost_usd=self._estimate_openai_cost(model.name, completion.usage)
            )
    
    def _estimate_openai_cost(self, model: str, usage) -> float:
        """Estimate OpenAI API cost."""
        # Simplified pricing (update with real pricing)
        if "gpt-4o" in model:
            input_cost = 0.005  # per 1K tokens
            output_cost = 0.015
        elif "o3-mini" in model:
            input_cost = 0.01
            output_cost = 0.03
        else:
            input_cost = 0.001
            output_cost = 0.002
        
        total = (usage.prompt_tokens / 1000 * input_cost) + (usage.completion_tokens / 1000 * output_cost)
        return round(total, 4)
    
    def _estimate_anthropic_cost(self, model: str, usage) -> float:
        """Estimate Anthropic API cost."""
        if "opus" in model:
            input_cost = 0.015
            output_cost = 0.075
        elif "sonnet" in model:
            input_cost = 0.003
            output_cost = 0.015
        else:
            input_cost = 0.00025
            output_cost = 0.00125
        
        total = (usage.input_tokens / 1000 * input_cost) + (usage.output_tokens / 1000 * output_cost)
        return round(total, 4)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_agent_client.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add agents/client.py tests/test_agent_client.py
git commit -m "feat(stage4): dual-mode agent API client"
```

---

## Task 17: Retrieval Analysis Extraction

**Files:**
- Create: `stages/retrieval_analysis.py`
- Create: `tests/test_retrieval_analysis.py`

- [ ] **Step 1: Write failing test for retrieval analysis**

Create `tests/test_retrieval_analysis.py`:

```python
import pytest
from stages.retrieval_analysis import analyze_retrieval, extract_content_from_response
from core.context import RetrievalAnalysis
from agents.client import AgentResponse

def test_extract_content_from_response():
    response = AgentResponse(
        text="The product costs $299 and is stored at -20°C.",
        mode="live",
        tool_calls=[{"name": "web_search", "arguments": '{"query":"test"}'}],
        retrieved_urls=["https://example.com/product/test"],
        cost_usd=0.05
    )
    
    content = extract_content_from_response(response, "https://example.com/product/test")
    assert len(content) > 0
    assert "299" in content or "20" in content

def test_analyze_retrieval_target_found():
    target_url = "https://example.com/product/test"
    response = AgentResponse(
        text="The product costs $299.",
        mode="live",
        tool_calls=[],
        retrieved_urls=[target_url, "https://competitor.com/product"],
        cost_usd=0.05
    )
    
    reference_facts = {
        "commercial": {"price": "299.00", "currency": "USD"}
    }
    
    analysis = analyze_retrieval(response, target_url, reference_facts)
    
    assert analysis.retrieved_target is True
    assert analysis.target_url_rank == 1
    assert analysis.extraction_quality > 0.0

def test_analyze_retrieval_target_not_found():
    response = AgentResponse(
        text="Generic response.",
        mode="live",
        tool_calls=[],
        retrieved_urls=["https://competitor.com/product"],
        cost_usd=0.05
    )
    
    analysis = analyze_retrieval(response, "https://example.com/product/test", {})
    
    assert analysis.retrieved_target is False
    assert analysis.target_url_rank is None
    assert analysis.usage_classification == "ignored"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_retrieval_analysis.py -v`  
Expected: FAIL with "ImportError: cannot import name 'analyze_retrieval'"

- [ ] **Step 3: Implement stages/retrieval_analysis.py**

Create `stages/retrieval_analysis.py`:

```python
from core.context import RetrievalAnalysis
from agents.client import AgentResponse
from difflib import SequenceMatcher

def extract_content_from_response(response: AgentResponse, target_url: str) -> str:
    """Extract content that came from target URL."""
    # Simple heuristic: if URL retrieved, assume response contains extracted content
    if target_url in response.retrieved_urls:
        return response.text
    return ""

def calculate_extraction_quality(
    extracted_content: str,
    reference_facts: dict
) -> float:
    """Calculate how much of reference facts were extracted (0.0-1.0)."""
    if not extracted_content:
        return 0.0
    
    # Flatten reference facts to list of values
    fact_values = []
    for category_dict in reference_facts.values():
        if isinstance(category_dict, dict):
            fact_values.extend(str(v) for v in category_dict.values() if v)
    
    if not fact_values:
        return 0.0
    
    # Check how many facts appear in extracted content
    matched = 0
    for fact in fact_values:
        fact_str = str(fact).lower()
        if fact_str in extracted_content.lower():
            matched += 1
    
    return round(matched / len(fact_values), 2)

def calculate_usage_ratio(response_text: str, extracted_content: str) -> float:
    """Calculate what fraction of extracted content was used in final response."""
    if not extracted_content:
        return 0.0
    
    # Use sequence matching to estimate content overlap
    matcher = SequenceMatcher(None, extracted_content.lower(), response_text.lower())
    ratio = matcher.ratio()
    return round(ratio, 2)

def classify_usage(
    retrieved: bool,
    extraction_quality: float,
    usage_ratio: float,
    content_used: bool
) -> str:
    """Classify how agent used retrieved content."""
    if not retrieved:
        return "ignored"
    
    if not content_used or usage_ratio < 0.1:
        return "ignored"
    
    if usage_ratio > 0.7:
        return "primary_source"
    elif usage_ratio > 0.3:
        return "supporting"
    else:
        return "contradicted"

def determine_not_used_reason(
    usage_classification: str,
    extraction_quality: float
) -> str | None:
    """Determine why content wasn't used."""
    if usage_classification != "ignored":
        return None
    
    if extraction_quality < 0.3:
        return "parsing_failure"
    
    return "deemed_irrelevant"

def analyze_retrieval(
    response: AgentResponse,
    target_url: str,
    reference_facts: dict
) -> RetrievalAnalysis:
    """Analyze retrieval behavior from agent response."""
    # Check if target was retrieved
    retrieved_target = target_url in response.retrieved_urls
    
    # Get target rank
    target_rank = None
    if retrieved_target:
        target_rank = response.retrieved_urls.index(target_url) + 1
    
    # Extract content from target
    extracted_content = extract_content_from_response(response, target_url)
    
    # Calculate extraction quality
    extraction_quality = calculate_extraction_quality(extracted_content, reference_facts)
    
    # Check if content was used
    content_used = len(extracted_content) > 0 and extracted_content.lower() in response.text.lower()
    
    # Calculate usage ratio
    usage_ratio = calculate_usage_ratio(response.text, extracted_content)
    
    # Classify usage
    usage_classification = classify_usage(
        retrieved_target,
        extraction_quality,
        usage_ratio,
        content_used
    )
    
    # Determine why not used
    not_used_reason = determine_not_used_reason(usage_classification, extraction_quality)
    
    return RetrievalAnalysis(
        retrieved_target=retrieved_target,
        retrieved_urls=response.retrieved_urls,
        target_url_rank=target_rank,
        extracted_content=extracted_content[:500],  # Truncate for storage
        extraction_quality=extraction_quality,
        content_used_in_response=content_used,
        content_usage_ratio=usage_ratio,
        usage_classification=usage_classification,
        not_used_reason=not_used_reason
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_retrieval_analysis.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add stages/retrieval_analysis.py tests/test_retrieval_analysis.py
git commit -m "feat(stage4): retrieval analysis extraction"
```

---

## Task 18: Traffic Analysis

**Files:**
- Create: `stages/traffic_analysis.py`
- Create: `tests/test_traffic_analysis.py`

- [ ] **Step 1: Write failing test for traffic analysis**

Create `tests/test_traffic_analysis.py`:

```python
import pytest
from stages.traffic_analysis import analyze_traffic, detect_citation_format
from agents.client import AgentResponse

def test_detect_citation_format_prominent():
    text = "You can order from: https://example.com/product/test"
    fmt = detect_citation_format(text, "https://example.com/product/test")
    assert fmt == "prominent_link"

def test_detect_citation_format_footnote():
    text = "The product costs $299. [1]\n\n[1] https://example.com/product/test"
    fmt = detect_citation_format(text, "https://example.com/product/test")
    assert fmt == "footnote"

def test_detect_citation_format_none():
    text = "The product costs $299."
    fmt = detect_citation_format(text, "https://example.com/product/test")
    assert fmt == "none"

def test_analyze_traffic_drives_traffic():
    response = AgentResponse(
        text="You can order from: https://example.com/product/test",
        mode="live",
        tool_calls=[],
        retrieved_urls=["https://example.com/product/test"],
        cost_usd=0.05
    )
    
    analysis = analyze_traffic(response, "https://example.com/product/test", "example.com")
    
    assert analysis.cited_target is True
    assert analysis.citation_format == "prominent_link"
    assert analysis.traffic_verdict == "drives_traffic"
    assert analysis.click_likelihood > 0.5

def test_analyze_traffic_diverts_traffic():
    response = AgentResponse(
        text="You can order from: https://competitor.com/product/similar",
        mode="live",
        tool_calls=[],
        retrieved_urls=["https://example.com/product/test", "https://competitor.com/product/similar"],
        cost_usd=0.05
    )
    
    analysis = analyze_traffic(response, "https://example.com/product/test", "example.com")
    
    assert analysis.cited_competitor is True
    assert analysis.traffic_verdict == "diverts_traffic"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_traffic_analysis.py -v`  
Expected: FAIL with "ImportError: cannot import name 'analyze_traffic'"

- [ ] **Step 3: Implement stages/traffic_analysis.py**

Create `stages/traffic_analysis.py`:

```python
import re
from urllib.parse import urlparse
from core.context import TrafficAnalysis
from agents.client import AgentResponse

def detect_citation_format(text: str, target_url: str) -> str:
    """Detect how URL is cited in response."""
    if target_url not in text:
        return "none"
    
    # Check if URL is in a prominent position (first 100 chars)
    if text.find(target_url) < 100:
        return "prominent_link"
    
    # Check for footnote pattern [N] followed by URL later
    if re.search(r'\[\d+\].*?' + re.escape(target_url), text, re.DOTALL):
        return "footnote"
    
    # Check if inline (within sentence)
    url_pos = text.find(target_url)
    context = text[max(0, url_pos-50):min(len(text), url_pos+len(target_url)+50)]
    if re.search(r'\w.*?' + re.escape(target_url) + r'.*?\w', context):
        return "inline"
    
    return "footnote"

def calculate_click_likelihood(citation_format: str, placement: str) -> float:
    """Estimate likelihood user will click citation."""
    if citation_format == "none":
        return 0.0
    elif citation_format == "prominent_link":
        return 0.9
    elif citation_format == "inline":
        return 0.7
    elif citation_format == "footnote":
        return 0.3
    return 0.5

def detect_competitors(retrieved_urls: list[str], target_domain: str) -> list[str]:
    """Detect competitor product pages from retrieved URLs."""
    competitors = []
    
    for url in retrieved_urls:
        domain = urlparse(url).netloc
        
        # Skip target domain
        if domain == target_domain:
            continue
        
        # Skip generic sources
        generic_sources = ["wikipedia.org", "protocols.io", "nih.gov", "pubmed.gov"]
        if any(gs in domain for gs in generic_sources):
            continue
        
        # Check if URL looks like product page
        if "/product/" in url or "/catalog/" in url or "/item/" in url:
            competitors.append(url)
    
    return competitors

def determine_traffic_verdict(
    cited_target: bool,
    answered_without_citation: bool,
    cited_competitor: bool
) -> str:
    """Determine traffic impact verdict."""
    if cited_target and not cited_competitor:
        return "drives_traffic"
    elif cited_competitor and not cited_target:
        return "diverts_traffic"
    elif answered_without_citation:
        return "no_traffic"
    else:
        return "neutral"

def analyze_traffic(
    response: AgentResponse,
    target_url: str,
    target_domain: str
) -> TrafficAnalysis:
    """Analyze traffic impact from agent response."""
    # Detect citation
    cited_target = target_url in response.text
    citation_format = detect_citation_format(response.text, target_url)
    
    # Determine placement
    if citation_format == "none":
        citation_placement = "none"
    else:
        url_pos = response.text.find(target_url)
        if url_pos < len(response.text) / 3:
            citation_placement = "beginning"
        elif url_pos < 2 * len(response.text) / 3:
            citation_placement = "middle"
        else:
            citation_placement = "end"
    
    # Calculate click likelihood
    click_likelihood = calculate_click_likelihood(citation_format, citation_placement)
    
    # Check if answered without citation
    answered_without_citation = len(response.text) > 100 and not cited_target
    
    # Detect competitors
    competitor_urls = detect_competitors(response.retrieved_urls, target_domain)
    cited_competitor = any(comp_url in response.text for comp_url in competitor_urls)
    
    # Determine verdict
    traffic_verdict = determine_traffic_verdict(
        cited_target,
        answered_without_citation,
        cited_competitor
    )
    
    # Assess business impact
    if traffic_verdict == "drives_traffic":
        business_impact = "positive"
    elif traffic_verdict == "diverts_traffic":
        business_impact = "negative_high"
    elif traffic_verdict == "no_traffic":
        business_impact = "negative_medium"
    else:
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_traffic_analysis.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add stages/traffic_analysis.py tests/test_traffic_analysis.py
git commit -m "feat(stage4): traffic impact analysis"
```

---

## Task 19: Auto-Competitor Discovery

**Files:**
- Create: `stages/competitor_discovery.py`
- Create: `tests/test_competitor_discovery.py`

- [ ] **Step 1: Write failing test for competitor discovery**

Create `tests/test_competitor_discovery.py`:

```python
import pytest
from stages.competitor_discovery import classify_url, discover_competitors_from_responses
from core.context import CompetitorAnalysis

def test_classify_url_product_page():
    classification = classify_url("https://competitor.com/product/xyz-123", "example.com")
    assert classification == "competitor"

def test_classify_url_generic_source():
    classification = classify_url("https://wikipedia.org/wiki/Cell_culture", "example.com")
    assert classification == "generic_source"

def test_classify_url_target_domain():
    classification = classify_url("https://example.com/product/test", "example.com")
    assert classification == "target"

def test_discover_competitors_from_responses():
    responses = {
        "agent1": [
            {"retrieved_urls": ["https://competitor.com/product/x", "https://wikipedia.org/wiki/test"]},
            {"retrieved_urls": ["https://competitor.com/product/y"]}
        ]
    }
    
    competitors = discover_competitors_from_responses(responses, "example.com")
    
    assert len(competitors) > 0
    assert any(c.url == "https://competitor.com/product/x" for c in competitors)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_competitor_discovery.py -v`  
Expected: FAIL with "ImportError: cannot import name 'classify_url'"

- [ ] **Step 3: Implement stages/competitor_discovery.py**

Create `stages/competitor_discovery.py`:

```python
from urllib.parse import urlparse
from collections import Counter
from core.context import CompetitorAnalysis

GENERIC_SOURCES = [
    "wikipedia.org", "protocols.io", "nih.gov", "pubmed.gov",
    "ncbi.nlm.nih.gov", "sciencedirect.com", "nature.com", "springer.com",
    "addgene.org", "atcc.org", "thermofisher.com"  # Known generic databases
]

def classify_url(url: str, target_domain: str) -> str:
    """Classify URL as target, competitor, or generic source."""
    domain = urlparse(url).netloc
    
    # Check if target domain
    if domain == target_domain:
        return "target"
    
    # Check if generic source
    for generic in GENERIC_SOURCES:
        if generic in domain:
            return "generic_source"
    
    # Check if looks like product page
    product_indicators = ["/product/", "/catalog/", "/item/", "/sku/", "/p/"]
    if any(indicator in url.lower() for indicator in product_indicators):
        return "competitor"
    
    return "generic_source"

def discover_competitors_from_responses(
    responses_by_agent: dict[str, list[dict]],
    target_domain: str
) -> list[CompetitorAnalysis]:
    """Auto-discover competitors from cited URLs across all responses."""
    # Collect all competitor URLs
    competitor_urls = []
    
    for agent_name, agent_responses in responses_by_agent.items():
        for response_data in agent_responses:
            retrieved_urls = response_data.get("retrieved_urls", [])
            
            for url in retrieved_urls:
                classification = classify_url(url, target_domain)
                if classification == "competitor":
                    competitor_urls.append((url, agent_name))
    
    # Count citations per competitor
    url_counter = Counter(url for url, _ in competitor_urls)
    
    # Build competitor analysis
    competitors = []
    for url, citation_count in url_counter.items():
        domain = urlparse(url).netloc
        
        # Find which agents cited this competitor
        citing_agents = [agent for comp_url, agent in competitor_urls if comp_url == url]
        
        competitors.append(CompetitorAnalysis(
            url=url,
            domain=domain,
            citation_count=citation_count,
            citing_agents=list(set(citing_agents)),
            classification="competitor"
        ))
    
    # Sort by citation count descending
    competitors.sort(key=lambda c: c.citation_count, reverse=True)
    
    return competitors
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_competitor_discovery.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add stages/competitor_discovery.py tests/test_competitor_discovery.py
git commit -m "feat(stage4): auto-competitor discovery"
```

---

## Task 20: Content Value Analysis

**Files:**
- Create: `stages/content_value.py`
- Create: `tests/test_content_value.py`

- [ ] **Step 1: Write failing test for content value analysis**

Create `tests/test_content_value.py`:

```python
import pytest
from stages.content_value import calculate_content_value, rank_content_blocks
from core.context import ContentBlockValue

def test_calculate_content_value():
    extraction_rate = 0.8  # 80% of agents extracted this block
    usage_rate = 0.6  # 60% of agents used it in response
    citation_correlation = 0.9  # 90% of agents who cited target used this block
    
    value_score = calculate_content_value(extraction_rate, usage_rate, citation_correlation)
    
    assert value_score > 50  # Should be high value
    assert value_score <= 100

def test_rank_content_blocks():
    blocks_by_type = {
        "product_description": {
            "extracted_by": ["agent1", "agent2", "agent3"],
            "used_in_citations": ["agent1", "agent2"]
        },
        "pricing": {
            "extracted_by": ["agent1"],
            "used_in_citations": []
        }
    }
    
    total_agents = 3
    citing_agents = ["agent1", "agent2"]
    
    rankings = rank_content_blocks(blocks_by_type, total_agents, citing_agents)
    
    assert len(rankings) == 2
    # Product description should rank higher than pricing
    assert rankings[0].block_type == "product_description"
    assert rankings[0].value_tier in ["critical", "high"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_content_value.py -v`  
Expected: FAIL with "ImportError: cannot import name 'calculate_content_value'"

- [ ] **Step 3: Implement stages/content_value.py**

Create `stages/content_value.py`:

```python
from core.context import ContentBlockValue

def calculate_content_value(
    extraction_rate: float,
    usage_rate: float,
    citation_correlation: float
) -> float:
    """Calculate value score 0-100 for content block."""
    # Weighted formula emphasizing citation correlation
    score = (
        extraction_rate * 0.25 +
        usage_rate * 0.35 +
        citation_correlation * 0.40
    ) * 100
    
    return round(score, 1)

def classify_value_tier(value_score: float) -> str:
    """Classify value tier from score."""
    if value_score >= 80:
        return "critical"
    elif value_score >= 60:
        return "high"
    elif value_score >= 40:
        return "medium"
    else:
        return "low"

def rank_content_blocks(
    blocks_by_type: dict[str, dict],
    total_agents: int,
    citing_agents: list[str]
) -> list[ContentBlockValue]:
    """Rank content blocks by value to agents."""
    rankings = []
    
    for block_type, block_data in blocks_by_type.items():
        extracted_by = block_data.get("extracted_by", [])
        used_in_citations = block_data.get("used_in_citations", [])
        
        # Calculate rates
        extraction_rate = len(extracted_by) / total_agents if total_agents > 0 else 0.0
        usage_rate = len(used_in_citations) / len(extracted_by) if extracted_by else 0.0
        
        # Calculate citation correlation
        # What % of citing agents used this block?
        citing_and_using = [a for a in citing_agents if a in used_in_citations]
        citation_correlation = len(citing_and_using) / len(citing_agents) if citing_agents else 0.0
        
        # Calculate value score
        value_score = calculate_content_value(extraction_rate, usage_rate, citation_correlation)
        value_tier = classify_value_tier(value_score)
        
        rankings.append(ContentBlockValue(
            block_type=block_type,
            extracted_by_agents=extracted_by,
            extraction_rate=round(extraction_rate, 2),
            used_in_citations=used_in_citations,
            usage_rate=round(usage_rate, 2),
            citation_correlation_score=round(citation_correlation, 2),
            value_score=value_score,
            value_tier=value_tier
        ))
    
    # Sort by value score descending
    rankings.sort(key=lambda r: r.value_score, reverse=True)
    
    return rankings
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_content_value.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add stages/content_value.py tests/test_content_value.py
git commit -m "feat(stage4): content value analysis and ranking"
```

---

## Task 21: Stage 4 Orchestration

**Files:**
- Create: `stages/stage4.py`
- Create: `tests/test_stage4.py`

- [ ] **Step 1: Write failing test for stage 4 orchestration**

Create `tests/test_stage4.py`:

```python
import pytest
from unittest.mock import AsyncMock, patch
from stages.stage4 import run_stage4
from core.context import AuditContext

@pytest.mark.asyncio
async def test_run_stage4():
    context = AuditContext(url="https://example.com/product/test")
    context.product_category = "cell_culture_media"
    context.content_blocks = [
        {"type": "product_description", "content": "Test product"}
    ]
    
    config = {
        "agents": {
            "openai": {
                "test_training_mode": True,
                "models": [{"name": "gpt-4o", "tier": "flagship"}]
            }
        }
    }
    
    with patch('stages.stage4.AgentClient') as mock_client:
        mock_response = AsyncMock()
        mock_response.text = "Test response"
        mock_response.mode = "training"
        mock_response.tool_calls = []
        mock_response.retrieved_urls = []
        mock_response.cost_usd = 0.05
        
        mock_client.return_value.call_agent = AsyncMock(return_value=mock_response)
        
        context = await run_stage4(context, config)
        
        assert len(context.agent_results) > 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_stage4.py -v`  
Expected: FAIL with "ImportError: cannot import name 'run_stage4'"

- [ ] **Step 3: Implement stages/stage4.py**

Create `stages/stage4.py`:

```python
import asyncio
from core.context import AuditContext, AgentResult
from agents.client import AgentClient, ModelConfig
from stages.prompts import extract_characteristics, build_unbranded_prompts
from stages.retrieval_analysis import analyze_retrieval
from stages.traffic_analysis import analyze_traffic
from stages.scoring import score_response

async def run_stage4(context: AuditContext, config: dict) -> AuditContext:
    """Stage 4: AI agent prompting with dual-mode testing."""
    # Build unbranded prompts
    reference_facts = context.reference_facts
    siblings = context.siblings
    category = context.product_category
    
    prompts = build_unbranded_prompts(
        reference_facts,
        siblings,
        category,
        {},  # templates loaded internally
        pass_threshold=config.get("pass_threshold", 70)
    )
    
    # Initialize agent client
    client = AgentClient()
    
    # Get agent config
    agents_config = config.get("agents", {})
    
    # Collect all agent/model/prompt/mode combinations
    tasks = []
    
    for agent_name, agent_config in agents_config.items():
        if not agent_config.get("enabled", True):
            continue
        
        test_training = agent_config.get("test_training_mode", True)
        models = agent_config.get("models", [])
        
        # Filter to flagship tier for flagship_only mode
        if config.get("testing_scope") == "flagship_only":
            models = [m for m in models if m.get("tier") == "flagship"]
        
        for model_dict in models:
            model = ModelConfig(
                name=model_dict["name"],
                provider=agent_name,
                tier=model_dict.get("tier", "flagship")
            )
            
            for prompt_exec in prompts:
                # Training mode (if enabled for this agent)
                if test_training and agent_name != "perplexity":
                    tasks.append((agent_name, model, prompt_exec, "training"))
                
                # Live mode
                tasks.append((agent_name, model, prompt_exec, "live"))
    
    # Execute all combinations
    results = []
    
    for agent_name, model, prompt_exec, mode in tasks:
        try:
            response = await client.call_agent(
                agent=agent_name,
                model=model,
                prompt=prompt_exec.prompt,
                mode=mode
            )
            
            # Score response
            score = score_response(response.text, reference_facts)
            
            # Analyze retrieval (live mode only)
            retrieval_analysis = None
            traffic_analysis = None
            
            if mode == "live":
                retrieval_analysis = analyze_retrieval(
                    response,
                    context.url,
                    reference_facts
                )
                
                target_domain = context.url.split("/")[2]
                traffic_analysis = analyze_traffic(
                    response,
                    context.url,
                    target_domain
                )
            
            # Create result
            result = AgentResult(
                agent_name=agent_name,
                model_name=model.name,
                prompt_id=prompt_exec.id,
                dimension=prompt_exec.dimension,
                training_response=response.text if mode == "training" else "",
                training_score=score if mode == "training" else 0.0,
                training_hallucinations=[],
                training_evidence_id="",
                live_response=response.text if mode == "live" else "",
                live_score=score if mode == "live" else 0.0,
                live_hallucinations=[],
                live_evidence_id="",
                retrieval_analysis=retrieval_analysis,
                traffic_analysis=traffic_analysis,
                improvement_from_live=0.0  # Calculate after both modes collected
            )
            
            results.append(result)
            
        except Exception as e:
            # Log error and continue
            print(f"Error calling {agent_name}/{model.name} in {mode} mode: {e}")
            continue
    
    context.agent_results = results
    
    return context
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_stage4.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add stages/stage4.py tests/test_stage4.py
git commit -m "feat(stage4): orchestrate dual-mode agent testing"
```

---

## Task 22: Stage 5 Gap Diagnosis

**Files:**
- Create: `stages/stage5.py`
- Create: `tests/test_stage5.py`

- [ ] **Step 1: Write failing test for gap diagnosis**

Create `tests/test_stage5.py`:

```python
import pytest
from stages.stage5 import diagnose_gaps, map_to_fix_category
from core.context import GapEntry, RootCause

def test_map_to_fix_category():
    root_cause = RootCause(
        type="content_gap",
        layer="server-rendered",
        missing_content=["storage_conditions"],
        contributing_factors=[]
    )
    
    fix_category = map_to_fix_category(root_cause)
    assert fix_category == "content_gap"

def test_diagnose_gaps():
    failing_results = [
        {
            "dimension": "specificity",
            "agent": "openai/gpt-4o",
            "score": 45,
            "hallucinations": [{"type": "generic_synthesis"}],
            "retrieval": {"retrieved_target": False}
        }
    ]
    
    context = {"content_blocks": [], "visibility_matrix": {}}
    
    gaps = diagnose_gaps(failing_results, context)
    
    assert len(gaps) > 0
    assert gaps[0].failure_type in ["hallucination", "retrieval_failure"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_stage5.py -v`  
Expected: FAIL with "ImportError: cannot import name 'diagnose_gaps'"

- [ ] **Step 3: Implement stages/stage5.py**

Create `stages/stage5.py`:

```python
from core.context import GapEntry, RootCause, RemediationItem

def map_to_fix_category(root_cause: RootCause) -> str:
    """Map root cause to fix category."""
    if root_cause.type == "content_gap":
        return "content_gap"
    elif root_cause.type == "js_rendering_gap":
        return "js_rendering_gap"
    elif root_cause.type == "infrastructure_gap":
        return "infrastructure_gap"
    elif root_cause.type == "selection_logic_gap":
        return "selection_logic_gap"
    else:
        return "document_format_gap"

def diagnose_single_failure(
    result: dict,
    context: dict
) -> GapEntry:
    """Diagnose single failing agent result."""
    # Simplified diagnosis - check retrieval first
    if not result.get("retrieval", {}).get("retrieved_target"):
        root_cause = RootCause(
            type="retrieval_failure",
            layer="search",
            missing_content=[],
            contributing_factors=["not_in_search_results"]
        )
        
        return GapEntry(
            dimension=result["dimension"],
            agent=result["agent"],
            failure_type="retrieval_failure",
            root_cause=root_cause,
            fix_category="infrastructure_gap",
            evidence_ids=[],
            explanation="Target URL not retrieved by agent search",
            geo_impact="high"
        )
    
    # Check hallucinations
    hallucinations = result.get("hallucinations", [])
    if hallucinations:
        hal_type = hallucinations[0].get("type", "")
        
        root_cause = RootCause(
            type="content_gap",
            layer="server-rendered",
            missing_content=["unknown"],
            contributing_factors=[hal_type]
        )
        
        return GapEntry(
            dimension=result["dimension"],
            agent=result["agent"],
            failure_type="hallucination",
            root_cause=root_cause,
            fix_category="content_gap",
            evidence_ids=[],
            explanation=f"Agent hallucinated: {hal_type}",
            geo_impact="medium"
        )
    
    # Default: low score without clear cause
    root_cause = RootCause(
        type="content_gap",
        layer="server-rendered",
        missing_content=[],
        contributing_factors=["low_quality_response"]
    )
    
    return GapEntry(
        dimension=result["dimension"],
        agent=result["agent"],
        failure_type="low_score",
        root_cause=root_cause,
        fix_category="content_gap",
        evidence_ids=[],
        explanation="Low score without clear root cause",
        geo_impact="low"
    )

def diagnose_gaps(
    failing_results: list[dict],
    context: dict
) -> list[GapEntry]:
    """Diagnose all failing results."""
    gaps = []
    
    for result in failing_results:
        gap = diagnose_single_failure(result, context)
        gaps.append(gap)
    
    return gaps

def prioritize_remediations(gaps: list[GapEntry]) -> list[RemediationItem]:
    """Group gaps into remediation items and prioritize."""
    # Group by fix category
    by_category = {}
    for gap in gaps:
        category = gap.fix_category
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(gap)
    
    # Build remediation items
    remediations = []
    
    for category, category_gaps in by_category.items():
        dimensions = list(set(g.dimension for g in category_gaps))
        agents = list(set(g.agent for g in category_gaps))
        
        # Estimate effort
        if len(category_gaps) < 3:
            effort = "small"
        elif len(category_gaps) < 7:
            effort = "medium"
        else:
            effort = "large"
        
        # Calculate impact score
        impact_score = len(category_gaps) * len(dimensions) * 10
        
        remediations.append(RemediationItem(
            fix_category=category,
            owner="webmaster" if "infrastructure" in category else "content",
            gaps_addressed=len(category_gaps),
            dimensions_affected=dimensions,
            agents_affected=agents,
            effort_estimate=effort,
            impact_score=float(impact_score),
            priority_rank=0,  # Set after sorting
            specific_actions=[],
            retest_condition="",
            evidence_ids=[]
        ))
    
    # Sort by impact score
    remediations.sort(key=lambda r: r.impact_score, reverse=True)
    
    # Assign priority ranks
    for i, rem in enumerate(remediations):
        rem.priority_rank = i + 1
    
    return remediations
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_stage5.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add stages/stage5.py tests/test_stage5.py
git commit -m "feat(stage5): gap diagnosis and remediation prioritization"
```

---

## Task 23: Cross-Agent Retrieval Matrix

**Files:**
- Create: `stages/cross_agent_matrix.py`
- Create: `tests/test_cross_agent_matrix.py`

- [ ] **Step 1: Write failing test**

Create `tests/test_cross_agent_matrix.py`:

```python
import pytest
from stages.cross_agent_matrix import build_retrieval_matrix, diagnose_pattern

def test_build_retrieval_matrix():
    agent_results = [
        {
            "dimension": "specificity",
            "agent": "openai/gpt-4o",
            "retrieval": {
                "retrieved_target": True,
                "target_url_rank": 1,
                "extraction_quality": 0.8,
                "usage_classification": "primary_source"
            },
            "traffic": {"cited_target": True}
        },
        {
            "dimension": "specificity",
            "agent": "google/gemini-2.0",
            "retrieval": {
                "retrieved_target": False
            },
            "traffic": {"cited_target": False}
        }
    ]
    
    matrix = build_retrieval_matrix(agent_results, "https://example.com/test")
    
    assert matrix.url == "https://example.com/test"
    assert len(matrix.retrieval_status) == 2

def test_diagnose_pattern_google_missing():
    retrieval_status = {
        "openai/gpt-4o": {"retrieved_target": True},
        "google/gemini-2.0": {"retrieved_target": False},
        "perplexity/sonar": {"retrieved_target": True}
    }
    
    pattern, diagnosis = diagnose_pattern(retrieval_status)
    
    assert "google" in pattern.lower()
    assert "SEO" in diagnosis or "Search" in diagnosis
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_cross_agent_matrix.py -v`  
Expected: FAIL

- [ ] **Step 3: Implement stages/cross_agent_matrix.py**

Create `stages/cross_agent_matrix.py`:

```python
from core.context import CrossAgentRetrievalMatrix, AgentRetrievalStatus

def build_retrieval_matrix(
    agent_results: list[dict],
    url: str
) -> list[CrossAgentRetrievalMatrix]:
    """Build cross-agent retrieval matrices per dimension."""
    # Group by dimension
    by_dimension = {}
    for result in agent_results:
        dim = result["dimension"]
        if dim not in by_dimension:
            by_dimension[dim] = []
        by_dimension[dim].append(result)
    
    matrices = []
    
    for dimension, results in by_dimension.items():
        # Build retrieval status per agent
        retrieval_status = {}
        
        for result in results:
            agent_key = f"{result['agent']}"
            retrieval = result.get("retrieval", {})
            traffic = result.get("traffic", {})
            
            retrieval_status[agent_key] = AgentRetrievalStatus(
                agent_name=result["agent"],
                model=result.get("model", ""),
                searched=len(retrieval.get("retrieved_urls", [])) > 0,
                retrieved_target=retrieval.get("retrieved_target", False),
                target_rank=retrieval.get("target_url_rank"),
                cited_target=traffic.get("cited_target", False),
                extraction_quality=retrieval.get("extraction_quality", 0.0),
                usage_classification=retrieval.get("usage_classification", "ignored")
            )
        
        # Diagnose pattern
        pattern, diagnosis = diagnose_pattern(retrieval_status)
        citation_pattern = diagnose_citation_pattern(retrieval_status)
        
        matrices.append(CrossAgentRetrievalMatrix(
            url=url,
            dimension=dimension,
            retrieval_status=retrieval_status,
            retrieval_pattern=pattern,
            citation_pattern=citation_pattern,
            diagnosis=diagnosis,
            suggested_fix="",  # Filled in later
            business_impact=""
        ))
    
    return matrices

def diagnose_pattern(retrieval_status: dict) -> tuple[str, str]:
    """Diagnose retrieval pattern across agents."""
    retrieved = [k for k, v in retrieval_status.items() if v.retrieved_target]
    not_retrieved = [k for k, v in retrieval_status.items() if not v.retrieved_target]
    
    if len(retrieved) == len(retrieval_status):
        return "all_retrieved", "All agents retrieved target - check content quality if not cited"
    
    if len(retrieved) == 0:
        return "none_retrieved", "CRITICAL: No agents retrieved target - major discoverability failure"
    
    # Check if Google missing
    google_agents = [k for k in retrieval_status.keys() if "google" in k.lower() or "gemini" in k.lower()]
    google_retrieved = [k for k in google_agents if k in retrieved]
    
    if google_agents and not google_retrieved:
        return "google_missing", "Google Search visibility issue - affects Gemini and traditional SEO"
    
    return "mixed_retrieval", f"Mixed retrieval: {len(retrieved)}/{len(retrieval_status)} agents found target"

def diagnose_citation_pattern(retrieval_status: dict) -> str:
    """Diagnose citation pattern."""
    cited = [k for k, v in retrieval_status.items() if v.cited_target]
    retrieved = [k for k, v in retrieval_status.items() if v.retrieved_target]
    
    if len(cited) == 0:
        return "no_citations"
    elif len(cited) == len(retrieved):
        return "all_citing"
    else:
        return "partial_citing"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_cross_agent_matrix.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add stages/cross_agent_matrix.py tests/test_cross_agent_matrix.py
git commit -m "feat(stage5): cross-agent retrieval matrix analysis"
```

---

## Task 24: HTML Report Generation

**Files:**
- Create: `reports/html_generator.py`
- Create: `reports/templates/audit_report.html`
- Create: `tests/test_html_generator.py`

- [ ] **Step 1: Write failing test**

Create `tests/test_html_generator.py`:

```python
import pytest
from reports.html_generator import generate_html_report
from core.context import AuditContext

def test_generate_html_report():
    context = AuditContext(url="https://example.com/product/test")
    context.geo_risk_level = "medium"
    context.overall_score = 75.5
    
    html = generate_html_report(context)
    
    assert "<html>" in html
    assert "GEO Audit Report" in html
    assert "75.5" in html
    assert "medium" in html.lower()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_html_generator.py -v`  
Expected: FAIL

- [ ] **Step 3: Create template reports/templates/audit_report.html**

Create `reports/templates/audit_report.html`:

```html
<!DOCTYPE html>
<html>
<head>
    <title>GEO Audit Report - {{ url }}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .summary { background: #f0f0f0; padding: 15px; margin: 20px 0; }
        .risk-low { color: green; }
        .risk-medium { color: orange; }
        .risk-high { color: red; }
        table { border-collapse: collapse; width: 100%; margin: 20px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background: #4CAF50; color: white; }
    </style>
</head>
<body>
    <h1>GEO Audit Report</h1>
    <div class="summary">
        <p><strong>URL:</strong> {{ url }}</p>
        <p><strong>Overall Score:</strong> {{ overall_score }}</p>
        <p><strong>Risk Level:</strong> <span class="risk-{{ geo_risk_level }}">{{ geo_risk_level }}</span></p>
    </div>
    
    <h2>Agent Results</h2>
    <table>
        <tr>
            <th>Agent</th>
            <th>Dimension</th>
            <th>Training Score</th>
            <th>Live Score</th>
            <th>Cited Target</th>
        </tr>
        {% for result in agent_results %}
        <tr>
            <td>{{ result.agent_name }}</td>
            <td>{{ result.dimension }}</td>
            <td>{{ result.training_score }}</td>
            <td>{{ result.live_score }}</td>
            <td>{{ result.traffic_analysis.cited_target if result.traffic_analysis else 'N/A' }}</td>
        </tr>
        {% endfor %}
    </table>
    
    <h2>Remediations</h2>
    <ul>
        {% for remediation in remediations %}
        <li><strong>{{ remediation.fix_category }}</strong>: {{ remediation.gaps_addressed }} gaps, {{ remediation.effort_estimate }} effort</li>
        {% endfor %}
    </ul>
</body>
</html>
```

- [ ] **Step 4: Implement reports/html_generator.py**

Create `reports/html_generator.py`:

```python
from jinja2 import Template
from pathlib import Path
from core.context import AuditContext

def generate_html_report(context: AuditContext) -> str:
    """Generate HTML report from audit context."""
    template_path = Path(__file__).parent / "templates" / "audit_report.html"
    template = Template(template_path.read_text())
    
    html = template.render(
        url=context.url,
        overall_score=context.overall_score,
        geo_risk_level=context.geo_risk_level,
        agent_results=context.agent_results,
        remediations=context.remediations
    )
    
    return html
```

- [ ] **Step 5: Run test to verify it passes**

Run: `pytest tests/test_html_generator.py -v`  
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add reports/html_generator.py reports/templates/audit_report.html tests/test_html_generator.py
git commit -m "feat(reports): HTML report generation"
```

---

## Task 25: CLI Interface

**Files:**
- Create: `cli.py`
- Create: `tests/test_cli.py`

- [ ] **Step 1: Write failing test**

Create `tests/test_cli.py`:

```python
import pytest
from unittest.mock import patch, MagicMock
from cli import parse_args, interactive_url_input

def test_parse_args_file_mode():
    args = parse_args(["--urls-file", "urls.txt"])
    assert args.urls_file == "urls.txt"
    assert args.interactive is False

def test_parse_args_interactive_mode():
    args = parse_args(["--interactive"])
    assert args.interactive is True

def test_interactive_url_input():
    with patch('builtins.input', side_effect=["https://example.com/test", ""]):
        urls = interactive_url_input()
        assert len(urls) == 1
        assert urls[0] == "https://example.com/test"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_cli.py -v`  
Expected: FAIL

- [ ] **Step 3: Implement cli.py**

Create `cli.py`:

```python
import argparse
import asyncio
from pathlib import Path
from typing import List
from core.orchestrator import run_audit
from core.config import load_config

def parse_args(argv=None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="GEO Audit Tool")
    
    parser.add_argument("--urls-file", help="Path to file with URLs (one per line)")
    parser.add_argument("--interactive", action="store_true", help="Interactive URL input mode")
    parser.add_argument("--config", default="config.yaml", help="Path to config file")
    parser.add_argument("--output-dir", default="output", help="Output directory")
    
    return parser.parse_args(argv)

def interactive_url_input() -> List[str]:
    """Prompt user to enter URLs interactively."""
    print("Enter URLs to audit (one per line, empty line to finish):")
    urls = []
    
    while True:
        url = input("> ").strip()
        if not url:
            break
        urls.append(url)
    
    return urls

def load_urls_from_file(file_path: str) -> List[str]:
    """Load URLs from text file."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"URLs file not found: {file_path}")
    
    urls = []
    for line in path.read_text().splitlines():
        url = line.strip()
        if url and not url.startswith("#"):
            urls.append(url)
    
    return urls

async def main():
    """Main CLI entry point."""
    args = parse_args()
    
    # Load config
    config = load_config(args.config)
    
    # Get URLs
    if args.interactive:
        urls = interactive_url_input()
    elif args.urls_file:
        urls = load_urls_from_file(args.urls_file)
    else:
        print("Error: Specify --urls-file or --interactive")
        return 1
    
    if not urls:
        print("No URLs provided")
        return 1
    
    print(f"Auditing {len(urls)} URLs...")
    
    # Run audits
    for url in urls:
        print(f"\\nAuditing: {url}")
        try:
            context = await run_audit(url, config, args.output_dir)
            print(f"  Overall Score: {context.overall_score}")
            print(f"  Risk Level: {context.geo_risk_level}")
            print(f"  Report: {context.output_files.get('html_report')}")
        except Exception as e:
            print(f"  ERROR: {e}")
    
    print("\\nAudit complete!")
    return 0

if __name__ == "__main__":
    exit(asyncio.run(main()))
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_cli.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add cli.py tests/test_cli.py
git commit -m "feat(cli): command-line interface"
```

---

## Task 26: Main Orchestrator

**Files:**
- Create: `core/orchestrator.py`
- Create: `tests/test_orchestrator.py`

- [ ] **Step 1: Write failing test**

Create `tests/test_orchestrator.py`:

```python
import pytest
from unittest.mock import AsyncMock, patch
from core.orchestrator import run_audit

@pytest.mark.asyncio
async def test_run_audit():
    config = {
        "agents": {"openai": {"enabled": True, "models": [{"name": "gpt-4o", "tier": "flagship"}]}}
    }
    
    with patch('core.orchestrator.run_stage1') as mock_stage1, \\
         patch('core.orchestrator.run_stage2') as mock_stage2, \\
         patch('core.orchestrator.run_stage3') as mock_stage3, \\
         patch('core.orchestrator.run_stage4') as mock_stage4, \\
         patch('core.orchestrator.run_stage5') as mock_stage5:
        
        mock_stage1.return_value = AsyncMock()
        mock_stage2.return_value = AsyncMock()
        mock_stage3.return_value = AsyncMock()
        mock_stage4.return_value = AsyncMock()
        mock_stage5.return_value = AsyncMock()
        
        context = await run_audit("https://example.com/product/test", config, "output")
        
        assert context.url == "https://example.com/product/test"
        assert mock_stage1.called
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_orchestrator.py -v`  
Expected: FAIL

- [ ] **Step 3: Implement core/orchestrator.py**

Create `core/orchestrator.py`:

```python
from core.context import AuditContext
from stages.stage1 import run_stage1
from stages.stage2 import run_stage2
from stages.stage3 import run_stage3
from stages.stage4 import run_stage4
from stages.stage5 import run_stage5
from reports.html_generator import generate_html_report
from pathlib import Path
import json

async def run_audit(url: str, config: dict, output_dir: str) -> AuditContext:
    """Run complete GEO audit pipeline."""
    # Initialize context
    context = AuditContext(url=url)
    
    # Stage 1: Fetch & Import
    context = await run_stage1(context, config)
    
    # Stage 2: Render
    context = await run_stage2(context, config)
    
    # Stage 3: Extract & Classify
    context = run_stage3(context, config)
    
    # Stage 4: AI Agent Prompting
    context = await run_stage4(context, config)
    
    # Stage 5: Gap Diagnosis
    context = run_stage5(context, config)
    
    # Generate outputs
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    product_id = context.product_id or "unknown"
    timestamp = context.audit_timestamp.replace(":", "-")
    
    # Full audit JSON
    audit_json_path = output_path / f"geo-audit-{product_id}-{timestamp}.json"
    audit_json_path.write_text(json.dumps(context.__dict__, indent=2, default=str))
    
    # HTML report
    html = generate_html_report(context)
    html_path = output_path / f"geo-audit-report-{product_id}-{timestamp}.html"
    html_path.write_text(html)
    
    context.output_files = {
        "audit_json": str(audit_json_path),
        "html_report": str(html_path)
    }
    
    return context
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_orchestrator.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add core/orchestrator.py tests/test_orchestrator.py
git commit -m "feat(core): main audit orchestrator"
```

---

## Task 27: Batch Processing with Error Handling

**Files:**
- Modify: `core/orchestrator.py`
- Create: `tests/test_batch_processing.py`

- [ ] **Step 1: Write failing test**

Create `tests/test_batch_processing.py`:

```python
import pytest
from unittest.mock import AsyncMock, patch
from core.orchestrator import run_batch_audit

@pytest.mark.asyncio
async def test_run_batch_audit_with_failures():
    urls = ["https://example.com/product/1", "https://example.com/product/2"]
    config = {}
    
    with patch('core.orchestrator.run_audit') as mock_audit:
        # First URL succeeds, second fails
        mock_audit.side_effect = [AsyncMock(), Exception("Network error")]
        
        results = await run_batch_audit(urls, config, "output")
        
        assert len(results["successful"]) == 1
        assert len(results["failed"]) == 1
        assert "Network error" in results["failed"][0]["error"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_batch_processing.py -v`  
Expected: FAIL

- [ ] **Step 3: Add batch processing to core/orchestrator.py**

Add to `core/orchestrator.py`:

```python
async def run_batch_audit(
    urls: list[str],
    config: dict,
    output_dir: str
) -> dict:
    """Run batch audit with skip-and-continue error handling."""
    results = {
        "successful": [],
        "failed": []
    }
    
    for url in urls:
        try:
            context = await run_audit(url, config, output_dir)
            results["successful"].append({
                "url": url,
                "score": context.overall_score,
                "risk": context.geo_risk_level
            })
        except Exception as e:
            results["failed"].append({
                "url": url,
                "error": str(e)
            })
            # Continue to next URL
            continue
    
    return results
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_batch_processing.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add core/orchestrator.py tests/test_batch_processing.py
git commit -m "feat(core): batch processing with skip-and-continue"
```

---

## Task 28: Integration Test

**Files:**
- Create: `tests/integration/test_full_audit.py`

- [ ] **Step 1: Write integration test**

Create `tests/integration/test_full_audit.py`:

```python
import pytest
import os
from pathlib import Path
from core.orchestrator import run_audit
from core.config import load_config

@pytest.mark.integration
@pytest.mark.skipif(not os.getenv("RUN_INTEGRATION_TESTS"), reason="Integration tests disabled")
@pytest.mark.asyncio
async def test_full_audit_end_to_end():
    """Full end-to-end audit test with real URL."""
    # Load config
    config = load_config("config.yaml")
    
    # Run audit on test URL
    url = "https://www.sigmaaldrich.com/US/en/product/sigma/c22010"
    
    context = await run_audit(url, config, "output/integration-test")
    
    # Verify stages completed
    assert context.product_id is not None
    assert len(context.content_blocks) > 0
    assert len(context.agent_results) > 0
    assert context.overall_score > 0
    assert context.geo_risk_level in ["low", "medium", "high", "critical"]
    
    # Verify outputs generated
    assert Path(context.output_files["audit_json"]).exists()
    assert Path(context.output_files["html_report"]).exists()
```

- [ ] **Step 2: Run test to verify it passes**

Run: `RUN_INTEGRATION_TESTS=1 pytest tests/integration/test_full_audit.py -v`  
Expected: PASS (requires API keys)

- [ ] **Step 3: Commit**

```bash
git add tests/integration/test_full_audit.py
git commit -m "test(integration): full audit end-to-end test"
```

---

## Task 29: Documentation

**Files:**
- Create: `README.md`
- Create: `docs/USAGE.md`

- [ ] **Step 1: Create README.md**

Create `README.md`:

```markdown
# GEO Audit Tool

Python CLI tool for auditing product pages for Generative Engine Optimization (GEO).

## Features

- Dual-mode testing (training data + live retrieval)
- Multi-agent support (OpenAI, Anthropic, Google, Perplexity, Bing)
- Unbranded prompts for real-world discovery
- Auto-competitor detection
- Content value ranking
- Traffic impact analysis
- HTML + PDF reports

## Installation

\`\`\`bash
pip install -r requirements.txt
\`\`\`

## Quick Start

Interactive mode:
\`\`\`bash
python cli.py --interactive
\`\`\`

File mode:
\`\`\`bash
python cli.py --urls-file urls.txt
\`\`\`

## Configuration

Edit `config.yaml` to configure agents, models, and testing scope.

## Cost Estimate

Flagship-only mode: ~$1.16 per URL (10 URLs = ~$12)

## Documentation

See `docs/USAGE.md` for detailed usage guide.
```

- [ ] **Step 2: Create docs/USAGE.md**

Create `docs/USAGE.md`:

```markdown
# Usage Guide

## Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Configure API keys in `.env`
3. Edit `config.yaml` for agent settings

## Running Audits

### Interactive Mode

\`\`\`bash
python cli.py --interactive
\`\`\`

### File Mode

Create `urls.txt`:
\`\`\`
https://example.com/product/1
https://example.com/product/2
\`\`\`

Run:
\`\`\`bash
python cli.py --urls-file urls.txt
\`\`\`

## Output Files

Per URL:
- `geo-audit-{id}-{timestamp}.json` - Full audit data
- `geo-audit-report-{id}-{timestamp}.html` - HTML report
- `geo-audit-report-{id}-{timestamp}.pdf` - PDF report

## Configuration

See `config.yaml` for all options.
```

- [ ] **Step 3: Commit**

```bash
git add README.md docs/USAGE.md
git commit -m "docs: README and usage guide"
```

---

## Task 30: Final Integration & Testing

**Files:**
- Review all files
- Run full test suite
- Test on real URL

- [ ] **Step 1: Run full test suite**

Run: `pytest tests/ -v`  
Expected: All tests PASS

- [ ] **Step 2: Test CLI on real URL**

Run:
\`\`\`bash
python cli.py --interactive
# Enter: https://www.sigmaaldrich.com/US/en/product/sigma/c22010
\`\`\`

Expected: Audit completes, generates reports

- [ ] **Step 3: Review output files**

Check `output/` directory for:
- audit JSON
- HTML report
- PDF report (if WeasyPrint installed)

- [ ] **Step 4: Final commit**

\`\`\`bash
git add -A
git commit -m "feat: complete GEO audit tool implementation"
\`\`\`

---

# Implementation Complete

All 30 tasks completed. Tool ready for use.

Next steps:
1. Deploy to production environment
2. Run audits on target product catalog
3. Prioritize remediations based on output
4. Iterate based on feedback

**Total estimated time:** 20-30 hours of focused development

## Task 14: Sibling Discovery via Search

**Files:**
- Create: `stages/sibling_discovery.py`
- Create: `tests/test_sibling_discovery.py`

- [ ] **Step 1: Write failing test for sibling discovery**

Create `tests/test_sibling_discovery.py`:

```python
import pytest
from unittest.mock import patch, Mock
from stages.sibling_discovery import discover_siblings, extract_domain

def test_extract_domain():
    url = "https://www.example.com/product/test-123"
    domain = extract_domain(url)
    assert domain == "www.example.com"

@pytest.mark.asyncio
async def test_discover_siblings():
    with patch('serpapi.GoogleSearch') as mock_search:
        mock_results = Mock()
        mock_results.get_dict.return_value = {
            "organic_results": [
                {"link": "https://example.com/product/sibling-1"},
                {"link": "https://example.com/product/sibling-2"}
            ]
        }
        mock_search.return_value = mock_results
        
        with patch('stages.sibling_discovery.fetch_and_parse_product') as mock_fetch:
            mock_fetch.return_value = {
                "url": "https://example.com/product/sibling-1",
                "name": "Sibling Product",
                "product_id": "SIB-001",
                "key_differences": ["Higher purity"]
            }
            
            siblings = await discover_siblings(
                product_name="Test Product",
                domain="example.com",
                category="chemical_reagent",
                config={"sibling_discovery": {"max_siblings": 3}}
            )
            
            assert len(siblings) > 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_sibling_discovery.py -v`  
Expected: FAIL with "ImportError: cannot import name 'discover_siblings'"

- [ ] **Step 3: Implement stages/sibling_discovery.py**

Create `stages/sibling_discovery.py`:

```python
import os
import httpx
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from serpapi import GoogleSearch
from core.context import SiblingProduct
from stages.extract import extract_json_ld, find_product_schema

def extract_domain(url: str) -> str:
    """Extract domain from URL."""
    parsed = urlparse(url)
    return parsed.netloc

async def fetch_and_parse_product(url: str) -> dict | None:
    """Fetch URL and extract product info."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10, follow_redirects=True)
            
            if response.status_code != 200:
                return None
            
            html = response.text
            json_ld_blocks = extract_json_ld(html)
            schema = find_product_schema(json_ld_blocks)
            
            if not schema:
                return None
            
            return {
                "url": url,
                "name": schema.get("name", ""),
                "product_id": schema.get("sku", ""),
                "schema": schema
            }
    except Exception:
        return None

def extract_distinguishing_features(schema: dict) -> list[str]:
    """Extract distinguishing features from product schema."""
    features = []
    
    # Check for purity/concentration differences
    if "description" in schema:
        desc = schema["description"].lower()
        if "purity" in desc or "%" in desc:
            features.append("Different purity level")
    
    # Check for size/volume differences
    if "offers" in schema:
        offer = schema["offers"]
        if "itemOffered" in offer:
            features.append("Different size/volume")
    
    # Generic fallback
    if not features:
        features.append("Product variant")
    
    return features

async def discover_siblings(
    product_name: str,
    domain: str,
    category: str,
    config: dict
) -> list[SiblingProduct]:
    """Discover sibling products via search."""
    api_key = os.getenv("SERPAPI_KEY")
    if not api_key:
        return []
    
    # Extract brand from product name (simple heuristic)
    brand = product_name.split()[0] if product_name else ""
    
    # Build search query
    query = f'site:{domain} "{category}" "{brand}"'
    
    # Search
    search = GoogleSearch({
        "q": query,
        "api_key": api_key,
        "num": 10
    })
    
    results = search.get_dict()
    organic_results = results.get("organic_results", [])
    
    # Filter to product URLs
    max_siblings = config.get("sibling_discovery", {}).get("max_siblings", 3)
    siblings = []
    
    for result in organic_results[:max_siblings * 2]:  # Fetch 2x in case some fail
        url = result.get("link")
        if not url:
            continue
        
        # Fetch and parse
        product_data = await fetch_and_parse_product(url)
        if not product_data:
            continue
        
        # Extract distinguishing features
        key_differences = extract_distinguishing_features(product_data["schema"])
        
        siblings.append(SiblingProduct(
            url=product_data["url"],
            name=product_data["name"],
            product_id=product_data["product_id"],
            key_differences=key_differences
        ))
        
        if len(siblings) >= max_siblings:
            break
    
    return siblings
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_sibling_discovery.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add stages/sibling_discovery.py tests/test_sibling_discovery.py
git commit -m "feat(stage4): sibling product discovery via search"
```

---

## Task 15: Unbranded Prompt Construction

**Files:**
- Modify: `stages/prompts.py`
- Modify: `tests/test_prompts.py`

- [ ] **Step 1: Write failing test for prompt construction**

Add to `tests/test_prompts.py`:

```python
import yaml
from pathlib import Path
from stages.prompts import build_adversarial_prompts

def test_build_adversarial_prompts():
    reference_facts = {
        "core": {
            "product_id": "TEST-001",
            "product_name": "Test Product",
            "canonical_url": "https://example.com/product/test"
        }
    }
    
    siblings = [
        SiblingProduct(
            url="https://example.com/product/sibling",
            name="Sibling Product",
            product_id="SIB-001",
            key_differences=["Higher purity"]
        )
    ]
    
    category = "chemical_reagent"
    templates = yaml.safe_load(Path("prompts/templates.yaml").read_text())
    
    prompts = build_adversarial_prompts(
        reference_facts,
        siblings,
        category,
        templates,
        pass_threshold=70
    )
    
    assert len(prompts) == 6  # 6 dimensions
    
    # Check specificity prompt
    spec_prompt = next(p for p in prompts if p.dimension == "specificity")
    assert "TEST-001" in spec_prompt.prompt
    assert "Test Product" in spec_prompt.prompt
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_prompts.py::test_build_adversarial_prompts -v`  
Expected: FAIL with "ImportError: cannot import name 'build_adversarial_prompts'"

- [ ] **Step 3: Implement prompt construction in stages/prompts.py**

Add to `stages/prompts.py`:

```python
import uuid
from core.context import PromptExecution, SiblingProduct

def extract_characteristics(reference_facts: dict, category: str) -> dict:
    """Extract product characteristics for unbranded query construction."""
    characteristics = {}
    
    # Extract from core
    core = reference_facts.get("core", {})
    
    # Extract from category-specific facts
    if category == "cell_culture_media":
        culture = reference_facts.get("culture", {})
        characteristics["application"] = "endothelial cell culture"
        characteristics["supplements"] = culture.get("supplements", [])
        characteristics["storage"] = culture.get("storage_temp", "")
    elif category == "chemical_reagent":
        chem = reference_facts.get("chemical", {})
        characteristics["purity"] = chem.get("purity", "")
        characteristics["formula"] = chem.get("formula", "")
    
    return characteristics

def build_unbranded_query(characteristics: dict, dimension: str) -> str:
    """Build generic query from characteristics - no brand, no catalog number."""
    if dimension == "specificity":
        # Generic product requirements query
        if "application" in characteristics:
            return f"What makes a good {characteristics['application']} product?"
        return "What factors to consider for this type of product?"
    
    elif dimension == "entity_understanding":
        # Generic "I need X with Y" query
        requirements = characteristics.get("supplements", [])
        if requirements:
            req_str = " and ".join(requirements)
            return f"I need a product with {req_str}. What are my options?"
        return "What options are available for this type of product?"
    
    elif dimension == "workflow_understanding":
        # Generic application workflow
        if "application" in characteristics:
            return f"I'm planning to use this for {characteristics['application']}. What should I know?"
        return "What should I know about using this type of product?"
    
    elif dimension == "evidence_trust":
        # Generic selection criteria
        return "What are the key factors when choosing this type of product?"
    
    elif dimension == "comparison":
        # Generic comparison
        if "purity" in characteristics:
            return f"Compare options for products with {characteristics['purity']} purity."
        return "Compare options for this type of product."
    
    elif dimension == "commercial":
        # Generic purchase query
        if "application" in characteristics:
            return f"Where can I buy products for {characteristics['application']}?"
        return "Where can I purchase this type of product?"
    
    return ""

def build_unbranded_prompts(
    reference_facts: dict,
    siblings: list[SiblingProduct],
    category: str,
    templates: dict,
    pass_threshold: int = 70
) -> list[PromptExecution]:
    """Build unbranded prompts for all dimensions - no brand/SKU in queries."""
    prompts = []
    
    core = reference_facts.get("core", {})
    
    # Extract characteristics
    characteristics = extract_characteristics(reference_facts, category)
    
    # Build all 6 dimensions with UNBRANDED queries
    dimensions = ["specificity", "entity_understanding", "workflow_understanding", 
                  "evidence_trust", "comparison", "commercial"]
    
    for dim in dimensions:
        # Build generic query (no brand, no catalog number)
        unbranded_query = build_unbranded_query(characteristics, dim)
        
        prompts.append(PromptExecution(
            id=f"prompt-{uuid.uuid4().hex[:8]}",
            dimension=dim,
            question=unbranded_query,  # UNBRANDED query
            prompt=unbranded_query,
            reference_content=reference_facts,
            sibling_context=siblings if dim == "entity_understanding" else None,
            pass_threshold=pass_threshold
        ))
    
    return prompts
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_prompts.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add stages/prompts.py tests/test_prompts.py
git commit -m "feat(stage4): adversarial prompt construction"
```

---

## Task 16: Agent API Integration & Rate Limiting

**Files:**
- Modify: `stages/prompts.py`
- Modify: `tests/test_prompts.py`

- [ ] **Step 1: Write failing test for agent API calls**

Add to `tests/test_prompts.py`:

```python
from stages.prompts import send_prompt_to_agents, RateLimiter

@pytest.mark.asyncio
async def test_rate_limiter():
    config = {
        "max_requests_per_minute": 60,
        "delay_between_requests": 1.0
    }
    
    limiter = RateLimiter(config)
    
    # Should acquire immediately
    await limiter.acquire()
    assert True  # No exception

@pytest.mark.asyncio
async def test_send_prompt_to_agents():
    with patch('openai.OpenAI') as mock_openai:
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test response"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        prompt = PromptExecution(
            id="test-001",
            dimension="specificity",
            question="Test question",
            prompt="Test prompt",
            reference_content={},
            sibling_context=None,
            pass_threshold=70
        )
        
        config = {
            "agents": {
                "openai": {
                    "enabled": True,
                    "models": [{"name": "gpt-4o", "mode": "search"}]
                }
            },
            "rate_limits": {
                "openai": {
                    "max_requests_per_minute": 60,
                    "delay_between_requests": 0.1
                }
            }
        }
        
        responses = await send_prompt_to_agents(prompt, config)
        
        assert len(responses) > 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_prompts.py::test_send_prompt_to_agents -v`  
Expected: FAIL with "ImportError: cannot import name 'send_prompt_to_agents'"

- [ ] **Step 3: Implement agent integration in stages/prompts.py**

Add to `stages/prompts.py`:

```python
import os
import asyncio
import time
from openai import OpenAI
from anthropic import Anthropic
import google.generativeai as genai
from core.context import AgentResponse, Hallucination
from core.evidence import create_evidence

class RateLimiter:
    def __init__(self, config: dict):
        self.delay = config.get("delay_between_requests", 1.0)
        self.last_request = 0
    
    async def acquire(self):
        """Wait if needed to respect rate limit."""
        now = time.time()
        time_since_last = now - self.last_request
        
        if time_since_last < self.delay:
            await asyncio.sleep(self.delay - time_since_last)
        
        self.last_request = time.time()

async def call_openai(prompt: str, model: str, mode: str) -> str:
    """Call OpenAI API."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set")
    
    client = OpenAI(api_key=api_key)
    
    # For search mode, add web search instruction
    if mode == "search":
        system_msg = "You have web search access. Use it to find current information about the product URL provided."
    else:
        system_msg = "Answer based on the information provided."
    
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )
    
    return response.choices[0].message.content

async def call_anthropic(prompt: str, model: str) -> str:
    """Call Anthropic API."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not set")
    
    client = Anthropic(api_key=api_key)
    
    # Note: Actual web search integration would require extended request format
    response = client.messages.create(
        model=model,
        max_tokens=1024,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.content[0].text

async def call_google(prompt: str, model: str) -> str:
    """Call Google Gemini API."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not set")
    
    genai.configure(api_key=api_key)
    model_obj = genai.GenerativeModel(model)
    
    response = model_obj.generate_content(prompt)
    return response.text

async def send_prompt_to_agents(
    prompt_exec: PromptExecution,
    config: dict
) -> list[AgentResponse]:
    """Send prompt to all enabled agents with rate limiting."""
    responses = []
    agents_config = config.get("agents", {})
    rate_limits = config.get("rate_limits", {})
    
    for agent_name, agent_config in agents_config.items():
        if not agent_config.get("enabled", False):
            continue
        
        # Rate limiter for this agent
        limiter = RateLimiter(rate_limits.get(agent_name, {}))
        
        # Send to each model
        for model_config in agent_config.get("models", []):
            model_name = model_config.get("name")
            mode = model_config.get("mode", "")
            
            await limiter.acquire()
            
            try:
                # Call appropriate API
                if agent_name == "openai":
                    raw_response = await call_openai(prompt_exec.prompt, model_name, mode)
                elif agent_name == "anthropic":
                    raw_response = await call_anthropic(prompt_exec.prompt, model_name)
                elif agent_name == "google":
                    raw_response = await call_google(prompt_exec.prompt, model_name)
                else:
                    continue
                
                # Parse citations (simple URL extraction)
                import re
                urls = re.findall(r'https?://[^\s]+', raw_response)
                
                responses.append(AgentResponse(
                    prompt_id=prompt_exec.id,
                    agent_name=agent_name,
                    model=model_name,
                    mode=mode,
                    raw_response=raw_response,
                    cited_urls=urls,
                    score=0.0,  # Will be scored later
                    hallucinations=[],  # Will be detected later
                    evidence_id=""  # Will be linked later
                ))
                
            except Exception as e:
                # Log error but continue with other agents
                print(f"Error calling {agent_name}/{model_name}: {e}")
                continue
    
    return responses
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_prompts.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add stages/prompts.py tests/test_prompts.py
git commit -m "feat(stage4): agent API integration with rate limiting"
```

---

## Task 17: Fact-Checking & Hallucination Detection

**Files:**
- Create: `stages/fact_check.py`
- Create: `tests/test_fact_check.py`

- [ ] **Step 1: Write failing test for fact checking**

Create `tests/test_fact_check.py`:

```python
import pytest
from stages.fact_check import fact_check_score, detect_hallucinations, extract_factual_claims

def test_extract_factual_claims():
    response_text = "The product TEST-001 has a molecular weight of 58.44 g/mol and 99.5% purity."
    category = "chemical_reagent"
    
    claims = extract_factual_claims(response_text, category)
    
    assert len(claims) > 0
    assert any("TEST-001" in claim for claim in claims)

def test_fact_check_score():
    response_text = "Product ID: TEST-001, Storage: -20°C"
    reference_facts = {
        "core": {"product_id": "TEST-001"},
        "chemical": {"storage_temp": "-20°C"}
    }
    category = "chemical_reagent"
    checklist = ["product_id", "storage_temp"]
    
    score = fact_check_score(response_text, reference_facts, category, checklist)
    
    assert score == 100.0  # Both facts matched

def test_detect_hallucinations():
    response_text = "Storage at -80°C (hallucinated)"
    content_blocks = [
        Mock(content="Storage at -20°C")
    ]
    product_schema = {"sku": "TEST-001"}
    category = "chemical_reagent"
    
    hallucinations = detect_hallucinations(
        response_text,
        content_blocks,
        product_schema,
        category
    )
    
    assert len(hallucinations) > 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_fact_check.py -v`  
Expected: FAIL with "ImportError: cannot import name 'fact_check_score'"

- [ ] **Step 3: Implement stages/fact_check.py**

Create `stages/fact_check.py`:

```python
import spacy
from rapidfuzz import fuzz
from core.context import ContentBlock, Hallucination

# Load spaCy model for NER
nlp = spacy.load("en_core_web_sm")

def extract_factual_claims(text: str, category: str) -> list[str]:
    """Extract factual claims from response text using NER."""
    doc = nlp(text)
    
    claims = []
    
    # Extract sentences with entities or numbers
    for sent in doc.sents:
        # Check if sentence contains numbers or specific entities
        has_number = any(token.like_num for token in sent)
        has_entity = len(sent.ents) > 0
        
        if has_number or has_entity:
            claims.append(sent.text.strip())
    
    return claims

def fact_check_score(
    response_text: str,
    reference_facts: dict,
    category: str,
    checklist: list[str]
) -> float:
    """Score response based on fact-checking against reference."""
    total = len(checklist)
    matched = 0
    
    for field in checklist:
        # Find expected value in reference facts
        expected_value = None
        for section in reference_facts.values():
            if isinstance(section, dict) and field in section:
                expected_value = str(section[field])
                break
        
        if not expected_value:
            continue
        
        # Check if in response (exact or fuzzy)
        if expected_value.lower() in response_text.lower():
            matched += 1
        elif fuzz.partial_ratio(expected_value, response_text) > 85:
            matched += 1
    
    return (matched / total * 100) if total > 0 else 0.0

def detect_hallucinations(
    response_text: str,
    content_blocks: list[ContentBlock],
    product_schema: dict,
    category: str
) -> list[Hallucination]:
    """Detect hallucinations by checking claims against page content."""
    claims = extract_factual_claims(response_text, category)
    hallucinations = []
    
    # Build searchable content
    all_content = " ".join([b.content for b in content_blocks])
    schema_text = str(product_schema)
    
    for claim in claims:
        # Skip generic claims (too short or common words)
        if len(claim.split()) < 5:
            continue
        
        # Check if supported by content
        supported = False
        
        # Exact match in content
        if claim.lower() in all_content.lower():
            supported = True
        
        # Exact match in schema
        if claim.lower() in schema_text.lower():
            supported = True
        
        # Fuzzy match
        if not supported:
            for block in content_blocks:
                if fuzz.partial_ratio(claim, block.content) > 85:
                    supported = True
                    break
        
        if not supported:
            # Determine type
            hallu_type = "hallucination"
            severity = "medium"
            
            # Check if critical fact
            critical_keywords = ["catalog", "product id", "sku", "storage", "temperature"]
            if any(kw in claim.lower() for kw in critical_keywords):
                severity = "high"
                hallu_type = "factual_hallucination"
            
            hallucinations.append(Hallucination(
                claim=claim,
                type=hallu_type,
                severity=severity
            ))
    
    return hallucinations
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_fact_check.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add stages/fact_check.py tests/test_fact_check.py
git commit -m "feat(stage4): fact-checking and hallucination detection"
```

---

## Task 18: LLM-as-Judge Scoring

**Files:**
- Create: `stages/judge.py`
- Create: `tests/test_judge.py`

- [ ] **Step 1: Write failing test for LLM judge**

Create `tests/test_judge.py`:

```python
import pytest
from unittest.mock import patch, Mock
from stages.judge import llm_judge_score

def test_llm_judge_score():
    with patch('openai.OpenAI') as mock_openai:
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '{"score": 85, "reasoning": "Good answer"}'
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        response_text = "Test response"
        reference_facts = {"core": {"product_id": "TEST-001"}}
        dimension = "workflow_understanding"
        
        score = llm_judge_score(response_text, reference_facts, dimension)
        
        assert score == 85
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_judge.py -v`  
Expected: FAIL with "ImportError: cannot import name 'llm_judge_score'"

- [ ] **Step 3: Implement stages/judge.py**

Create `stages/judge.py`:

```python
import os
import json
from openai import OpenAI

def llm_judge_score(
    response_text: str,
    reference_facts: dict,
    dimension: str
) -> float:
    """Score response using LLM-as-judge for qualitative dimensions."""
    api_key = os.getenv("JUDGE_API_KEY") or os.getenv("OPENAI_API_KEY")
    model = os.getenv("JUDGE_MODEL", "gpt-4o-mini")
    
    if not api_key:
        return 0.0
    
    client = OpenAI(api_key=api_key)
    
    # Build judge prompt
    judge_prompt = f"""You are evaluating an AI agent's response for the "{dimension}" dimension.

Reference facts from the product page:
{json.dumps(reference_facts, indent=2)}

Agent's response:
{response_text}

Score the response 0-100 based on:
- Accuracy: Does it match reference facts?
- Completeness: Does it address the question fully?
- Groundedness: Is it based on page content or hallucinated?

Return JSON: {{"score": 0-100, "reasoning": "brief explanation"}}"""
    
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": judge_prompt}],
        temperature=0
    )
    
    try:
        result = json.loads(response.choices[0].message.content)
        return float(result.get("score", 0))
    except (json.JSONDecodeError, ValueError):
        return 0.0
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_judge.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add stages/judge.py tests/test_judge.py
git commit -m "feat(stage4): LLM-as-judge scoring"
```

---

## Task 19: Stage 4 Orchestration

**Files:**
- Modify: `stages/prompts.py`
- Modify: `tests/test_prompts.py`

- [ ] **Step 1: Write test for full Stage 4**

Add to `tests/test_prompts.py`:

```python
@pytest.mark.asyncio
async def test_stage_4_prompts():
    ctx = AuditContext(
        url="https://example.com/product/test",
        config={
            "agents": {"openai": {"enabled": False}},  # Disabled for test
            "sibling_discovery": {"max_siblings": 0},
            "pass_threshold": 70
        }
    )
    ctx.product_schema = {"name": "Test", "sku": "TEST-001"}
    ctx.product_category = "chemical_reagent"
    ctx.content_blocks = []
    
    # Should not crash even with no agents enabled
    ctx = await stage_4_prompts(ctx)
    
    assert ctx.reference_facts is not None
    assert isinstance(ctx.prompts_sent, list)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_prompts.py::test_stage_4_prompts -v`  
Expected: FAIL with "ImportError: cannot import name 'stage_4_prompts'"

- [ ] **Step 3: Implement stage_4_prompts in stages/prompts.py**

Add to `stages/prompts.py`:

```python
from stages.sibling_discovery import discover_siblings
from stages.fact_check import fact_check_score, detect_hallucinations
from stages.judge import llm_judge_score
from core.evidence import link_evidence

async def stage_4_prompts(context: AuditContext) -> AuditContext:
    """Stage 4: AI agent prompting and scoring."""
    
    # 1. Generate reference facts
    context.reference_facts = generate_reference_facts(
        context.product_schema or {},
        context.content_blocks,
        context.product_category
    )
    
    # 2. Discover siblings
    domain = extract_domain(context.url) if context.url else ""
    context.sibling_products = await discover_siblings(
        product_name=context.product_schema.get("name", "") if context.product_schema else "",
        domain=domain,
        category=context.product_category,
        config=context.config
    )
    
    # 3. Build prompts
    templates = load_prompt_templates()
    prompts = build_adversarial_prompts(
        context.reference_facts,
        context.sibling_products,
        context.product_category,
        templates,
        pass_threshold=context.config.get("pass_threshold", 70)
    )
    
    context.prompts_sent = prompts
    
    # 4. Send to agents
    for prompt in prompts:
        responses = await send_prompt_to_agents(prompt, context.config)
        
        # 5. Score each response
        for response in responses:
            # Fact-check score
            category_checklist = context.config.get("category_checklists", {}).get(
                context.product_category, []
            )
            
            fact_score = fact_check_score(
                response.raw_response,
                context.reference_facts,
                context.product_category,
                category_checklist
            )
            
            # LLM judge score for qualitative dimensions
            judge_score = None
            if prompt.dimension in ["workflow_understanding", "evidence_trust"]:
                judge_score = llm_judge_score(
                    response.raw_response,
                    context.reference_facts,
                    prompt.dimension
                )
            
            # Hybrid score
            if judge_score is not None:
                response.score = (fact_score * 0.6) + (judge_score * 0.4)
            else:
                response.score = fact_score
            
            # 6. Detect hallucinations
            response.hallucinations = detect_hallucinations(
                response.raw_response,
                context.content_blocks,
                context.product_schema or {},
                context.product_category
            )
            
            # Link evidence
            ev = link_evidence(
                context,
                source_type="agent_response",
                source_agent=f"{response.agent_name}/{response.model}",
                content_ref=f"{prompt.dimension}.response",
                raw_content=response.raw_response
            )
            response.evidence_id = ev.id
        
        context.agent_responses.extend(responses)
    
    return context

from urllib.parse import urlparse

def extract_domain(url: str) -> str:
    """Extract domain from URL."""
    parsed = urlparse(url)
    return parsed.netloc
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_prompts.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add stages/prompts.py tests/test_prompts.py
git commit -m "feat(stage4): complete AI prompting pipeline"
```

---

## Task 20: Stage 5 - Dimension Scoring & Gap Diagnosis

**Files:**
- Create: `stages/report.py`
- Create: `tests/test_report.py`

- [ ] **Step 1: Write failing test for dimension scoring**

Create `tests/test_report.py`:

```python
import pytest
from stages.report import score_dimensions, diagnose_gaps, classify_failure

def test_score_dimensions():
    prompts = [
        PromptExecution(
            id="p1",
            dimension="specificity",
            question="Q",
            prompt="P",
            reference_content={},
            sibling_context=None,
            pass_threshold=70
        )
    ]
    
    responses = [
        AgentResponse(
            prompt_id="p1",
            agent_name="openai",
            model="gpt-4o",
            mode="search",
            raw_response="Response",
            cited_urls=[],
            score=85.0,
            hallucinations=[],
            evidence_id="ev-001"
        ),
        AgentResponse(
            prompt_id="p1",
            agent_name="anthropic",
            model="claude-sonnet-4",
            mode="tools",
            raw_response="Response",
            cited_urls=[],
            score=65.0,  # Below threshold
            hallucinations=[],
            evidence_id="ev-002"
        )
    ]
    
    scores = score_dimensions(responses, prompts)
    
    assert "specificity" in scores
    assert scores["specificity"].pass_rate == 0.5  # 1 of 2 passed
    assert scores["specificity"].avg_score == 75.0  # Average of 85 and 65
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_report.py -v`  
Expected: FAIL with "ImportError: cannot import name 'score_dimensions'"

- [ ] **Step 3: Implement stages/report.py (scoring)**

Create `stages/report.py`:

```python
from core.context import (
    AuditContext, PromptExecution, AgentResponse, DimensionScore,
    GapEntry, RootCause, RemediationItem, ContentBlock
)

def score_dimensions(
    agent_responses: list[AgentResponse],
    prompts_sent: list[PromptExecution]
) -> dict[str, DimensionScore]:
    """Score each dimension across all agents."""
    dimension_scores = {}
    
    for prompt in prompts_sent:
        dim = prompt.dimension
        responses = [r for r in agent_responses if r.prompt_id == prompt.id]
        
        if not responses:
            continue
        
        agent_results = {}
        for response in responses:
            agent_results[response.agent_name] = {
                "score": response.score,
                "passed": response.score >= prompt.pass_threshold,
                "hallucinations": len(response.hallucinations),
                "citations": response.cited_urls
            }
        
        pass_count = sum(1 for r in agent_results.values() if r["passed"])
        total_count = len(agent_results)
        
        dimension_scores[dim] = DimensionScore(
            dimension=dim,
            agent_results=agent_results,
            pass_rate=pass_count / total_count if total_count > 0 else 0.0,
            avg_score=sum(r["score"] for r in agent_results.values()) / total_count if total_count > 0 else 0.0
        )
    
    return dimension_scores

def classify_failure(response: AgentResponse, dimension: str) -> str:
    """Classify failure type based on response characteristics."""
    # Check for hallucinations
    if response.hallucinations:
        # Check if wrong URL/catalog number
        wrong_url_indicators = ["http", "www", ".com"]
        if any(ind in h.claim for h in response.hallucinations for ind in wrong_url_indicators):
            return "wrong_url"
        
        if any("catalog" in h.claim.lower() or "sku" in h.claim.lower() for h in response.hallucinations):
            return "wrong_catalog_number"
        
        return "hallucination"
    
    # Check for generic synthesis
    if response.score < 30:  # Very low score suggests generic answer
        return "generic_synthesis"
    
    # Check for sibling confusion (entity understanding dimension)
    if dimension == "entity_understanding" and response.score < 60:
        return "sibling_confusion"
    
    # Check for no citations
    if not response.cited_urls:
        return "no_citation"
    
    return "incomplete_answer"

def diagnose_gaps(
    dimension_scores: dict[str, DimensionScore],
    agent_responses: list[AgentResponse],
    visibility_matrix: dict,
    crawler_coverage: dict,
    content_blocks: list[ContentBlock]
) -> list[GapEntry]:
    """Diagnose root causes for failing responses."""
    gaps = []
    
    for dim, score in dimension_scores.items():
        failing_agents = [
            agent for agent, result in score.agent_results.items()
            if not result["passed"]
        ]
        
        if not failing_agents:
            continue
        
        for agent_name in failing_agents:
            # Find response
            response = next(
                (r for r in agent_responses 
                 if r.agent_name == agent_name and any(
                     p.dimension == dim for p in [Mock(dimension=dim)]
                 )),
                None
            )
            
            if not response:
                continue
            
            # Classify failure type
            failure_type = classify_failure(response, dim)
            
            # Trace root cause
            root_cause = trace_root_cause(
                failure_type,
                response,
                visibility_matrix,
                content_blocks
            )
            
            # Map to fix category
            fix_category = map_to_fix_category(root_cause)
            
            gaps.append(GapEntry(
                dimension=dim,
                agent=agent_name,
                failure_type=failure_type,
                root_cause=root_cause,
                fix_category=fix_category,
                evidence_ids=[response.evidence_id],
                explanation=generate_explanation(failure_type, root_cause),
                geo_impact=assess_geo_impact(dim, failure_type)
            ))
    
    return gaps

def trace_root_cause(
    failure_type: str,
    response: AgentResponse,
    visibility_matrix: dict,
    content_blocks: list[ContentBlock]
) -> RootCause:
    """Trace failure to root cause."""
    
    if failure_type == "generic_synthesis":
        # Check if unique facts exist
        unique_blocks = [b for b in content_blocks if b.type in ["product_id", "specifications"]]
        if not unique_blocks:
            return RootCause(
                type="content_gap",
                detail="No unique product facts in page content",
                evidence_ids=[b.evidence_id for b in content_blocks]
            )
    
    elif failure_type == "hallucination":
        return RootCause(
            type="content_gap",
            detail="Critical facts not present in page content",
            evidence_ids=[]
        )
    
    elif failure_type == "sibling_confusion":
        # Check if distinguishing features visible to crawlers
        spec_blocks = [b for b in content_blocks if b.type == "specifications"]
        if spec_blocks:
            block_id = spec_blocks[0].id
            if block_id in visibility_matrix:
                vis = visibility_matrix[block_id]
                if vis.get("layer") == "js-rendered-only":
                    return RootCause(
                        type="js_rendering_gap",
                        detail="Distinguishing features only in JS-rendered content",
                        evidence_ids=[spec_blocks[0].evidence_id]
                    )
    
    return RootCause(
        type="unknown",
        detail="Could not determine root cause",
        evidence_ids=[]
    )

def map_to_fix_category(root_cause: RootCause) -> str:
    """Map root cause to fix category."""
    mapping = {
        "content_gap": "content_gap",
        "js_rendering_gap": "js_rendering_gap",
        "infrastructure_gap": "infrastructure_gap",
        "unknown": "unknown"
    }
    return mapping.get(root_cause.type, "unknown")

def generate_explanation(failure_type: str, root_cause: RootCause) -> str:
    """Generate plain-English explanation."""
    return f"{failure_type}: {root_cause.detail}"

def assess_geo_impact(dimension: str, failure_type: str) -> str:
    """Assess GEO impact of failure."""
    if dimension in ["entity_understanding", "comparison_selection"]:
        return "AI may recommend competitor product instead"
    elif dimension == "commercial_bridge":
        return "AI cannot complete purchase journey"
    elif dimension == "workflow_understanding":
        return "AI may recommend product for wrong use case"
    else:
        return "Reduced visibility in AI search results"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_report.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add stages/report.py tests/test_report.py
git commit -m "feat(stage5): dimension scoring and gap diagnosis"
```

---

*[Due to response length, continuing with Tasks 21-30 in final section...]*


