# Architecture Overview

## 5-Stage Pipeline

```
Stage 1: Fetch & Import
  ├─ HTTP fetching (6 user agents)
  ├─ PowerShell cache import
  └─ Locale validation

Stage 2: Render
  ├─ Playwright lazy-load simulation
  └─ JS-rendered diff calculation

Stage 3: Extract & Classify
  ├─ Content block extraction
  ├─ Visibility matrix
  ├─ Product schema parsing
  ├─ Category classification
  └─ Crawler coverage scoring

Stage 4: AI Agent Prompting
  ├─ Reference facts generation
  ├─ Unbranded query construction
  ├─ Dual-mode testing (training + live)
  ├─ Retrieval analysis
  ├─ Traffic analysis
  └─ Competitor discovery

Stage 5: Gap Diagnosis & Reports
  ├─ Root cause analysis
  ├─ Remediation prioritization
  ├─ Content value ranking
  ├─ Cross-agent retrieval matrix
  └─ Report generation (HTML/PDF)
```

## Data Flow

```
URL
 ↓
AuditContext (initialized)
 ↓
Stage 1 → http_responses, locale_valid
 ↓
Stage 2 → lazy_loaded_content, js_rendered_diff
 ↓
Stage 3 → content_blocks, visibility_matrix, product_schema
 ↓
Stage 4 → agent_results, competitors, content_value_rankings
 ↓
Stage 5 → gaps, remediations, overall_score
 ↓
Output Files (JSON, HTML, PDF)
```

## Key Design Decisions

### Monolithic Pipeline
- Single AuditContext flows through all stages
- Stages modify context in place
- Evidence trail tracks all operations

### Dual-Mode Testing
- Training mode: No web access (tests training data staleness)
- Live mode: With web access (tests retrieval quality)
- Compares both to identify GEO gaps

### Unbranded Prompts
- Generic queries without brand/catalog numbers
- Tests real-world discovery
- Example: "I need cell culture medium" vs "Order C-22010"

### Auto-Competitor Discovery
- No manual competitor lists
- Detects product pages in cited URLs
- Classifies as competitor vs generic source

### Content Value Ranking
- Extraction rate × usage rate × citation correlation
- Identifies high-value vs low-value content blocks
- Guides content optimization priorities

## Module Organization

```
core/
  ├─ context.py      # Data structures
  └─ config.py       # Configuration loader

stages/
  ├─ stage1.py       # HTTP fetching
  ├─ stage2.py       # Playwright rendering
  ├─ extract.py      # Content extraction
  ├─ classify.py     # Category classification
  ├─ prompts.py      # Prompt generation
  ├─ scoring.py      # Response scoring
  ├─ retrieval_analysis.py
  ├─ traffic_analysis.py
  └─ stage5.py       # Gap diagnosis (TODO)

agents/
  └─ client.py       # AI agent client

reports/
  └─ html_generator.py  # Report generation (TODO)

tests/
  └─ test_*.py       # Unit tests per module
```

## Extension Points

### Adding New Agents
1. Add config to `config.yaml`
2. Implement method in `agents/client.py`
3. Handle agent-specific response format
4. Add tests

### Adding New Content Block Types
1. Add type to `config.yaml` content_extraction
2. Add extraction logic in `stages/extract.py`
3. Add weight to coverage calculation

### Adding New Dimensions
1. Add template to `prompts/templates.yaml`
2. Add to dimension list in `stages/prompts.py`
3. Update scoring logic

## Performance Considerations

- Async HTTP fetching (6 agents in parallel)
- Playwright runs once per URL (expensive)
- Agent API calls are sequential (rate limits)
- Cost: ~$1.16/URL in flagship-only mode

## Testing Strategy

- Unit tests for all modules (51 total)
- Integration tests for full pipeline (TODO)
- Mocks for external APIs
- Fixtures for test data
