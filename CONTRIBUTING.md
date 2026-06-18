# Contributing to eCommerce GEO Auditor

## Development Setup

```bash
# Clone repo
git clone https://github.com/truos-official/ecommerce-geo-auditor.git
cd ecommerce-geo-auditor

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
# Edit .env with your API keys

# Run tests
pytest tests/ -v
```

## Running Tests

```bash
# All tests
pytest tests/ -v

# Specific module
pytest tests/test_extract.py -v

# Skip slow tests
pytest tests/ -m "not slow"

# Skip integration tests
pytest tests/ -m "not integration"
```

## Code Style

- Follow PEP 8
- Use type hints
- Add docstrings to public functions
- Keep functions under 50 lines
- Run `ruff check .` before committing

## TDD Workflow

1. Write failing test
2. Run test to verify it fails
3. Implement minimal code to pass
4. Run test to verify it passes
5. Commit with descriptive message

## Commit Messages

Format: `<type>: <description>`

Types:
- `feat`: New feature
- `fix`: Bug fix
- `test`: Add tests
- `docs`: Documentation
- `refactor`: Code refactoring
- `chore`: Maintenance

Example:
```
feat: add dual-mode agent client

- Add AgentClient with training/live modes
- Add tests for OpenAI/Anthropic/Google
- Add cost estimation
```

## Pull Requests

1. Fork the repo
2. Create feature branch
3. Make changes with tests
4. Run full test suite
5. Push and create PR
6. Wait for CI to pass

## Adding New Agents

1. Add agent config to `config.yaml`
2. Implement in `agents/client.py`
3. Add tests in `tests/test_agent_client.py`
4. Update README

## Questions?

Open an issue: https://github.com/truos-official/ecommerce-geo-auditor/issues
