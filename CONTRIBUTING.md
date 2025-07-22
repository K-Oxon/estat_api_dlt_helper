# Contributing to estat_api_dlt_helper

Thank you for your interest in contributing! We welcome contributions from everyone.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/[YOUR_ACCOUNT]/estat_api_dlt_helper.git`
3. Create a new branch: `git checkout -b feature/your-feature-name`

## Development Setup

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync --locked --all-extras --dev

# Run tests
uv run pytest -v
```

## Development Workflow

1. Make your changes
2. Run tests: `uv run pytest`
3. Check types: `uv run pyright src`
4. Run linter: `uv run ruff check src/`
5. Fix imports: `uv run ruff check src/ --select I --fix`
6. Format code: `uv run ruff format src/`
7. Commit your changes with a clear message
8. Push to your fork and submit a pull request

## Code Style

- Use Pydantic for data models
- Follow PEP 8
- Add type hints to all functions
- Keep functions small and focused

## Testing

- Write tests for new features
- Ensure all tests pass before submitting PR
- Aim for high test coverage

## Pull Request Guidelines

- Keep PRs focused on a single issue
- Update documentation as needed
- Follow the PR template
- Be responsive to feedback

## Reporting Issues

Use the issue templates to report bugs or request features. Provide as much detail as possible.

## Questions?

Feel free to open an issue for any questions about contributing.
