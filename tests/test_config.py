import pytest
import yaml
from pathlib import Path
from core.config import load_config, validate_config

def test_load_config_from_file():
    config = load_config("config.yaml")

    assert config["testing_scope"] == "flagship_only"
    assert "agents" in config
    assert "openai" in config["agents"]
    assert config["agents"]["openai"]["enabled"] is True

def test_load_config_missing_file():
    with pytest.raises(FileNotFoundError):
        load_config("nonexistent.yaml")

def test_validate_config_valid():
    config = {
        "testing_scope": "flagship_only",
        "agents": {
            "openai": {
                "enabled": True,
                "models": [{"name": "gpt-4o", "tier": "flagship"}]
            }
        }
    }

    is_valid = validate_config(config)
    assert is_valid is True

def test_validate_config_invalid_scope():
    config = {
        "testing_scope": "invalid",
        "agents": {}
    }

    with pytest.raises(ValueError, match="Invalid testing_scope"):
        validate_config(config)

def test_validate_config_no_agents():
    config = {
        "testing_scope": "flagship_only",
        "agents": {}
    }

    with pytest.raises(ValueError, match="No agents configured"):
        validate_config(config)

def test_get_enabled_agents():
    from core.config import get_enabled_agents

    config = {
        "agents": {
            "openai": {"enabled": True},
            "anthropic": {"enabled": False},
            "google": {"enabled": True}
        }
    }

    enabled = get_enabled_agents(config)

    assert "openai" in enabled
    assert "google" in enabled
    assert "anthropic" not in enabled
