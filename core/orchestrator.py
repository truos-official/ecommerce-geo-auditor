"""Main audit orchestrator."""

import json
from pathlib import Path
from datetime import datetime
from core.context import AuditContext
from core.config import load_config
from stages.stage1 import run_stage1
from stages.stage2 import run_stage2
from stages.stage3 import run_stage3
from stages.stage4 import run_stage4
from stages.stage5 import run_stage5


async def run_audit(url: str, config: dict, output_dir: str) -> AuditContext:
    """Run complete GEO audit pipeline."""

    print(f"Starting audit for: {url}")

    # Initialize context
    context = AuditContext(url=url)

    # Stage 1: Fetch & Import
    print("  Stage 1: Fetching...")
    context = await run_stage1(context, config)

    # Debug: check fetch success
    browser_response = context.http_responses.get("browser", {})
    if not browser_response.get("html"):
        print("  ! Warning: No HTML fetched from browser user agent")

    # Stage 2: Render
    print("  Stage 2: Rendering...")
    try:
        context = await run_stage2(context, config)
    except Exception as e:
        print(f"  Stage 2 skipped: {e}")

    # Stage 3: Extract & Classify
    print("  Stage 3: Extracting...")
    context = run_stage3(context, config)

    # Debug: check extraction success
    if not context.product_schema:
        print("  ! Warning: No product schema found")
    if not context.content_blocks:
        print("  ! Warning: No content blocks extracted")

    # Stage 4: AI Agent Prompting
    print("  Stage 4: Testing agents...")
    context = await run_stage4(context, config)

    # Stage 5: Gap Diagnosis
    print("  Stage 5: Diagnosing gaps...")
    context = run_stage5(context, config)

    # Generate outputs
    print("  Generating outputs...")
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    product_id = context.product_id or "unknown"
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

    # Full audit JSON
    audit_json_path = output_path / f"geo-audit-{product_id}-{timestamp}.json"

    # Serialize context (simplified - would need custom serializer)
    audit_data = {
        "url": context.url,
        "product_id": context.product_id,
        "product_category": context.product_category,
        "overall_score": context.overall_score,
        "geo_risk_level": context.geo_risk_level,
        "agent_results_count": len(context.agent_results),
        "gaps_count": len(context.gaps),
        "remediations_count": len(context.remediations),
        "audit_timestamp": context.audit_timestamp
    }

    audit_json_path.write_text(json.dumps(audit_data, indent=2))

    # HTML report
    from reports.html_generator import generate_html_report
    html_path = output_path / f"geo-audit-{product_id}-{timestamp}.html"
    generate_html_report(context, str(html_path))

    context.output_files = {
        "audit_json": str(audit_json_path),
        "html_report": str(html_path)
    }

    print(f"  [OK] Audit complete!")
    print(f"    Score: {context.overall_score}")
    print(f"    Risk: {context.geo_risk_level}")
    print(f"    JSON: {audit_json_path}")
    print(f"    HTML: {html_path}")

    return context
