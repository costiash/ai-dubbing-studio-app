# Legacy Files

This directory contains legacy files from earlier versions of the AI Dubbing Studio project.

## app.py (Streamlit Version)

**Status:** Deprecated
**Date Archived:** 2025-12-10
**Replaced By:** FastAPI backend (`/backend`) + JavaScript frontend (`/frontend`)

### What was it?

The original `app.py` was a single-file Streamlit application (144 lines) that provided:
- Audio upload and transcription
- Manual editing of transcripts
- Translation and TTS generation
- Download of generated audio

### Why was it replaced?

The project evolved from a simple Streamlit app to a professional full-stack application:

**Old Architecture (Streamlit):**
- Single Python file
- Streamlit UI framework
- Synchronous execution
- Session state management
- Limited scalability

**New Architecture (FastAPI + JavaScript):**
- Separate backend and frontend
- RESTful API design
- Async/await patterns
- Modern JavaScript UI
- Production-ready
- Scalable and testable

### Can I still use it?

Yes, the legacy Streamlit app is fully functional. To run it:

```bash
# Install dependencies
uv sync

# Run the Streamlit app
uv run streamlit run archive/legacy/app.py
```

**Note:** This version is no longer maintained. For production use, please use the new backend/frontend architecture.

### Migration Notes

If you're migrating from the legacy Streamlit app:

1. **API Endpoints:** The new backend uses RESTful endpoints instead of Streamlit session state
   - See `/docs/api/API_CONTRACT.md` for API documentation
2. **Configuration:** Environment variables are now managed in `.env` (same as before)
3. **Audio Processing:** Same audio conversion logic, now in `backend/utils/audio_converter.py`
4. **OpenAI Integration:** Same OpenAI models, now in `backend/services/openai_client.py`

### References

- **Current Documentation:** `/docs/README.md`
- **Migration Guide:** Contact the development team
- **Backend Code:** `/backend`
- **Frontend Code:** `/frontend`

---

**For all new development, use the FastAPI backend and JavaScript frontend.**
