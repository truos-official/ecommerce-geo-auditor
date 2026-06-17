import pytest
from datetime import datetime
from core.context import AuditContext, Evidence, ContentBlock

def test_audit_context_creation():
    context = AuditContext(url="https://example.com/product/test-123")

    assert context.url == "https://example.com/product/test-123"
    assert context.product_id is None
    assert context.content_blocks == []
    assert context.agent_results == []
    assert isinstance(context.audit_timestamp, str)

def test_evidence_creation():
    evidence = Evidence(
        id="evt-123",
        type="http_response",
        source="fetch",
        timestamp=datetime.now().isoformat(),
        data={"status": 200}
    )

    assert evidence.id == "evt-123"
    assert evidence.type == "http_response"
    assert evidence.source == "fetch"
    assert evidence.data["status"] == 200

def test_content_block_creation():
    block = ContentBlock(
        id="blk-123",
        type="product_name",
        content="Test Product",
        xpath="/html/body/h1",
        char_count=12,
        visibility_layer="server-rendered"
    )

    assert block.id == "blk-123"
    assert block.type == "product_name"
    assert block.content == "Test Product"
    assert block.char_count == 12
