import pytest
from stages.classify import classify_product_category, calculate_crawler_coverage
from core.context import ContentBlock

def test_classify_cell_culture():
    category, confidence = classify_product_category(
        "Endothelial Cell Growth Medium",
        "Complete medium for cell culture"
    )
    assert category == "cell_culture_media"
    assert confidence > 0.8

def test_classify_chemical():
    category, confidence = classify_product_category(
        "Sodium Chloride",
        "Reagent grade chemical"
    )
    assert category == "chemical_reagent"
    assert confidence > 0.8

def test_classify_antibody():
    category, confidence = classify_product_category(
        "Anti-Mouse IgG",
        "Monoclonal antibody for research"
    )
    assert category == "antibody"
    assert confidence > 0.9

def test_calculate_crawler_coverage():
    blocks = [
        ContentBlock(
            id="blk-1",
            type="product_name",
            content="Test",
            xpath="//h1",
            char_count=4,
            visibility_layer="server-rendered"
        ),
        ContentBlock(
            id="blk-2",
            type="description",
            content="Desc",
            xpath="//p",
            char_count=4,
            visibility_layer="server-rendered"
        )
    ]

    visibility_matrix = {
        "blk-1": {"browser": True, "googlebot": True},
        "blk-2": {"browser": True, "googlebot": False}
    }

    weights = {
        "product_name": 0.6,
        "description": 0.4
    }

    scores = calculate_crawler_coverage(visibility_matrix, blocks, weights)
    assert scores["browser"] == 1.0
    assert scores["googlebot"] == 0.6
