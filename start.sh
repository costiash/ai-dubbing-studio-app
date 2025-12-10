#!/bin/bash
#
# AI Dubbing Studio - Development Server Startup Script
# =====================================================
# This script starts both the backend (FastAPI) and frontend (HTTP server)
# with proper logging, health checks, and user-friendly terminal output.
#

set -e  # Exit on error

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_PORT=8000
FRONTEND_PORT=8080
BACKEND_LOG="$SCRIPT_DIR/backend.log"
FRONTEND_LOG="$SCRIPT_DIR/frontend.log"
HEALTH_CHECK_URL="http://localhost:$BACKEND_PORT/health"
FRONTEND_URL="http://localhost:$FRONTEND_PORT"
MAX_HEALTH_RETRIES=30
HEALTH_RETRY_INTERVAL=1

# ─────────────────────────────────────────────────────────────────────────────
# Colors and Formatting
# ─────────────────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
BOLD='\033[1m'
DIM='\033[2m'
NC='\033[0m' # No Color

# ─────────────────────────────────────────────────────────────────────────────
# Helper Functions
# ─────────────────────────────────────────────────────────────────────────────

print_header() {
    echo ""
    echo -e "${CYAN}╔═══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${NC}  ${BOLD}${WHITE}🎙️  AI Dubbing Studio - Development Environment${NC}            ${CYAN}║${NC}"
    echo -e "${CYAN}╚═══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_separator() {
    echo -e "${DIM}───────────────────────────────────────────────────────────────────${NC}"
}

print_step() {
    echo -e "${BLUE}▶${NC} ${BOLD}$1${NC}"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${DIM}  $1${NC}"
}

print_url() {
    echo -e "  ${MAGENTA}→${NC} ${BOLD}${CYAN}$1${NC}"
}

# ─────────────────────────────────────────────────────────────────────────────
# Cleanup Function (called on exit)
# ─────────────────────────────────────────────────────────────────────────────
cleanup() {
    echo ""
    print_separator
    print_step "Shutting down servers..."

    if [ -n "$BACKEND_PID" ] && kill -0 "$BACKEND_PID" 2>/dev/null; then
        kill "$BACKEND_PID" 2>/dev/null || true
        print_success "Backend server stopped (PID: $BACKEND_PID)"
    fi

    if [ -n "$FRONTEND_PID" ] && kill -0 "$FRONTEND_PID" 2>/dev/null; then
        kill "$FRONTEND_PID" 2>/dev/null || true
        print_success "Frontend server stopped (PID: $FRONTEND_PID)"
    fi

    echo ""
    print_success "All servers shut down gracefully"
    echo ""
    exit 0
}

# Trap SIGINT (Ctrl+C) and SIGTERM
trap cleanup SIGINT SIGTERM

# ─────────────────────────────────────────────────────────────────────────────
# Initialize Log Files
# ─────────────────────────────────────────────────────────────────────────────
initialize_logs() {
    print_step "Initializing log files..."

    # Create/overwrite log files with header
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    cat > "$BACKEND_LOG" << EOF
================================================================================
AI Dubbing Studio - Backend Server Log
Started: $timestamp
================================================================================

EOF
    print_success "Backend log initialized: ${DIM}backend.log${NC}"

    cat > "$FRONTEND_LOG" << EOF
================================================================================
AI Dubbing Studio - Frontend Server Log
Started: $timestamp
================================================================================

EOF
    print_success "Frontend log initialized: ${DIM}frontend.log${NC}"
}

# ─────────────────────────────────────────────────────────────────────────────
# Check Prerequisites
# ─────────────────────────────────────────────────────────────────────────────
check_prerequisites() {
    print_step "Checking prerequisites..."

    # Check if uv is installed
    if ! command -v uv &> /dev/null; then
        print_error "uv package manager is not installed"
        print_info "Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"
        exit 1
    fi
    print_success "uv package manager found"

    # Check if Python is available
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed"
        exit 1
    fi
    print_success "Python 3 found"

    # Check if .env file exists
    if [ ! -f "$SCRIPT_DIR/.env" ]; then
        print_warning ".env file not found - backend may fail to start"
        print_info "Create .env with OPENAI_API_KEY=sk-..."
    else
        print_success ".env configuration file found"
    fi

    # Check if frontend directory exists
    if [ ! -d "$SCRIPT_DIR/frontend" ]; then
        print_error "Frontend directory not found"
        exit 1
    fi
    print_success "Frontend directory found"
}

# ─────────────────────────────────────────────────────────────────────────────
# Start Backend Server
# ─────────────────────────────────────────────────────────────────────────────
start_backend() {
    print_step "Starting backend server (FastAPI)..."

    # Check if port is already in use
    if lsof -Pi :$BACKEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_warning "Port $BACKEND_PORT is already in use"
        local existing_pid=$(lsof -Pi :$BACKEND_PORT -sTCP:LISTEN -t 2>/dev/null | head -1)
        print_info "Killing existing process (PID: $existing_pid)..."
        kill "$existing_pid" 2>/dev/null || true
        sleep 1
    fi

    cd "$SCRIPT_DIR"

    # Start uvicorn in background
    uv run uvicorn backend.api.main:app \
        --host 0.0.0.0 \
        --port $BACKEND_PORT \
        --reload \
        >> "$BACKEND_LOG" 2>&1 &

    BACKEND_PID=$!

    print_info "Backend PID: $BACKEND_PID"
    print_info "Logging to: backend.log"
}

# ─────────────────────────────────────────────────────────────────────────────
# Start Frontend Server
# ─────────────────────────────────────────────────────────────────────────────
start_frontend() {
    print_step "Starting frontend server (HTTP)..."

    # Check if port is already in use
    if lsof -Pi :$FRONTEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_warning "Port $FRONTEND_PORT is already in use"
        local existing_pid=$(lsof -Pi :$FRONTEND_PORT -sTCP:LISTEN -t 2>/dev/null | head -1)
        print_info "Killing existing process (PID: $existing_pid)..."
        kill "$existing_pid" 2>/dev/null || true
        sleep 1
    fi

    cd "$SCRIPT_DIR/frontend"

    # Start Python HTTP server in background
    python3 -m http.server $FRONTEND_PORT \
        >> "$FRONTEND_LOG" 2>&1 &

    FRONTEND_PID=$!

    print_info "Frontend PID: $FRONTEND_PID"
    print_info "Logging to: frontend.log"
}

# ─────────────────────────────────────────────────────────────────────────────
# Health Check
# ─────────────────────────────────────────────────────────────────────────────
perform_health_check() {
    print_step "Performing API health check..."

    local retries=0
    local health_status=""

    echo -ne "  ${DIM}Waiting for backend to be ready"

    while [ $retries -lt $MAX_HEALTH_RETRIES ]; do
        # Check if backend process is still running
        if ! kill -0 "$BACKEND_PID" 2>/dev/null; then
            echo -e "${NC}"
            print_error "Backend process died unexpectedly"
            print_info "Check backend.log for details"
            echo ""
            echo -e "${YELLOW}Last 10 lines of backend.log:${NC}"
            tail -10 "$BACKEND_LOG"
            exit 1
        fi

        # Try health check
        health_status=$(curl -s -o /dev/null -w "%{http_code}" "$HEALTH_CHECK_URL" 2>/dev/null || echo "000")

        if [ "$health_status" = "200" ]; then
            echo -e "${NC}"
            break
        fi

        echo -ne "."
        sleep $HEALTH_RETRY_INTERVAL
        retries=$((retries + 1))
    done

    if [ "$health_status" != "200" ]; then
        echo -e "${NC}"
        print_error "Health check failed after $MAX_HEALTH_RETRIES attempts"
        print_info "Backend may not have started correctly"
        print_info "Check backend.log for details"
        exit 1
    fi

    # Get detailed health response
    local health_response=$(curl -s "$HEALTH_CHECK_URL" 2>/dev/null)
    local api_version=$(echo "$health_response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('version', 'unknown'))" 2>/dev/null || echo "unknown")
    local openai_configured=$(echo "$health_response" | python3 -c "import sys, json; print('Yes' if json.load(sys.stdin).get('openai_api_configured', False) else 'No')" 2>/dev/null || echo "unknown")

    print_success "Backend API is healthy"
    print_info "API Version: $api_version"
    print_info "OpenAI API Configured: $openai_configured"

    if [ "$openai_configured" = "No" ]; then
        print_warning "OpenAI API key not configured - some features will not work"
    fi
}

# ─────────────────────────────────────────────────────────────────────────────
# Display Final Status
# ─────────────────────────────────────────────────────────────────────────────
display_status() {
    echo ""
    print_separator
    echo ""
    echo -e "${GREEN}${BOLD}  🚀 All systems operational!${NC}"
    echo ""
    print_separator
    echo ""
    echo -e "${WHITE}${BOLD}  Server Status:${NC}"
    echo ""
    echo -e "  ${GREEN}●${NC} Backend (FastAPI)   Port: ${CYAN}$BACKEND_PORT${NC}   PID: ${DIM}$BACKEND_PID${NC}"
    echo -e "  ${GREEN}●${NC} Frontend (HTTP)     Port: ${CYAN}$FRONTEND_PORT${NC}   PID: ${DIM}$FRONTEND_PID${NC}"
    echo ""
    print_separator
    echo ""
    echo -e "${WHITE}${BOLD}  Access the Application:${NC}"
    echo ""
    print_url "$FRONTEND_URL"
    echo ""
    print_separator
    echo ""
    echo -e "${WHITE}${BOLD}  API Endpoints:${NC}"
    echo ""
    echo -e "  ${DIM}Health Check:${NC}    http://localhost:$BACKEND_PORT/api/health"
    echo -e "  ${DIM}API Docs:${NC}        http://localhost:$BACKEND_PORT/docs"
    echo -e "  ${DIM}Redoc:${NC}           http://localhost:$BACKEND_PORT/redoc"
    echo ""
    print_separator
    echo ""
    echo -e "${WHITE}${BOLD}  Log Files:${NC}"
    echo ""
    echo -e "  ${DIM}Backend:${NC}   tail -f backend.log"
    echo -e "  ${DIM}Frontend:${NC}  tail -f frontend.log"
    echo ""
    print_separator
    echo ""
    echo -e "${YELLOW}  Press Ctrl+C to stop all servers${NC}"
    echo ""
}

# ─────────────────────────────────────────────────────────────────────────────
# Main Execution
# ─────────────────────────────────────────────────────────────────────────────
main() {
    print_header

    print_separator
    initialize_logs

    print_separator
    check_prerequisites

    print_separator
    start_backend

    print_separator
    start_frontend

    print_separator
    perform_health_check

    display_status

    # Keep script running and wait for both processes
    wait $BACKEND_PID $FRONTEND_PID
}

# Run main function
main
