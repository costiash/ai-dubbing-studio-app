# AI Dubbing Studio & MCP Server Suite

## Project Overview

This project consists of two main components:
1.  **AI Dubbing Studio:** A Streamlit-based web application for automated audio dubbing (transcription, translation, TTS) using OpenAI models.
2.  **MCP Servers:** A collection of Model Context Protocol servers (`codex` and `gemini`) to enhance AI coding assistants (like Claude Code) with advanced capabilities.

## 1. AI Dubbing Studio (Web App)

### Architecture
-   **Framework:** Streamlit (Python 3.13+)
-   **Entry Point:** `app.py` (Single-file architecture)
-   **Core Dependencies:** `openai`, `pydub`, `audioop-lts`, `ffmpeg` (system)

### Workflow
1.  **Input:** User uploads audio (OGG, MP3, WAV, M4A).
2.  **Process:**
    *   Convert to MP3 (`convert_to_mp3`).
    *   Transcribe via `gpt-4o-transcribe` (Whisper).
    *   User reviews/edits text.
    *   Translate via `gpt-5.1`.
    *   Generate speech via `tts-1` or `tts-1-hd`.
3.  **Output:** Downloadable dubbed MP3.

### Usage
```bash
# Run the application
uv run streamlit run app.py
# Access at http://localhost:8501
```

### Key Implementation Rules
-   **State Management:** Use `st.session_state` for persistence (transcription, translation, audio path).
-   **Audio:** Always convert input to MP3 before processing. Use temp files.
-   **Security:** API keys must be in `.env` or user input, never hardcoded.

## 2. MCP Servers (`mcp_servers/`)

### A. Codex Server (`mcp_servers/codex/`)
Provides GPT-5.1-Codex-Max integration for high-level code analysis and fixing.

*   **Tools:**
    *   `codex_query`: General coding questions.
    *   `codex_analyzer`: Deep analysis of files/directories (focus: security, perf, arch).
    *   `codex_fixer`: Root-cause bug fixing.
*   **Config:** Requires `OPENAI_API_KEY`.

### B. Gemini CLI Server (`mcp_servers/gemini/`)
Wraps the Google Gemini CLI to provide Gemini capabilities to MCP clients.

*   **Tools:**
    *   `gemini_query`: One-shot queries.
    *   `gemini_code`: Code generation.
    *   `gemini_chat`: Multi-turn conversations (session managed).
*   **Context System:** Uses this `GEMINI.md` file to ground Gemini in project context.
*   **Config:** Requires `GEMINI_API_KEY`.

## Development Environment

### Package Management
*   **Tool:** `uv` (replaces pip/poetry).
*   **Commands:**
    *   `uv sync`: Install dependencies.
    *   `uv add <package>`: Add dependency.
    *   `uv run <command>`: Run command in venv.

### Code Quality
*   **Linting:** `uv run ruff check app.py --fix`
*   **Formatting:** `uv run ruff format app.py`
*   **Type Checking:** `uv run mypy app.py` (Strict type hints required)

### File Structure
```
/
├── app.py                    # Main Streamlit application
├── pyproject.toml            # Project dependencies & tool config
├── .env                      # Secrets (API keys) - gitignored
├── .mcp.json                 # MCP server registry
├── mcp_servers/
│   ├── codex/                # Codex MCP server implementation
│   └── gemini/               # Gemini CLI MCP server implementation
└── ai_docs/                  # Reference documentation for APIs
```

## Critical Conventions
1.  **Type Hints:** All functions must have Python 3.10+ style annotations.
2.  **Error Handling:** Catch specific exceptions and show user-friendly messages.
3.  **Path Handling:** Use `pathlib` or robust path joining.
4.  **Async:** MCP servers use `asyncio`; Streamlit app is synchronous.
