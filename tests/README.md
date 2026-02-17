# Nodela SDK Test Suite

This directory contains comprehensive unit and integration tests for the Nodela Python SDK.

## Test Structure

```
tests/
├── conftest.py                      # Pytest fixtures and configuration
├── test_client.py                   # Tests for NodelaClient
├── test_exceptions.py               # Tests for exception classes
├── test_integration.py              # End-to-end integration tests
├── test_models_base.py              # Tests for base model
├── test_models_invoice.py           # Tests for invoice models
├── test_models_transaction.py       # Tests for transaction models
├── test_package.py                  # Tests for package exports
├── test_resources_invoices.py       # Tests for invoices resource
├── test_resources_transactions.py   # Tests for transactions resource
└── test_utils_http.py               # Tests for HTTP client utilities
```

## Running Tests

### Run all tests
```bash
pytest
```

### Run with coverage
```bash
pytest --cov=src/nodela --cov-report=html
```

### Run specific test file
```bash
pytest tests/test_client.py
```

### Run specific test class
```bash
pytest tests/test_client.py::TestNodelaClientInitialization
```

### Run specific test
```bash
pytest tests/test_client.py::TestNodelaClientInitialization::test_initialization_with_api_key
```

### Run tests with verbose output
```bash
pytest -v
```

### Run tests and show local variables on failure
```bash
pytest -l
```

### Run only unit tests
```bash
pytest -m unit
```

### Run only integration tests
```bash
pytest -m integration
```

## Test Categories

### Unit Tests
- **test_exceptions.py**: Tests for all exception classes
- **test_models_base.py**: Tests for the base Pydantic model
- **test_models_invoice.py**: Tests for invoice-related models
- **test_models_transaction.py**: Tests for transaction-related models
- **test_utils_http.py**: Tests for HTTP client functionality
- **test_resources_invoices.py**: Tests for invoice resource methods
- **test_resources_transactions.py**: Tests for transaction resource methods
- **test_client.py**: Tests for the main NodelaClient class

### Integration Tests
- **test_integration.py**: End-to-end tests that verify the complete workflow
- **test_package.py**: Tests for package structure and exports

## Test Coverage

The test suite aims for >90% code coverage across all modules:

- ✅ **Exceptions**: 100% coverage of all exception classes
- ✅ **Models**: Complete coverage of model initialization, validation, serialization
- ✅ **HTTP Client**: All HTTP methods, error handling, retry logic
- ✅ **Resources**: All resource methods and endpoint building
- ✅ **Client**: Initialization, configuration, resource access
- ✅ **Integration**: End-to-end workflows, error scenarios

## Fixtures

Common fixtures are defined in `conftest.py`:

- `api_key`: Test API key
- `base_url`: Test base URL
- `http_client`: Configured HTTPClient instance
- `nodela_client`: Configured NodelaClient instance
- `mock_invoice_response_data`: Mock invoice creation response
- `mock_verify_invoice_response_data`: Mock invoice verification response
- `mock_list_transactions_response_data`: Mock transaction list response
- `mock_error_response_data`: Mock error response

## Type Checking

All tests are fully typed using Python's type hints. Run mypy to verify:

```bash
mypy tests/
```

## Best Practices

1. **Full Type Coverage**: All test functions, parameters, and return values are typed
2. **Descriptive Names**: Test names clearly describe what is being tested
3. **Arrange-Act-Assert**: Tests follow AAA pattern
4. **Isolated Tests**: Each test is independent and can run in any order
5. **Mocking**: External dependencies are mocked appropriately
6. **Comprehensive**: Tests cover success cases, error cases, edge cases
7. **Documentation**: Each test has a clear docstring

## Adding New Tests

When adding new tests:

1. Create test file with `test_` prefix
2. Create test classes with `Test` prefix
3. Create test methods with `test_` prefix
4. Add type hints to all parameters and return values
5. Add docstrings to all test methods
6. Use existing fixtures from conftest.py
7. Mock external dependencies
8. Test both success and failure scenarios

## Continuous Integration

These tests are designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    pip install -e ".[dev]"
    pytest --cov --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v3
```

## Debugging Tests

### Run with Python debugger
```bash
pytest --pdb
```

### Show print statements
```bash
pytest -s
```

### Run last failed tests
```bash
pytest --lf
```

### Run failed tests first
```bash
pytest --ff
```

## Performance

The test suite is designed to run quickly:

- Unit tests use mocking to avoid network calls
- Fixtures are reused where appropriate
- Tests are parallelizable (can use pytest-xdist)

### Run tests in parallel
```bash
pip install pytest-xdist
pytest -n auto
```
