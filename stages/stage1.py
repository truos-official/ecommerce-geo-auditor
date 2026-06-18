"""Stage 1: Fetch & Import."""

import re
import httpx
from typing import Any
from core.context import AuditContext


async def fetch_with_user_agent(url: str, user_agent: str, timeout: int = 30) -> dict[str, Any]:
    """Fetch URL with specific user agent."""
    try:
        async with httpx.AsyncClient(timeout=timeout, verify=False) as client:
            response = await client.get(
                url,
                headers={"User-Agent": user_agent},
                follow_redirects=True
            )

            return {
                "status_code": response.status_code,
                "html": response.text,
                "headers": dict(response.headers),
                "error": None
            }

    except Exception as e:
        return {
            "status_code": 0,
            "html": "",
            "headers": {},
            "error": str(e)
        }


def validate_locale(url: str) -> bool:
    """Validate URL contains locale pattern (e.g., /US/en/)."""
    # Pattern: /COUNTRY/LANG/
    locale_pattern = r'/[A-Z]{2}/[a-z]{2}/'
    return bool(re.search(locale_pattern, url))


async def run_stage1(context: AuditContext, config: dict) -> AuditContext:
    """Stage 1: Fetch URL with multiple user agents."""
    url = context.url

    # Get user agents from config
    user_agents = config.get("crawlers", {}).get("user_agents", {})
    timeout = config.get("crawlers", {}).get("timeout", 30)

    # Fetch with each user agent
    for agent_name, user_agent in user_agents.items():
        result = await fetch_with_user_agent(url, user_agent, timeout)
        context.http_responses[agent_name] = result

        # Debug logging
        if result.get("error"):
            print(f"    {agent_name}: ERROR - {result['error']}")
        elif not result.get("html"):
            print(f"    {agent_name}: No HTML (status {result.get('status_code')})")
        else:
            html_len = len(result.get("html", ""))
            print(f"    {agent_name}: OK ({html_len} bytes)")

    # Validate locale
    context.locale_valid = validate_locale(url)

    # Check for PowerShell cache (would be imported here if exists)
    # For now, just mark as None
    context.powershell_cache = None

    return context
