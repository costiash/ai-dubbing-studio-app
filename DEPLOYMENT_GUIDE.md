# AI Dubbing Studio - Complete Deployment Guide

This guide explains how to run the complete AI Dubbing Studio application (Backend + Frontend).

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    USER BROWSER                         │
│              http://localhost:3000                      │
│                                                         │
│  ┌───────────────────────────────────────────────┐    │
│  │  FRONTEND (Vanilla JavaScript)                 │    │
│  │  - HTML/CSS/JS                                 │    │
│  │  - Dark/Light Theme                            │    │
│  │  - Audio Player                                │    │
│  │  - Session Management                          │    │
│  └───────────┬───────────────────────────────────┘    │
│              │                                          │
└──────────────┼──────────────────────────────────────────┘
               │ Fetch API
               │ (JSON + FormData)
               ▼
┌─────────────────────────────────────────────────────────┐
│         BACKEND (FastAPI)                               │
│         http://localhost:8000                           │
│                                                         │
│  ┌───────────────────────────────────────────────┐    │
│  │  API Routes                                    │    │
│  │  - /api/v1/audio/transcribe (POST)            │    │
│  │  - /api/v1/audio/translate (POST)             │    │
│  │  - /api/v1/audio/tts (POST)                   │    │
│  │  - /health (GET)                               │    │
│  └───────────┬───────────────────────────────────┘    │
│              │                                          │
└──────────────┼──────────────────────────────────────────┘
               │
               │ OpenAI Python SDK
               ▼
┌─────────────────────────────────────────────────────────┐
│         OpenAI API                                      │
│         https://api.openai.com                          │
│                                                         │
│  - Whisper (gpt-4o-transcribe)                         │
│  - GPT-5.1 (translation)                               │
│  - TTS (tts-1, tts-1-hd)                               │
└─────────────────────────────────────────────────────────┘
```

## Prerequisites

### Required Software

1. **Python 3.13+** with `uv` package manager
   ```bash
   # Check Python version
   python --version  # Should be 3.13+

   # Install uv (if not already installed)
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **FFmpeg** (for audio processing)
   ```bash
   # macOS
   brew install ffmpeg

   # Ubuntu/Debian
   sudo apt-get install ffmpeg

   # Windows (using Chocolatey)
   choco install ffmpeg

   # Verify installation
   ffmpeg -version
   ```

3. **OpenAI API Key**
   - Get your API key from: https://platform.openai.com/api-keys
   - Required for transcription, translation, and TTS

### Optional Software

- **Git** (for version control)
- **Modern web browser** (Chrome 90+, Firefox 88+, Safari 14+)

## Installation

### Step 1: Clone/Navigate to Project

```bash
cd /home/rudycosta3/ai-dubbing-studio-app
```

### Step 2: Set Up Environment Variables

Create a `.env` file in the project root:

```bash
# .env
OPENAI_API_KEY=sk-your-api-key-here

# Optional configuration
APP_NAME="AI Dubbing Studio API"
DEBUG=false
API_VERSION=v1
MAX_UPLOAD_SIZE=26214400
TEMP_DIR=/tmp/ai-dubbing-studio
TRANSCRIPTION_MODEL=gpt-4o-transcribe
TRANSLATION_MODEL=gpt-5.1
TTS_MODEL_DEFAULT=tts-1
TTS_VOICE_DEFAULT=onyx
```

**Important**: Never commit `.env` to Git. It's already in `.gitignore`.

### Step 3: Install Backend Dependencies

```bash
# Sync all dependencies
uv sync

# Verify installation
uv run python --version
uv run pip list | grep openai
```

## Running the Application

### Option 1: Two Terminal Windows (Recommended for Development)

**Terminal 1 - Backend**
```bash
cd /home/rudycosta3/ai-dubbing-studio-app

# Start FastAPI backend with auto-reload
uv run uvicorn backend.api.main:app --reload --port 8000
```

**Terminal 2 - Frontend**
```bash
cd /home/rudycosta3/ai-dubbing-studio-app/frontend

# Start frontend server
python server.py
```

Then open your browser to:
- **Frontend**: http://localhost:3000
- **Backend API Docs**: http://localhost:8000/docs

### Option 2: Background Processes

**Start Backend in Background**
```bash
cd /home/rudycosta3/ai-dubbing-studio-app
nohup uv run uvicorn backend.api.main:app --port 8000 > backend.log 2>&1 &
echo $! > backend.pid
```

**Start Frontend in Background**
```bash
cd /home/rudycosta3/ai-dubbing-studio-app/frontend
nohup python server.py > frontend.log 2>&1 &
echo $! > frontend.pid
```

**Stop Background Processes**
```bash
# Stop backend
kill $(cat backend.pid)

# Stop frontend
kill $(cat frontend.pid)
```

### Option 3: Using Screen/Tmux (for SSH sessions)

```bash
# Start new screen session
screen -S dubbing-studio

# Window 1: Backend (Ctrl+A C to create new window)
cd /home/rudycosta3/ai-dubbing-studio-app
uv run uvicorn backend.api.main:app --reload --port 8000

# Window 2: Frontend (Ctrl+A C)
cd frontend
python server.py

# Detach: Ctrl+A D
# Reattach: screen -r dubbing-studio
```

## Verification Steps

### 1. Check Backend Health

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "openai_api_configured": true,
  "version": "v1"
}
```

### 2. Check Frontend is Serving

```bash
curl -I http://localhost:3000
```

Expected response:
```
HTTP/1.0 200 OK
Content-Type: text/html
...
```

### 3. Test Complete Workflow

1. Open http://localhost:3000 in your browser
2. Upload a short audio file (MP3, WAV, OGG, or M4A)
3. Wait for transcription to complete
4. Review and edit the transcript if needed
5. Select target language
6. Click "Translate & Generate Speech"
7. Play and compare original vs. generated audio
8. Download the dubbed MP3

## Troubleshooting

### Backend Issues

**Issue**: `ImportError: No module named 'openai'`

**Solution**:
```bash
uv sync
uv add openai
```

**Issue**: `FFmpeg not found`

**Solution**:
```bash
# Install FFmpeg (see Prerequisites section)
which ffmpeg  # Verify it's in PATH
```

**Issue**: `OpenAI API key not configured`

**Solution**:
```bash
# Check .env file exists
cat .env | grep OPENAI_API_KEY

# Ensure it starts with 'sk-'
# Get new key from https://platform.openai.com/api-keys
```

### Frontend Issues

**Issue**: `Failed to fetch` or CORS errors

**Solution**:
1. Ensure backend is running on port 8000
2. Check browser console for specific error
3. Verify CORS configuration in backend (`backend/api/main.py`)

**Issue**: Theme doesn't change

**Solution**:
```javascript
// Open browser console
localStorage.clear();
location.reload();
```

**Issue**: Audio player doesn't work

**Solution**:
1. Check browser console for errors
2. Verify audio file format is supported
3. Try in a different browser
4. Check browser audio permissions

### Network Issues

**Issue**: Cannot access from other devices

**Solution**:
```bash
# Backend: Allow external connections
uv run uvicorn backend.api.main:app --host 0.0.0.0 --port 8000

# Frontend: Use your local IP
python server.py
# Then access from: http://192.168.x.x:3000
```

**Issue**: Port already in use

**Solution**:
```bash
# Find process using port 8000
lsof -i :8000
# or
netstat -an | grep 8000

# Kill the process
kill -9 <PID>

# Or use different port
uv run uvicorn backend.api.main:app --port 8001
```

## Development Workflow

### Making Changes

**Backend Changes**:
1. Edit files in `backend/`
2. Uvicorn auto-reloads on save (if `--reload` flag used)
3. Test at http://localhost:8000/docs

**Frontend Changes**:
1. Edit files in `frontend/`
2. Refresh browser (no build step needed)
3. Use browser DevTools for debugging

### Code Quality Checks

```bash
# Backend linting
uv run ruff check backend/ --fix

# Backend formatting
uv run ruff format backend/

# Backend type checking
uv run mypy backend/

# Run all checks
uv run ruff check backend/ --fix && \
uv run ruff format backend/ && \
uv run mypy backend/
```

## Production Deployment

### Backend (FastAPI)

**Option 1: Docker**
```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY . .
RUN pip install uv && uv sync
CMD ["uv", "run", "uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Option 2: Gunicorn + Uvicorn Workers**
```bash
gunicorn backend.api.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120
```

**Option 3: Systemd Service**
```ini
# /etc/systemd/system/dubbing-backend.service
[Unit]
Description=AI Dubbing Studio Backend
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/ai-dubbing-studio-app
Environment="PATH=/path/to/uv/bin:/usr/bin"
ExecStart=/usr/bin/uv run uvicorn backend.api.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

### Frontend (Static Files)

**Option 1: Netlify**
```bash
# Deploy folder
cd frontend
netlify deploy --prod
```

**Option 2: Vercel**
```bash
cd frontend
vercel --prod
```

**Option 3: AWS S3 + CloudFront**
```bash
# Sync to S3 bucket
aws s3 sync frontend/ s3://your-bucket-name/ --delete

# Update API URL in scripts/api.js first!
```

**Option 4: Nginx**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    root /path/to/ai-dubbing-studio-app/frontend;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Environment-Specific Configuration

**Frontend API URL**:
Edit `frontend/scripts/api.js`:

```javascript
// Development
const API_BASE_URL = 'http://localhost:8000';

// Production
const API_BASE_URL = 'https://api.your-domain.com';

// Or use environment detection
const API_BASE_URL = window.location.hostname === 'localhost'
  ? 'http://localhost:8000'
  : 'https://api.your-domain.com';
```

## Monitoring

### Backend Logs

```bash
# Development
# Logs appear in terminal

# Production (systemd)
journalctl -u dubbing-backend -f

# Production (Docker)
docker logs -f container-name
```

### Frontend Logs

```bash
# Browser console
# Open DevTools (F12) → Console tab

# Network requests
# DevTools → Network tab
```

### Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# Frontend availability
curl -I http://localhost:3000

# Full workflow test (using httpie)
http POST http://localhost:8000/api/v1/audio/transcribe file@test.mp3
```

## Security Checklist

- [ ] OpenAI API key stored in `.env` (not committed to Git)
- [ ] `.env` in `.gitignore`
- [ ] CORS origins restricted in production
- [ ] HTTPS enabled in production
- [ ] File upload size limits enforced
- [ ] Rate limiting enabled (production)
- [ ] Error messages don't expose sensitive info
- [ ] Backend API behind authentication (production)

## Performance Tuning

### Backend

```python
# backend/api/main.py
# Increase worker count for production
workers = 4  # 2-4 per CPU core

# Adjust timeouts
timeout = 120  # seconds
```

### Frontend

1. **Enable compression** (gzip/brotli) on web server
2. **Minify CSS/JS** for production
3. **Use CDN** for static assets
4. **Enable browser caching**
5. **Lazy load images** (if any)

## Backup & Restore

### Configuration Backup

```bash
# Backup .env file
cp .env .env.backup

# Backup configuration
tar -czf config-backup.tar.gz .env pyproject.toml uv.lock
```

### Session Data

Session data is stored in browser localStorage (client-side only).

To preserve user sessions:
- Do not clear browser localStorage
- Session expires after 1 hour of inactivity

## Support

### Logs Location

- **Backend logs**: stdout (terminal or log file if redirected)
- **Frontend logs**: Browser console (F12 → Console)
- **System logs**: `/var/log/syslog` (Linux) or `journalctl`

### Debug Mode

**Backend**:
```bash
# Set debug mode in .env
DEBUG=true

# Or use environment variable
DEBUG=true uv run uvicorn backend.api.main:app --reload
```

**Frontend**:
```javascript
// Browser console
window.dubbingStudio  // Access app instance
window.dubbingStudio.state  // View current state
```

### Getting Help

1. Check logs (backend terminal + browser console)
2. Review this guide's Troubleshooting section
3. Check API documentation: http://localhost:8000/docs
4. Review frontend README: `frontend/README.md`
5. Check backend README: `backend/README.md`

---

## Quick Reference

### Start Development Environment
```bash
# Terminal 1
cd /home/rudycosta3/ai-dubbing-studio-app
uv run uvicorn backend.api.main:app --reload --port 8000

# Terminal 2
cd /home/rudycosta3/ai-dubbing-studio-app/frontend
python server.py
```

### Access Points
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- OpenAPI Spec: http://localhost:8000/openapi.json

### Stop Services
- Press `Ctrl+C` in each terminal window

---

**Ready to go!** Follow the steps above to run the complete AI Dubbing Studio application.
