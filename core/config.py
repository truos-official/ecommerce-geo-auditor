"""Configuration loader and validator."""

import yaml
from pathlib import Path


def load_config(config_path: str) -> dict:
    """Load configuration from YAML file."""
    path = Path(config_path)

    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with path.open("r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    validate_config(config)

    return config


def validate_config(config: dict) -> bool:
    """Validate configuration structure and values."""
    # Check testing scope
    valid_scopes = ["flagship_only", "multi_model"]
    if config.get("testing_scope") not in valid_scopes:
        raise ValueError(f"Invalid testing_scope: {config.get('testing_scope')}. Must be one of {valid_scopes}")

    # Check agents
    agents = config.get("agents", {})
    if not agents:
        raise ValueError("No agents configured")

    # Validate each enabled agent has models
    for agent_name, agent_config in agents.items():
        if agent_config.get("enabled", True):
            models = agent_config.get("models", [])
            if not models:
                raise ValueError(f"Agent {agent_name} is enabled but has no models configured")

    return True


def get_enabled_agents(config: dict) -> list[str]:
    """Get list of enabled agent names."""
    agents = config.get("agents", {})
    enabled = []

    for agent_name, agent_config in agents.items():
        if agent_config.get("enabled", True):
            enabled.append(agent_name)

    return enabled


def get_models_for_agent(config: dict, agent_name: str, tier: str | None = None) -> list[dict]:
    """Get models for specific agent, optionally filtered by tier."""
    agents = config.get("agents", {})

    if agent_name not in agents:
        return []

    agent_config = agents[agent_name]
    models = agent_config.get("models", [])

    if tier:
        models = [m for m in models if m.get("tier") == tier]

    return models
