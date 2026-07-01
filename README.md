# eCommerce GEO Auditor

Python CLI tool for auditing eCommerce product pages for Generative Engine Optimization (GEO).

## Overview

Tests whether AI agents (ChatGPT, Anthropic, Gemini, Perplexity, Bing Copilot) cite product pages vs answering generically vs citing competitors. Identifies traffic-driving vs traffic-diverting content.

## Features

- **Dual-mode testing**: Training data (no web) + live retrieval (with web)
- **Multi-agent support**: OpenAI, Anthropic, Google, Perplexity, Bing/Azure
- **Unbranded prompts**: Generic queries without brand/catalog numbers
- **Auto-competitor discovery**: Detects competitor product pages from cited URLs
- **Content value ranking**: Score content blocks by extraction/usage/citation correlation
- **Traffic impact analysis**: Citation format, click likelihood, business impact
- **Cross-agent retrieval matrix**: Diagnose Google Search visibility issues
- **Comprehensive reports**: HTML with remediation priorities

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

### Interactive Mode

```bash
python cli.py --interactive
```

### File Mode

Create `urls.txt`:
```
https://example.com/product/abc123
https://example.com/product/xyz789
```

Run:
```bash
python cli.py --urls-file urls.txt
```

## Cost Estimate

- **Flagship-only mode** (default): ~$1.16/URL
- **10 URLs**: ~$12
- **Full multi-model mode**: ~$5/URL

## Configuration

Edit `config.yaml`:

```yaml
testing_scope: flagship_only  # or "multi_model"

agents:
  openai:
    enabled: true
    test_training_mode: true
    models:
      - name: gpt-4o
        tier: flagship
      - name: o3-mini
        tier: reasoning

  google:
    enabled: true
    models:
      - name: gemini-2.0-flash-exp
        tier: flagship

  anthropic:
    enabled: true
    models:
      - name: claude-sonnet-4
        tier: flagship

  perplexity:
    enabled: true
    models:
      - name: sonar-pro
        tier: flagship

  bing:
    enabled: true
    bing_grounding: true
```

## Environment Variables

Create `.env`:

```bash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
PERPLEXITY_API_KEY=pplx-...
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_ENDPOINT=https://...
BING_SEARCH_ENDPOINT=https://...
SERPAPI_KEY=...  # For sibling discovery
```

## Output Files

Per URL:

1. `geo-audit-{id}-{timestamp}.json` - Full audit data
2. `geo-audit-failures-{id}-{timestamp}.json` - Failed prompts with diagnosis
3. `geo-retrieval-analysis-{id}-{timestamp}.json` - Retrieval behavior analysis
4. `geo-content-value-{id}-{timestamp}.json` - Content block rankings
5. `geo-competitors-{id}-{timestamp}.json` - Auto-discovered competitors
6. `geo-audit-report-{id}-{timestamp}.html` - HTML report
7. `geo-audit-report-{id}-{timestamp}.pdf` - PDF report

## Architecture

5-stage pipeline:

1. **Fetch & Import**: HTTP + PowerShell cache import
2. **Render**: Playwright lazy-load simulation
3. **Extract & Classify**: Content blocks, visibility matrix, product category
4. **AI Agent Prompting**: Dual-mode testing, retrieval analysis, traffic analysis
5. **Gap Diagnosis**: Root cause mapping, remediation prioritization

## Documentation

- [Design Specification](docs/superpowers/specs/2026-06-16-geo-audit-tool-design.md)
- [Implementation Plan](docs/superpowers/plans/2026-06-16-geo-audit-tool.md)
- [Usage Guide](docs/USAGE.md)

## License

MIT

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md)
