"""Stage 3: Content block extraction."""

import uuid
from bs4 import BeautifulSoup
from core.context import ContentBlock, ProductSchema
from typing import Any


def extract_json_ld(html: str) -> list[dict]:
    """Extract JSON-LD blocks from HTML."""
    import json
    soup = BeautifulSoup(html, 'html.parser')
    json_ld_blocks = []

    for script in soup.find_all('script', type='application/ld+json'):
        try:
            data = json.loads(script.string)
            json_ld_blocks.append(data)
        except:
            continue

    return json_ld_blocks


def find_product_schema(json_ld_blocks: list[dict]) -> dict | None:
    """Find Product schema from JSON-LD blocks."""
    for block in json_ld_blocks:
        if isinstance(block, dict) and block.get("@type") == "Product":
            return block

    return None


def parse_product_schema(schema: dict) -> ProductSchema:
    """Parse Product schema into ProductSchema object."""
    offer = schema.get("offers", {})
    if isinstance(offer, list):
        offer = offer[0] if offer else {}

    return ProductSchema(
        raw=schema,
        product_id=schema.get("sku"),
        name=schema.get("name"),
        description=schema.get("description"),
        price=offer.get("price"),
        currency=offer.get("priceCurrency"),
        availability=offer.get("availability")
    )


def extract_content_blocks(html: str, url: str) -> list[ContentBlock]:
    """Extract semantic content blocks from HTML."""
    soup = BeautifulSoup(html, 'html.parser')
    blocks = []

    # Extract product name (h1)
    h1 = soup.find('h1')
    if h1:
        blocks.append(ContentBlock(
            id=f"blk-{uuid.uuid4().hex[:8]}",
            type="product_name",
            content=h1.get_text(strip=True),
            xpath="//h1",
            char_count=len(h1.get_text(strip=True)),
            visibility_layer="server-rendered"
        ))

    # Extract description (meta description or first p)
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    if meta_desc and meta_desc.get('content'):
        blocks.append(ContentBlock(
            id=f"blk-{uuid.uuid4().hex[:8]}",
            type="product_description",
            content=meta_desc.get('content'),
            xpath="//meta[@name='description']",
            char_count=len(meta_desc.get('content')),
            visibility_layer="server-rendered"
        ))

    # Extract specifications (tables, dl, etc)
    for table in soup.find_all('table')[:3]:  # Max 3 tables
        text = table.get_text(strip=True)
        if len(text) > 20:
            blocks.append(ContentBlock(
                id=f"blk-{uuid.uuid4().hex[:8]}",
                type="specifications",
                content=text[:500],  # Truncate
                xpath="//table",
                char_count=len(text),
                visibility_layer="server-rendered"
            ))

    return blocks


def build_visibility_matrix(
    content_blocks: list[ContentBlock],
    http_responses: dict[str, dict]
) -> dict[str, dict[str, bool]]:
    """Build visibility matrix showing which agents see which blocks."""
    matrix = {}

    for block in content_blocks:
        block_visibility = {}

        for agent_name, response in http_responses.items():
            html = response.get("html", "")
            # Simple check: is block content in HTML?
            block_visibility[agent_name] = block.content in html

        matrix[block.id] = block_visibility

    return matrix
