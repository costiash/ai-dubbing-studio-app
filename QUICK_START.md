# Quick Start Guide - AI Dubbing Studio

Get the AI Dubbing Studio up and running in 5 minutes.

## Prerequisites Check

```bash
# 1. Check Python version (need 3.13+)
python --version

# 2. Check if uv is installed
uv --version

# 3. Check if FFmpeg is installed
ffmpeg -version

# 4. Verify you have an OpenAI API key
# Get one from: https://platform.openai.com/api-keys
```

If any are missing, see `DEPLOYMENT_GUIDE.md` for installation instructions.

---

## Setup (One-Time)

### Step 1: Create `.env` file

```bash
cd /home/rudycosta3/ai-dubbing-studio-app

# Create .env file with your API key
cat > .env << 'EOF'
OPENAI_API_KEY=sk-your-api-key-here
EOF

# IMPORTANT: Replace 'sk-your-api-key-here' with your actual key
```

### Step 2: Install Dependencies

```bash
# Install all Python dependencies
uv sync

# Verify installation
uv run python --version
```

---

## Running the App

### Start Backend (Terminal 1)

```bash
cd /home/rudycosta3/ai-dubbing-studio-app

uv run uvicorn backend.api.main:app --reload --port 8000
```

**Expected output**:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Start Frontend (Terminal 2)

Open a **new terminal** window:

```bash
cd /home/rudycosta3/ai-dubbing-studio-app/frontend

python server.py
```

**Expected output**:
```
╔══════════════════════════════════════════════════════════╗
║  AI Dubbing Studio - Frontend Server                    ║
╚══════════════════════════════════════════════════════════╝

Server running at:
  → http://localhost:3000

Press Ctrl+C to stop the server
```

---

## Access the App

Open your web browser and go to:

### http://localhost:3000

You should see the AI Dubbing Studio interface with:
- A drag-and-drop upload zone
- A theme toggle button in the top-right
- "AI Dubbing Studio" header

---

## Quick Test

### 1. Verify Backend Connection

The app should automatically check the backend on load. Look for:
- No error messages in the browser
- Console log: "Backend API Status: {status: 'healthy', ...}"

If you see "Cannot connect to backend", check that Terminal 1 is still running.

### 2. Test File Upload

**Option A: Drag and Drop**
1. Find an audio file on your computer (MP3, WAV, OGG, or M4A)
2. Drag it onto the upload zone
3. The zone should highlight when you hover over it
4. Drop the file

**Option B: Click to Browse**
1. Click anywhere in the upload zone
2. File picker opens
3. Select an audio file
4. Click "Open"

### 3. Wait for Transcription

- A progress bar appears
- Backend processes the audio (may take 5-30 seconds)
- Transcription appears in a text area
- Original audio player loads

### 4. Translate & Generate

1. Select target language (e.g., "Russian")
2. Choose a voice (default: "Onyx")
3. Click "Translate & Generate Speech"
4. Loading overlay shows progress
5. Results appear with original vs generated audio

### 5. Download

1. Click "Download MP3"
2. File downloads to your browser's download folder
3. Play it in your media player to verify it works

---

## Troubleshooting

### Issue: "Cannot connect to backend"

**Solution**:
```bash
# Check if backend is running
curl http://localhost:8000/health

# If not, start it in Terminal 1
cd /home/rudycosta3/ai-dubbing-studio-app
uv run uvicorn backend.api.main:app --reload --port 8000
```

### Issue: "OpenAI API key not configured"

**Solution**:
```bash
# Check .env file
cat .env | grep OPENAI_API_KEY

# Should show: OPENAI_API_KEY=sk-...
# If not, edit .env and add your key
```

### Issue: Port 8000 or 3000 already in use

**Solution**:
```bash
# Find process using port
lsof -i :8000  # or :3000

# Kill the process
kill -9 <PID>

# Or use different ports
uv run uvicorn backend.api.main:app --port 8001
python server.py 3001
```

### Issue: File upload fails

**Solutions**:
1. Check file is audio format (MP3, WAV, OGG, M4A)
2. Check file size (must be < 25 MB)
3. Try a different audio file
4. Check browser console for errors (F12 → Console)

### Issue: FFmpeg not found

**Solution**:
```bash
# Install FFmpeg
# macOS:
brew install ffmpeg

# Ubuntu/Debian:
sudo apt-get install ffmpeg

# Verify:
ffmpeg -version
```

---

## Development Tips

### View Backend API Docs

Open in browser:
```
http://localhost:8000/docs
```

Interactive Swagger UI with all endpoints documented.

### View Browser Console

Press `F12` or:
- Chrome/Firefox: Ctrl+Shift+I (Windows/Linux) or Cmd+Option+I (Mac)
- Safari: Cmd+Option+C

Check the Console tab for:
- Backend connection status
- API call results
- Any JavaScript errors

### Debug Application State

Open browser console (F12) and type:
```javascript
// Access app instance
window.dubbingStudio

// View current state
window.dubbingStudio.state

// Check theme
themeManager.getTheme()

// Check session
sessionManager.getState()
```

### Auto-Reload

Both servers support auto-reload:
- **Backend**: Uvicorn reloads on file changes (if `--reload` flag used)
- **Frontend**: Just refresh browser (Ctrl+R or Cmd+R)

---

## What to Test

Use the `TESTING_CHECKLIST.md` for a comprehensive 50-test checklist.

**Quick smoke test**:
1. [ ] Upload audio file
2. [ ] See transcription
3. [ ] Edit transcript
4. [ ] Change languages
5. [ ] Generate speech
6. [ ] Play both audios
7. [ ] Download result
8. [ ] Toggle theme
9. [ ] Start new project

---

## Getting Help

1. **Backend logs**: Check Terminal 1 for API errors
2. **Frontend logs**: Check browser console (F12)
3. **Documentation**:
   - `DEPLOYMENT_GUIDE.md` - Full deployment guide
   - `frontend/README.md` - Frontend documentation
   - `TESTING_CHECKLIST.md` - Testing guide
   - `API_CONTRACT.md` - API documentation

---

## Stopping the App

Press `Ctrl+C` in both terminal windows:

1. **Terminal 1** (Backend): Ctrl+C
2. **Terminal 2** (Frontend): Ctrl+C

---

## Next Steps

Once everything works:

1. **Test thoroughly**: Use `TESTING_CHECKLIST.md`
2. **Customize**: Edit colors in `frontend/styles/design-tokens.css`
3. **Deploy**: Follow `DEPLOYMENT_GUIDE.md` for production deployment
4. **Phase 4**: Visual refinement (fonts, animations, polish)

---

## One-Command Start (Future)

Create a start script for convenience:

```bash
# Create start.sh
cat > start.sh << 'EOF'
#!/bin/bash
cd /home/rudycosta3/ai-dubbing-studio-app
echo "Starting backend..."
uv run uvicorn backend.api.main:app --reload --port 8000 &
BACKEND_PID=$!
echo "Backend started (PID: $BACKEND_PID)"

cd frontend
echo "Starting frontend..."
python server.py &
FRONTEND_PID=$!
echo "Frontend started (PID: $FRONTEND_PID)"

echo ""
echo "✅ AI Dubbing Studio is running!"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
EOF

chmod +x start.sh

# Run with:
./start.sh
```

---

**Happy dubbing!** 🎤
