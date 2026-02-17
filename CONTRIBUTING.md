# Contributing to Nodela Python SDK

Thank you for your interest in contributing to the Nodela Python SDK! This guide will help you get started.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [Code Style](#code-style)
- [Testing](#testing)
- [Commit Conventions](#commit-conventions)
- [Pull Request Process](#pull-request-process)
- [Reporting Issues](#reporting-issues)

## Code of Conduct

By participating in this project, you agree to maintain a respectful, inclusive, and harassment-free environment for everyone. Please be considerate in your communication and contributions.

## Getting Started

1. **Fork** the repository on GitHub.
2. **Clone** your fork locally:
   ```bash
   git clone https://github.com/<your-username>/nodela-python-sdk.git
   cd nodela-python-sdk
   ```
3. **Add the upstream remote:**
   ```bash
   git remote add upstream https://github.com/Devkrea8-Technologies/nodela-python-sdk.git
   ```

## Development Setup

### Prerequisites

- Python 3.9 or higher
- pip
- Git

### Install dependencies

The project uses a Makefile to streamline common tasks. To install the package with all development dependencies:

```bash
make dev-install
```

This will:
- Install the package in editable mode (`pip install -e ".[dev]"`)
- Set up pre-commit hooks

### Manual setup (alternative)

```bash
python -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pre-commit install
```

## Project Structure

```
nodela-python-sdk/
├── src/
│   └── nodela/
│       ├── __init__.py           # Package exports
│       ├── client.py             # NodelaClient main class
│       ├── exceptions.py         # Custom exception hierarchy
│       ├── models/
│       │   ├── base.py           # Base Pydantic model
│       │   ├── invoice.py        # Invoice request/response models
│       │   └── transaction.py    # Transaction models
│       ├── resources/
│       │   ├── base.py           # Base resource class
│       │   ├── invoices.py       # Invoices API resource
│       │   └── transactions.py   # Transactions API resource
│       └── utils/
│           └── http.py           # HTTP client with retry logic
├── tests/
│   ├── conftest.py               # Shared fixtures
│   ├── test_client.py            # Client tests
│   ├── test_exceptions.py        # Exception tests
│   ├── test_models_*.py          # Model tests
│   ├── test_resources_*.py       # Resource tests
│   ├── test_utils_http.py        # HTTP client tests
│   └── test_integration.py       # Integration tests
├── pyproject.toml                # Project configuration
├── makefile                      # Development commands
└── pytest.ini                    # Test configuration
```

## Development Workflow

### 1. Create a feature branch

```bash
git checkout -b feat/your-feature-name
```

Use branch prefixes that match conventional commit types:
- `feat/` for new features
- `fix/` for bug fixes
- `docs/` for documentation changes
- `refactor/` for code refactoring
- `test/` for test additions or changes

### 2. Make your changes

- Write code following the project's [code style](#code-style)
- Add or update tests as appropriate
- Ensure all tests pass before committing

### 3. Format and lint

```bash
make format    # Auto-format with Black and Ruff
make lint      # Check with Ruff and mypy
```

### 4. Run tests

```bash
make test              # Run all tests
make test-coverage     # Run tests with coverage report
```

### 5. Commit your changes

```bash
make commit    # Uses Commitizen for conventional commits
```

Or manually:

```bash
git add <files>
git commit -m "feat: add new payment method support"
```

### 6. Push and create a Pull Request

```bash
git push origin feat/your-feature-name
```

Then open a Pull Request against the `main` branch on GitHub.

## Code Style

This project enforces consistent code style through automated tooling:

- **[Black](https://github.com/psf/black)** - Code formatting (line length: 100)
- **[Ruff](https://github.com/astral-sh/ruff)** - Linting (line length: 100, rules: E, F, I, N, W)
- **[mypy](https://mypy-lang.org/)** - Static type checking (strict mode)

### Key conventions

- **Type annotations** are required on all function signatures.
- **Docstrings** should use the Google style for public classes and methods.
- **Line length** is limited to 100 characters.
- **Imports** should be sorted (enforced by Ruff's `I` rules).

### Pre-commit hooks

Pre-commit hooks run automatically on each commit to enforce formatting, linting, and commit message conventions. If a hook fails, fix the issues and re-commit.

To run all hooks manually:

```bash
pre-commit run --all-files
```

## Testing

Tests are written with [pytest](https://pytest.org/) and live in the `tests/` directory.

### Running tests

```bash
# All tests
make test

# With coverage report
make test-coverage

# Specific test file
pytest tests/test_client.py

# Specific test
pytest tests/test_client.py::TestNodelaClient::test_init_with_api_key

# By marker
pytest -m unit
pytest -m integration
```

### Test markers

- `@pytest.mark.unit` - Unit tests (fast, no external dependencies)
- `@pytest.mark.integration` - Integration tests (may require API access)
- `@pytest.mark.slow` - Slow-running tests

### Writing tests

- Place test files in `tests/` with the `test_` prefix.
- Use fixtures from `conftest.py` for common setup (e.g., `http_client`, `nodela_client`).
- Mock external HTTP calls - do not make real API requests in unit tests.
- Aim for **90%+ code coverage** (enforced by CI).

### Example test

```python
def test_create_invoice_success(self, invoices, http_client, mock_invoice_response_data):
    http_client.post.return_value = mock_invoice_response_data

    params = CreateInvoiceParams(amount=100.0, currency="USD")
    response = invoices.create(params)

    assert response.success is True
    assert response.data.invoice_id == "INV-123"
    http_client.post.assert_called_once()
```

## Commit Conventions

This project uses [Conventional Commits](https://www.conventionalcommits.org/) enforced by [Commitizen](https://commitizen-tools.github.io/commitizen/).

### Format

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Types

| Type | Description |
|------|-------------|
| `feat` | A new feature |
| `fix` | A bug fix |
| `docs` | Documentation changes |
| `style` | Code style changes (formatting, no logic change) |
| `refactor` | Code changes that neither fix a bug nor add a feature |
| `perf` | Performance improvements |
| `test` | Adding or updating tests |
| `build` | Build system or dependency changes |
| `ci` | CI configuration changes |
| `chore` | Other changes that don't modify src or test files |

### Examples

```
feat(invoices): add bulk invoice creation support
fix(http): handle timeout errors during retry
docs: update installation instructions in README
test(transactions): add pagination edge case tests
```

Use `make commit` to get an interactive prompt that guides you through the format.

## Pull Request Process

1. **Ensure your branch is up to date** with `main`:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **All checks must pass:**
   - Tests pass (`make test`)
   - Code is formatted (`make format`)
   - Linting passes (`make lint`)
   - Commit messages follow conventions

3. **Write a clear PR description** that includes:
   - What the change does and why
   - How to test it
   - Any breaking changes

4. **Keep PRs focused.** One feature or fix per PR. Large changes should be broken into smaller, reviewable pieces.

5. **Respond to review feedback** promptly. Push additional commits to address comments rather than force-pushing.

6. A maintainer will review and merge your PR once all checks pass and the code is approved.

## Reporting Issues

Found a bug or have a feature request? [Open an issue](https://github.com/Devkrea8-Technologies/nodela-python-sdk/issues/new) with:

- **Bug reports:** Steps to reproduce, expected behavior, actual behavior, Python version, and SDK version.
- **Feature requests:** Description of the desired behavior and the use case it addresses.

## Questions?

If you have questions about contributing, feel free to [open a discussion](https://github.com/Devkrea8-Technologies/nodela-python-sdk/issues) or reach out to the team at sayhello@nodela.co.
