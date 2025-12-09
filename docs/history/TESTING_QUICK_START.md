# Testing Quick Start Guide

## 🚀 Get Started in 30 Seconds

```bash
# 1. Install dependencies
uv sync --group test

# 2. Run tests
uv run pytest

# 3. View coverage
open htmlcov/index.html
```

---

## 📋 Common Commands

### Run Tests

```bash
# All tests
uv run pytest

# Unit tests only
uv run pytest -m unit

# Integration tests only
uv run pytest -m integration

# Security tests only
uv run pytest -m security

# Specific file
uv run pytest backend/tests/test_config.py

# Specific test
uv run pytest backend/tests/test_config.py::TestSettings::test_settings_with_all_defaults

# With coverage
uv run pytest --cov=backend --cov-report=html

# Fast mode (skip slow tests)
uv run pytest -m "not slow"

# Verbose
uv run pytest -v

# Stop on first failure
uv run pytest -x

# Show failed tests only
uv run pytest --lf
```

### Using Test Runner Script

```bash
# Make executable (first time only)
chmod +x scripts/run-tests.sh

# Run tests
./scripts/run-tests.sh           # All tests
./scripts/run-tests.sh -u        # Unit tests
./scripts/run-tests.sh -i        # Integration tests
./scripts/run-tests.sh -s        # Security tests
./scripts/run-tests.sh -c        # With HTML coverage
./scripts/run-tests.sh -v        # Verbose
./scripts/run-tests.sh -f        # Fast (skip slow)
./scripts/run-tests.sh --lint    # Linting only
./scripts/run-tests.sh --type    # Type checking only
```

### Code Quality

```bash
# Linting
uv run ruff check backend/

# Auto-fix linting issues
uv run ruff check backend/ --fix

# Format code
uv run ruff format backend/

# Type checking
uv run mypy backend/
```

---

## 📊 Current Status

| Metric | Value |
|--------|-------|
| **Total Tests** | 114 tests |
| **Coverage** | 76.20% |
| **Target** | 80%+ |
| **Passing** | 85 tests |
| **Categories** | Unit, Integration, Security |

---

## 🏗️ Test Structure

```
backend/tests/
├── test_config.py              # Configuration tests (11 tests)
├── test_exceptions.py          # Exception tests (15 tests)
├── test_openai_client.py       # OpenAI service tests (23 tests)
├── test_audio_converter.py     # Audio conversion tests (12 tests)
├── test_file_handlers.py       # File utility tests (21 tests)
├── test_health_routes.py       # Health endpoint tests (13 tests)
├── test_audio_routes.py        # Audio route tests (24 tests)
├── integration/
│   └── test_complete_flows.py  # E2E workflow tests (12 tests)
└── security/
    └── test_input_validation.py # Security tests (19 tests)
```

---

## 🔧 Prerequisites

### Required

- **Python 3.13+**
- **uv** package manager
- **FFmpeg** (for audio conversion)

### Install FFmpeg

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# Verify installation
ffmpeg -version
```

---

## 📝 Writing Tests

### Basic Test Template

```python
import pytest

@pytest.mark.unit
class TestMyFeature:
    """Test suite for my feature."""

    def test_basic_functionality(self) -> None:
        """Test basic functionality."""
        # ARRANGE
        input_data = "test"

        # ACT
        result = my_function(input_data)

        # ASSERT
        assert result == "expected"
```

### Using Fixtures

```python
def test_with_fixtures(
    self,
    client: TestClient,
    mock_openai_service: OpenAIService,
) -> None:
    """Test using fixtures."""
    response = client.get("/health")
    assert response.status_code == 200
```

### Async Tests

```python
@pytest.mark.asyncio
async def test_async_function(self) -> None:
    """Test async function."""
    result = await async_function()
    assert result is not None
```

---

## 🎯 Test Markers

```python
@pytest.mark.unit          # Unit test
@pytest.mark.integration   # Integration test
@pytest.mark.security      # Security test
@pytest.mark.slow          # Slow-running test
```

---

## 🐛 Troubleshooting

### Common Issues

**Tests not found:**
```bash
# Ensure you're in project root
cd /path/to/ai-dubbing-studio-app
```

**FFmpeg not found:**
```bash
brew install ffmpeg  # macOS
sudo apt-get install ffmpeg  # Ubuntu
```

**Import errors:**
```bash
uv sync --group test
```

**Coverage not working:**
```bash
uv run pytest --cov=backend --cov-report=term-missing
```

---

## 📚 Documentation

- **Full Testing Guide:** `backend/tests/README.md`
- **Testing Summary:** `TESTING_SUMMARY.md`
- **CI/CD Workflow:** `.github/workflows/backend-tests.yml`

---

## 🔗 Useful Links

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Pytest Coverage](https://pytest-cov.readthedocs.io/)
- [Ruff Linter](https://docs.astral.sh/ruff/)

---

## 🎉 Quick Tips

1. **Run tests before committing:**
   ```bash
   ./scripts/run-tests.sh -u -f
   ```

2. **Check coverage:**
   ```bash
   uv run pytest --cov=backend --cov-report=term-missing
   ```

3. **Fix linting issues:**
   ```bash
   uv run ruff check backend/ --fix
   ```

4. **Debug failing test:**
   ```bash
   uv run pytest backend/tests/test_config.py -v --pdb
   ```

5. **Update test snapshots:**
   ```bash
   uv run pytest --snapshot-update
   ```

---

**Need Help?** Check `backend/tests/README.md` for detailed documentation.
