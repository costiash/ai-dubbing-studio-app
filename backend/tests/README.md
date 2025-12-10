# Backend Testing Suite

Comprehensive testing suite for AI Dubbing Studio backend API.

## Table of Contents

- [Overview](#overview)
- [Test Structure](#test-structure)
- [Running Tests](#running-tests)
- [Test Categories](#test-categories)
- [Coverage Requirements](#coverage-requirements)
- [Writing Tests](#writing-tests)
- [CI/CD Integration](#cicd-integration)

## Overview

This testing suite provides comprehensive coverage for the AI Dubbing Studio backend, including:

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test complete workflows across components
- **Security Tests**: Validate input handling and security measures
- **Fixtures & Mocks**: Reusable test data and OpenAI API mocks

**Coverage Goals:**
- Overall: 80%+ line coverage
- Critical paths: 100% coverage
- Core services: 85%+ coverage

## Test Structure

```
backend/tests/
├── __init__.py                    # Package initialization
├── conftest.py                    # Pytest configuration & global fixtures
├── README.md                      # This file
│
├── fixtures/                      # Test fixtures and mocks
│   ├── __init__.py
│   ├── test_data.py              # Test constants and sample data
│   └── openai_mocks.py           # OpenAI API mock responses
│
├── test_config.py                 # Tests for configuration
├── test_exceptions.py             # Tests for custom exceptions
├── test_openai_client.py          # Tests for OpenAI service
├── test_audio_converter.py        # Tests for audio conversion
├── test_file_handlers.py          # Tests for file utilities
├── test_health_routes.py          # Tests for health endpoint
├── test_audio_routes.py           # Tests for audio endpoints
│
├── integration/                   # Integration tests
│   ├── __init__.py
│   └── test_complete_flows.py    # End-to-end workflow tests
│
└── security/                      # Security tests
    ├── __init__.py
    └── test_input_validation.py   # Input validation & security
```

## Running Tests

### Prerequisites

1. **Install dependencies:**
   ```bash
   uv sync --all-groups
   ```

2. **Install FFmpeg** (required for audio conversion):
   ```bash
   # macOS
   brew install ffmpeg

   # Ubuntu/Debian
   sudo apt-get install ffmpeg

   # Windows
   # Download from https://ffmpeg.org/download.html
   ```

3. **Set up environment** (optional):
   ```bash
   export OPENAI_API_KEY="sk-test-key-12345"
   ```
   Note: Tests use mocks, so a real API key is not required.

### Run All Tests

```bash
# Run all tests with coverage
uv run pytest

# Run with verbose output
uv run pytest -v

# Run with coverage report
uv run pytest --cov=backend --cov-report=term-missing --cov-report=html
```

### Run by Category

```bash
# Unit tests only
uv run pytest -m unit

# Integration tests
uv run pytest -m integration

# Security tests
uv run pytest -m security

# Slow tests
uv run pytest -m "not slow"  # Skip slow tests
```

### Run Specific Test Files

```bash
# Single test file
uv run pytest backend/tests/test_openai_client.py

# Specific test class
uv run pytest backend/tests/test_openai_client.py::TestOpenAIService

# Specific test function
uv run pytest backend/tests/test_openai_client.py::TestOpenAIService::test_transcribe_audio_success
```

### Run with Different Output Formats

```bash
# Detailed output
uv run pytest -v --tb=short

# Quiet mode (only errors)
uv run pytest -q

# Show local variables on failure
uv run pytest -l

# Stop on first failure
uv run pytest -x

# Show test durations
uv run pytest --durations=10
```

### Watch Mode (Re-run on file changes)

```bash
# Install pytest-watch
uv add --dev pytest-watch

# Run in watch mode
uv run ptw
```

## Test Categories

### Unit Tests (`@pytest.mark.unit`)

Test individual components in isolation with mocked dependencies.

**Files:**
- `test_config.py` - Configuration loading and validation
- `test_exceptions.py` - Custom exception classes
- `test_openai_client.py` - OpenAI service methods (mocked API)
- `test_audio_converter.py` - Audio conversion (mocked pydub)
- `test_file_handlers.py` - File utilities and validation
- `test_health_routes.py` - Health check endpoint
- `test_audio_routes.py` - Audio API endpoints (mocked services)

**Run:**
```bash
uv run pytest -m unit -v
```

### Integration Tests (`@pytest.mark.integration`)

Test complete workflows across multiple components.

**Files:**
- `integration/test_complete_flows.py` - End-to-end workflows

**Examples:**
- Upload → Transcribe → Translate → TTS
- Error recovery scenarios
- Concurrent requests
- Multiple audio formats

**Run:**
```bash
uv run pytest -m integration -v
```

### Security Tests (`@pytest.mark.security`)

Validate input handling, file security, and attack prevention.

**Files:**
- `security/test_input_validation.py` - Security validation

**Test Areas:**
- File upload security (malicious files, path traversal)
- XSS prevention
- SQL injection prevention
- Unicode handling
- DoS prevention
- Error message safety

**Run:**
```bash
uv run pytest -m security -v
```

### Slow Tests (`@pytest.mark.slow`)

Tests that take significant time to run.

**Skip slow tests:**
```bash
uv run pytest -m "not slow"
```

## Coverage Requirements

### Coverage Targets

| Component | Target Coverage | Current |
|-----------|----------------|---------|
| Overall | 80%+ | 86.28% ✅ |
| Core Services | 85%+ | 96.15% ✅ |
| API Routes | 80%+ | 80.00% ✅ |
| Schemas & Exceptions | 100% | 100% ✅ |

### View Coverage Report

```bash
# Generate HTML report
uv run pytest --cov=backend --cov-report=html

# Open in browser
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Coverage Configuration

Coverage is configured in `pyproject.toml`:

```toml
[tool.coverage.run]
source = ["backend"]
omit = [
    "*/tests/*",
    "*/__init__.py",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
]
```

## Writing Tests

### Test Structure (AAA Pattern)

```python
def test_function_behavior(self) -> None:
    """Test description."""
    # ARRANGE: Set up test data and mocks
    input_data = "test input"
    expected_output = "expected result"

    # ACT: Execute the function being tested
    result = function_under_test(input_data)

    # ASSERT: Verify the results
    assert result == expected_output
```

### Using Fixtures

```python
def test_with_fixtures(
    self,
    client: TestClient,
    mock_openai_service: OpenAIService,
    sample_audio_file: BinaryIO,
) -> None:
    """Test using pytest fixtures."""
    # Fixtures are automatically injected
    response = client.post("/v1/audio/transcribe", files={"file": sample_audio_file})
    assert response.status_code == 200
```

### Mocking FastAPI Dependencies

**⚠️ Important:** Standard `patch()` does NOT work for FastAPI dependencies. Use `app.dependency_overrides`:

```python
from backend.api.main import app
from backend.services.openai_client import get_openai_service

class MockOpenAIService:
    def __init__(self) -> None:
        self.api_key = "sk-test"  # Required by health endpoint
        self.transcribe_audio = AsyncMock(return_value=("Text", "en"))
        self.translate_text = AsyncMock(return_value="Translated")
        self.generate_speech = AsyncMock(return_value=b"audio")

@pytest.fixture
def client_with_mock(mock_service: MockOpenAIService) -> Generator[TestClient]:
    app.dependency_overrides[get_openai_service] = lambda: mock_service
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
```

### Mocking OpenAI API

```python
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_transcription(self) -> None:
    """Test with mocked OpenAI API."""
    with patch("backend.services.openai_client.AsyncOpenAI") as mock_client:
        mock_client.audio.transcriptions.create = AsyncMock(
            return_value={"text": "Test transcription", "language": "en"}
        )

        # Test code here
```

### Testing Async Functions

```python
@pytest.mark.asyncio
async def test_async_function(self) -> None:
    """Test async function."""
    result = await async_function()
    assert result is not None
```

### Parametrized Tests

```python
@pytest.mark.parametrize("input,expected", [
    ("hello", "hola"),
    ("goodbye", "adiós"),
    ("thank you", "gracias"),
])
def test_translations(self, input: str, expected: str) -> None:
    """Test multiple translation cases."""
    result = translate(input)
    assert result == expected
```

### Testing Exceptions

```python
def test_raises_exception(self) -> None:
    """Test that function raises expected exception."""
    with pytest.raises(ValidationError) as exc_info:
        invalid_function_call()

    assert "error message" in str(exc_info.value)
```

## Best Practices

### Do's ✅

- **Write descriptive test names**: `test_should_return_error_when_file_too_large`
- **Test one thing per test**: Each test should verify a single behavior
- **Use fixtures for setup**: Reuse common test data
- **Mock external dependencies**: Don't hit real APIs or file systems
- **Test edge cases**: Empty inputs, large inputs, invalid inputs
- **Add docstrings**: Explain what the test validates
- **Clean up resources**: Use fixtures with teardown

### Don'ts ❌

- **Don't test implementation details**: Test public behavior, not internal logic
- **Don't skip cleanup**: Always clean up temp files and resources
- **Don't use real API keys**: Use mocks or test keys
- **Don't write flaky tests**: Tests should be deterministic
- **Don't ignore test failures**: Fix broken tests immediately
- **Don't test multiple things in one test**: Split into separate tests

## CI/CD Integration

### GitHub Actions Workflow

Tests run automatically on:
- Push to `main`, `develop`, or feature branches
- Pull requests to `main` or `develop`

**Workflow file:** `.github/workflows/backend-tests.yml`

### Workflow Steps

1. **Setup**: Install Python, uv, FFmpeg
2. **Lint**: Run Ruff for code quality
3. **Type Check**: Run mypy for type safety
4. **Test**: Run pytest with coverage
5. **Report**: Upload coverage to Codecov
6. **Artifacts**: Save test results and coverage reports

### Required Secrets

Configure in GitHub repository settings:

- `OPENAI_API_KEY` (optional): For tests that need real API access
  - Tests use mocks by default, so this is not required

### Status Badges

Add to README.md:

```markdown
![Tests](https://github.com/username/repo/workflows/Backend%20Tests/badge.svg)
![Coverage](https://codecov.io/gh/username/repo/branch/main/graph/badge.svg)
```

## Troubleshooting

### Common Issues

**Issue: FFmpeg not found**
```
AudioProcessingError: Audio conversion failed
```
Solution: Install FFmpeg (see Prerequisites)

**Issue: Import errors**
```
ModuleNotFoundError: No module named 'backend'
```
Solution: Run tests from project root, ensure dependencies installed

**Issue: Fixture not found**
```
fixture 'mock_openai_service' not found
```
Solution: Check `conftest.py` has the fixture, or add to test file

**Issue: Tests hang**
```
Tests run indefinitely
```
Solution: Check for blocking I/O operations, ensure async tests use `@pytest.mark.asyncio`

**Issue: Coverage not generated**
```
No coverage report created
```
Solution: Ensure `pytest-cov` is installed, use `--cov=backend` flag

### Debug Tests

```bash
# Run with Python debugger
uv run pytest --pdb

# Drop into debugger on failure
uv run pytest --pdb -x

# Show print statements
uv run pytest -s

# Very verbose output
uv run pytest -vv
```

## Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [Testing Best Practices](https://docs.python-guide.org/writing/tests/)

## Contributing

When adding new features:

1. Write tests first (TDD approach)
2. Ensure tests pass locally
3. Add tests to appropriate category (unit/integration/security)
4. Update this documentation if needed
5. Verify coverage meets requirements
6. CI/CD pipeline must pass before merge

## Support

For issues or questions about testing:

- Open an issue on GitHub
- Contact the development team
- Check CI/CD logs for failure details
