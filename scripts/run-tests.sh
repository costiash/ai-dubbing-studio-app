#!/bin/bash
# Test runner script for AI Dubbing Studio backend tests

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored message
print_msg() {
    local color=$1
    local msg=$2
    echo -e "${color}${msg}${NC}"
}

# Print usage
usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Run backend test suite for AI Dubbing Studio

OPTIONS:
    -h, --help              Show this help message
    -a, --all               Run all tests (default)
    -u, --unit              Run only unit tests
    -i, --integration       Run only integration tests
    -s, --security          Run only security tests
    -c, --coverage          Run with coverage report (HTML)
    -f, --fast              Run tests without slow tests
    -v, --verbose           Run with verbose output
    -w, --watch             Run in watch mode (requires pytest-watch)
    -x, --fail-fast         Stop on first failure
    --no-cov                Run without coverage
    --lint                  Run linting checks only
    --type                  Run type checking only

EXAMPLES:
    $0                      # Run all tests
    $0 -u                   # Run unit tests only
    $0 -c                   # Run all tests with HTML coverage report
    $0 -u -v                # Run unit tests with verbose output
    $0 -f                   # Run fast tests only (skip slow tests)
    $0 --lint               # Run linting checks

EOF
}

# Default options
RUN_ALL=true
RUN_UNIT=false
RUN_INTEGRATION=false
RUN_SECURITY=false
VERBOSE=false
COVERAGE=true
WATCH=false
FAIL_FAST=false
SKIP_SLOW=false
LINT_ONLY=false
TYPE_ONLY=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            exit 0
            ;;
        -a|--all)
            RUN_ALL=true
            shift
            ;;
        -u|--unit)
            RUN_ALL=false
            RUN_UNIT=true
            shift
            ;;
        -i|--integration)
            RUN_ALL=false
            RUN_INTEGRATION=true
            shift
            ;;
        -s|--security)
            RUN_ALL=false
            RUN_SECURITY=true
            shift
            ;;
        -c|--coverage)
            COVERAGE=true
            shift
            ;;
        -f|--fast)
            SKIP_SLOW=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -w|--watch)
            WATCH=true
            shift
            ;;
        -x|--fail-fast)
            FAIL_FAST=true
            shift
            ;;
        --no-cov)
            COVERAGE=false
            shift
            ;;
        --lint)
            LINT_ONLY=true
            shift
            ;;
        --type)
            TYPE_ONLY=true
            shift
            ;;
        *)
            print_msg "$RED" "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Check if we're in project root
if [ ! -f "pyproject.toml" ]; then
    print_msg "$RED" "Error: Must run from project root directory"
    exit 1
fi

# Linting only
if [ "$LINT_ONLY" = true ]; then
    print_msg "$BLUE" "Running linting checks..."
    uv run ruff check backend/ app.py
    print_msg "$GREEN" "✓ Linting passed!"
    exit 0
fi

# Type checking only
if [ "$TYPE_ONLY" = true ]; then
    print_msg "$BLUE" "Running type checking..."
    uv run mypy backend/
    print_msg "$GREEN" "✓ Type checking passed!"
    exit 0
fi

# Build test command
TEST_CMD="uv run pytest backend/tests/"

# Add markers
MARKERS=""
if [ "$RUN_ALL" = false ]; then
    if [ "$RUN_UNIT" = true ]; then
        MARKERS="unit"
    fi
    if [ "$RUN_INTEGRATION" = true ]; then
        [ -n "$MARKERS" ] && MARKERS="${MARKERS} or integration" || MARKERS="integration"
    fi
    if [ "$RUN_SECURITY" = true ]; then
        [ -n "$MARKERS" ] && MARKERS="${MARKERS} or security" || MARKERS="security"
    fi
    if [ -n "$MARKERS" ]; then
        TEST_CMD="${TEST_CMD} -m \"${MARKERS}\""
    fi
fi

# Skip slow tests
if [ "$SKIP_SLOW" = true ]; then
    TEST_CMD="${TEST_CMD} -m \"not slow\""
fi

# Add coverage
if [ "$COVERAGE" = true ]; then
    TEST_CMD="${TEST_CMD} --cov=backend --cov-report=term-missing"
    if [ "$RUN_ALL" = true ]; then
        TEST_CMD="${TEST_CMD} --cov-report=html --cov-report=xml"
    fi
fi

# Add verbose
if [ "$VERBOSE" = true ]; then
    TEST_CMD="${TEST_CMD} -v"
fi

# Add fail fast
if [ "$FAIL_FAST" = true ]; then
    TEST_CMD="${TEST_CMD} -x"
fi

# Watch mode
if [ "$WATCH" = true ]; then
    print_msg "$BLUE" "Running tests in watch mode..."
    uv run ptw backend/tests/
    exit 0
fi

# Print configuration
print_msg "$BLUE" "========================================"
print_msg "$BLUE" "  AI Dubbing Studio - Test Runner"
print_msg "$BLUE" "========================================"
echo ""
print_msg "$YELLOW" "Configuration:"
[ "$RUN_ALL" = true ] && echo "  • Running ALL tests"
[ "$RUN_UNIT" = true ] && echo "  • Running UNIT tests"
[ "$RUN_INTEGRATION" = true ] && echo "  • Running INTEGRATION tests"
[ "$RUN_SECURITY" = true ] && echo "  • Running SECURITY tests"
[ "$COVERAGE" = true ] && echo "  • Coverage reporting ENABLED"
[ "$VERBOSE" = true ] && echo "  • Verbose output ENABLED"
[ "$SKIP_SLOW" = true ] && echo "  • Skipping SLOW tests"
[ "$FAIL_FAST" = true ] && echo "  • Fail-fast ENABLED"
echo ""

# Check FFmpeg
print_msg "$BLUE" "Checking dependencies..."
if command -v ffmpeg &> /dev/null; then
    print_msg "$GREEN" "✓ FFmpeg found: $(ffmpeg -version | head -n1)"
else
    print_msg "$RED" "✗ FFmpeg not found (required for audio conversion tests)"
    print_msg "$YELLOW" "  Install: brew install ffmpeg (macOS) or apt-get install ffmpeg (Ubuntu)"
    exit 1
fi

# Set test API key if not set
if [ -z "$OPENAI_API_KEY" ]; then
    export OPENAI_API_KEY="sk-test-key-for-local-testing"
    print_msg "$YELLOW" "⚠ Using test API key (tests use mocks anyway)"
fi

# Run tests
print_msg "$BLUE" "Running tests..."
echo ""
eval $TEST_CMD
TEST_EXIT_CODE=$?

echo ""
if [ $TEST_EXIT_CODE -eq 0 ]; then
    print_msg "$GREEN" "========================================"
    print_msg "$GREEN" "  ✓ All tests passed!"
    print_msg "$GREEN" "========================================"

    if [ "$COVERAGE" = true ] && [ "$RUN_ALL" = true ]; then
        echo ""
        print_msg "$BLUE" "Coverage report saved to: htmlcov/index.html"
        print_msg "$BLUE" "View with: open htmlcov/index.html"
    fi
else
    print_msg "$RED" "========================================"
    print_msg "$RED" "  ✗ Tests failed!"
    print_msg "$RED" "========================================"
    exit 1
fi

exit 0
