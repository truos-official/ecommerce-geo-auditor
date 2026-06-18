import pytest
from stages.extract import (
    extract_json_ld, find_product_schema, parse_product_schema,
    extract_content_blocks, build_visibility_matrix
)

def test_extract_json_ld():
    html = '''<html><head>
    <script type="application/ld+json">
    {"@type": "Product", "name": "Test Product"}
    </script>
    </head></html>'''

    blocks = extract_json_ld(html)
    assert len(blocks) == 1
    assert blocks[0]["@type"] == "Product"

def test_find_product_schema():
    json_ld_blocks = [
        {"@type": "WebPage"},
        {"@type": "Product", "name": "Test"},
        {"@type": "Organization"}
    ]

    schema = find_product_schema(json_ld_blocks)
    assert schema is not None
    assert schema["@type"] == "Product"

def test_parse_product_schema():
    schema = {
        "sku": "TEST-001",
        "name": "Test Product",
        "description": "A test product",
        "offers": {
            "price": "99.99",
            "priceCurrency": "USD",
            "availability": "InStock"
        }
    }

    parsed = parse_product_schema(schema)
    assert parsed.product_id == "TEST-001"
    assert parsed.name == "Test Product"
    assert parsed.price == "99.99"

def test_extract_content_blocks():
    html = '''<html><body>
    <h1>Test Product</h1>
    <meta name="description" content="This is a test product">
    <p>Description here</p>
    <table><tr><td>Spec 1</td><td>Value 1</td></tr></table>
    </body></html>'''

    blocks = extract_content_blocks(html, "https://example.com")
    assert len(blocks) > 0
    assert any(b.type == "product_name" for b in blocks)

def test_build_visibility_matrix():
    from core.context import ContentBlock

    blocks = [
        ContentBlock(
            id="blk-1",
            type="product_name",
            content="Test Product",
            xpath="//h1",
            char_count=12,
            visibility_layer="server-rendered"
        )
    ]

    http_responses = {
        "browser": {"html": "<h1>Test Product</h1>"},
        "googlebot": {"html": "<h1>Test Product</h1>"},
        "bingbot": {"html": "<div>Other content</div>"}
    }

    matrix = build_visibility_matrix(blocks, http_responses)
    assert matrix["blk-1"]["browser"] is True
    assert matrix["blk-1"]["googlebot"] is True
    assert matrix["blk-1"]["bingbot"] is False
