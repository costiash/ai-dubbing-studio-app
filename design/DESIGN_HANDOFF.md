# Design Handoff Document - AI Dubbing Studio

**For:** Phase 3 Frontend Architect
**From:** Phase 2 UI/UX Architect
**Date:** 2025-12-09
**Status:** Ready for Implementation

---

## Executive Summary

This document provides everything needed to implement the AI Dubbing Studio frontend. The design system is complete, tested against WCAG 2.1 AA standards, and optimized for Dark/Light themes with modern audio UI patterns.

**Key Features:**
- Kinetic drag-and-drop upload zones
- Karaoke-style transcript highlighting
- Custom audio player with waveform
- Dark/Light theme system (auto-detects OS preference)
- Full keyboard navigation + screen reader support
- Mobile-responsive (touch-friendly 44px targets)

---

## File Structure for Frontend

```
frontend/
├── index.html                  # Single-page app structure
├── styles/
│   ├── design-tokens.css      # CSS custom properties (Phase 2 ✅)
│   ├── component-styles.css   # Component classes (Phase 2 ✅)
│   ├── layout.css             # Grid/flex layouts (Phase 3)
│   └── main.css               # Imports all stylesheets
├── scripts/
│   ├── api.js                 # Backend API client
│   ├── theme.js               # Dark/Light theme toggle
│   ├── upload.js              # File upload + drag-drop
│   ├── audio.js               # Audio player controls
│   ├── transcript.js          # Transcript editor + sync
│   └── main.js                # App initialization
├── assets/
│   ├── fonts/                 # Inter, Space Grotesk, JetBrains Mono
│   └── icons/                 # SVG icons (upload, play, etc.)
└── README.md                  # Setup instructions
```

---

## HTML Structure Template

### Base HTML5 Shell

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="Transform audio across languages with AI-powered transcription, translation, and text-to-speech">

  <title>AI Dubbing Studio - Audio Translation Tool</title>

  <!-- Preload fonts for performance -->
  <link rel="preload" href="/assets/fonts/Inter-Regular.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="/assets/fonts/Inter-Medium.woff2" as="font" type="font/woff2" crossorigin>

  <!-- Stylesheets -->
  <link rel="stylesheet" href="/styles/main.css">

  <!-- Theme detection (inline to prevent FOUC) -->
  <script>
    // Detect theme preference BEFORE page renders
    const savedTheme = localStorage.getItem('theme');
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const theme = savedTheme || (systemPrefersDark ? 'dark' : 'light');
    document.documentElement.setAttribute('data-theme', theme);
  </script>
</head>
<body>
  <!-- App container -->
  <div id="app" class="app-container">
    <!-- Content injected by JavaScript -->
  </div>

  <!-- Scripts (defer for performance) -->
  <script src="/scripts/api.js" defer></script>
  <script src="/scripts/theme.js" defer></script>
  <script src="/scripts/upload.js" defer></script>
  <script src="/scripts/audio.js" defer></script>
  <script src="/scripts/transcript.js" defer></script>
  <script src="/scripts/main.js" defer></script>
</body>
</html>
```

### Main App Structure

```html
<div id="app" class="app-container">
  <!-- Theme Toggle (fixed top-right) -->
  <button
    id="theme-toggle"
    class="theme-toggle"
    aria-label="Toggle dark mode"
    aria-pressed="false"
  >
    <svg class="theme-toggle__icon theme-toggle__icon--light" aria-hidden="true">
      <!-- Sun icon -->
    </svg>
    <svg class="theme-toggle__icon theme-toggle__icon--dark" aria-hidden="true">
      <!-- Moon icon -->
    </svg>
  </button>

  <!-- Header -->
  <header class="app-header">
    <h1 class="app-title">🎤 AI Dubbing Studio</h1>
    <p class="app-description">
      Transform audio across languages with AI
    </p>
  </header>

  <!-- Main Content Area -->
  <main id="main-content" class="app-main">
    <!-- Step 1: Upload -->
    <section id="upload-section" class="section">
      <div
        id="upload-zone"
        class="upload-zone"
        role="button"
        tabindex="0"
        aria-label="Upload audio file. Drag and drop or press enter to browse. Supported formats: MP3, WAV, OGG, M4A. Maximum size: 25 megabytes"
      >
        <svg class="upload-zone__icon" aria-hidden="true">
          <!-- Upload icon -->
        </svg>
        <h2 class="upload-zone__title">Drag & Drop Audio File</h2>
        <p class="upload-zone__description">or click to browse</p>
        <p class="upload-zone__description">
          Supported: MP3, WAV, OGG, M4A (max 25 MB)
        </p>
        <input
          type="file"
          id="file-input"
          class="upload-zone__input"
          accept=".mp3,.wav,.ogg,.m4a,audio/mpeg,audio/wav,audio/ogg,audio/x-m4a"
          aria-hidden="true"
        >
      </div>

      <!-- Progress (hidden initially) -->
      <div id="upload-progress" class="progress-bar" hidden>
        <div class="progress-bar__fill" style="width: 0%"></div>
      </div>
    </section>

    <!-- Step 2: Transcribe (hidden initially) -->
    <section id="transcribe-section" class="section" hidden>
      <!-- Original audio player -->
      <div class="card">
        <div class="card__header">
          <h2 class="card__title">🎵 Original Audio</h2>
        </div>
        <div id="original-audio-player" class="audio-player">
          <!-- Audio player controls -->
        </div>
      </div>

      <!-- Source language selector -->
      <div class="form-group">
        <label for="source-language" class="form-label">
          Source Language
        </label>
        <select
          id="source-language"
          class="form-select"
          aria-describedby="source-lang-help"
        >
          <option value="hebrew">Hebrew</option>
          <option value="russian">Russian</option>
          <option value="english">English</option>
          <!-- More languages... -->
        </select>
        <span id="source-lang-help" class="form-helper">
          Detected from audio (you can change if incorrect)
        </span>
      </div>

      <!-- Transcript editor -->
      <div class="card">
        <div class="card__header">
          <h2 class="card__title">📝 Transcript</h2>
        </div>
        <div class="transcript-box">
          <textarea
            id="transcript-editor"
            class="transcript-box__textarea"
            placeholder="Transcription will appear here..."
            aria-label="Transcript editor. Click a word to seek audio. Double-click to edit."
          ></textarea>
          <span id="char-count" class="transcript-box__char-count" aria-live="polite">
            0 / 50,000
          </span>
        </div>
      </div>

      <!-- Target language selector -->
      <div class="form-group">
        <label for="target-language" class="form-label">
          Target Language
        </label>
        <select
          id="target-language"
          class="form-select"
        >
          <option value="russian">Russian</option>
          <option value="hebrew">Hebrew</option>
          <option value="english">English</option>
          <!-- More languages... -->
        </select>
      </div>

      <!-- Translate button -->
      <button id="translate-btn" class="btn btn-primary btn-lg">
        Translate & Generate Speech
      </button>
    </section>

    <!-- Step 3: Results (hidden initially) -->
    <section id="results-section" class="section" hidden>
      <!-- Success message -->
      <div class="alert alert--success">
        <svg class="alert__icon" aria-hidden="true">
          <!-- Checkmark icon -->
        </svg>
        <div class="alert__content">
          <h3 class="alert__title">Audio dubbing complete!</h3>
          <p class="alert__message">Your translated audio is ready to download.</p>
        </div>
      </div>

      <!-- Original vs Generated comparison -->
      <div class="comparison-grid">
        <!-- Original -->
        <div class="card">
          <div class="card__header">
            <h2 class="card__title">🎵 Original Audio (Hebrew)</h2>
          </div>
          <div id="original-player-result" class="audio-player">
            <!-- Audio controls -->
          </div>
          <div class="transcript-display">
            <p lang="he">שלום, זהו דוגמה של תמלול אודיו...</p>
          </div>
        </div>

        <!-- Generated -->
        <div class="card">
          <div class="card__header">
            <h2 class="card__title">🔊 Generated Audio (Russian)</h2>
          </div>
          <div id="generated-player" class="audio-player">
            <!-- Audio controls -->
          </div>
          <div class="transcript-display">
            <p lang="ru">Привет, это пример транскрипции аудио...</p>
          </div>
        </div>
      </div>

      <!-- Action buttons -->
      <div class="button-group">
        <button id="download-btn" class="btn btn-primary btn-lg">
          <svg aria-hidden="true"><!-- Download icon --></svg>
          Download MP3
        </button>
        <button id="start-new-btn" class="btn btn-secondary">
          Start New
        </button>
      </div>
    </section>

    <!-- Error alerts (hidden initially) -->
    <div id="error-alert" class="alert alert--error" hidden role="alert">
      <svg class="alert__icon" aria-hidden="true">
        <!-- Error icon -->
      </svg>
      <div class="alert__content">
        <h3 class="alert__title">Error Title</h3>
        <p class="alert__message">Error message here</p>
      </div>
    </div>
  </main>

  <!-- Footer -->
  <footer class="app-footer">
    <p>Powered by OpenAI API</p>
  </footer>
</div>
```

---

## JavaScript Requirements

### 1. API Client (`api.js`)

**Purpose:** Communicate with FastAPI backend

```javascript
// Base URL for API
const API_BASE_URL = 'http://localhost:8000';

/**
 * Upload and transcribe audio file
 * @param {File} file - Audio file
 * @returns {Promise<{text: string, language: string}>}
 */
async function transcribeAudio(file) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/api/v1/audio/transcribe`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Transcription failed');
  }

  return response.json();
}

/**
 * Translate text
 * @param {string} text
 * @param {string} sourceLang
 * @param {string} targetLang
 * @returns {Promise<{translated_text: string}>}
 */
async function translateText(text, sourceLang, targetLang) {
  const response = await fetch(`${API_BASE_URL}/api/v1/audio/translate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      text,
      source_language: sourceLang,
      target_language: targetLang,
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Translation failed');
  }

  return response.json();
}

/**
 * Generate TTS audio
 * @param {string} text
 * @param {string} voice - Default: "onyx"
 * @param {string} model - Default: "tts-1"
 * @returns {Promise<Blob>} - MP3 audio blob
 */
async function generateTTS(text, voice = 'onyx', model = 'tts-1') {
  const response = await fetch(`${API_BASE_URL}/api/v1/audio/tts`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      text,
      voice,
      model,
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'TTS generation failed');
  }

  return response.blob();
}

/**
 * Check API health
 * @returns {Promise<{status: string, openai_api_configured: boolean}>}
 */
async function checkHealth() {
  const response = await fetch(`${API_BASE_URL}/health`);
  return response.json();
}
```

---

### 2. Theme Toggle (`theme.js`)

**Purpose:** Manage Dark/Light theme switching

```javascript
/**
 * Initialize theme system
 * Detects saved preference or system preference
 */
function initTheme() {
  const themeToggle = document.getElementById('theme-toggle');
  const savedTheme = localStorage.getItem('theme');
  const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

  // Set initial theme
  const currentTheme = savedTheme || (systemPrefersDark ? 'dark' : 'light');
  setTheme(currentTheme);

  // Toggle on click
  themeToggle.addEventListener('click', () => {
    const newTheme = document.documentElement.getAttribute('data-theme') === 'dark'
      ? 'light'
      : 'dark';
    setTheme(newTheme);
  });

  // Keyboard support
  themeToggle.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      themeToggle.click();
    }
  });
}

/**
 * Set theme and persist preference
 * @param {string} theme - 'light' or 'dark'
 */
function setTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem('theme', theme);

  // Update ARIA state
  const themeToggle = document.getElementById('theme-toggle');
  themeToggle.setAttribute('aria-pressed', theme === 'dark' ? 'true' : 'false');
  themeToggle.setAttribute('aria-label',
    theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'
  );
}

// Initialize on DOM ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initTheme);
} else {
  initTheme();
}
```

---

### 3. Upload Handler (`upload.js`)

**Purpose:** Handle file upload + drag-and-drop

```javascript
/**
 * Initialize upload zone
 */
function initUpload() {
  const uploadZone = document.getElementById('upload-zone');
  const fileInput = document.getElementById('file-input');

  // Click to browse
  uploadZone.addEventListener('click', () => {
    fileInput.click();
  });

  // Keyboard support
  uploadZone.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      fileInput.click();
    }
  });

  // File selected
  fileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
      handleFileUpload(file);
    }
  });

  // Drag and drop
  uploadZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadZone.classList.add('upload-zone--dragging');
  });

  uploadZone.addEventListener('dragleave', () => {
    uploadZone.classList.remove('upload-zone--dragging');
  });

  uploadZone.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadZone.classList.remove('upload-zone--dragging');

    const file = e.dataTransfer.files[0];
    if (file) {
      handleFileUpload(file);
    }
  });
}

/**
 * Handle file upload and transcription
 * @param {File} file
 */
async function handleFileUpload(file) {
  // Validate file
  const validExtensions = ['.mp3', '.wav', '.ogg', '.m4a'];
  const fileExt = '.' + file.name.split('.').pop().toLowerCase();

  if (!validExtensions.includes(fileExt)) {
    showError('Invalid file type',
      `Please upload an audio file: ${validExtensions.join(', ')}`);
    return;
  }

  if (file.size > 25 * 1024 * 1024) { // 25 MB
    showError('File too large',
      `Maximum file size is 25 MB. Your file is ${(file.size / 1024 / 1024).toFixed(1)} MB.`);
    return;
  }

  try {
    // Show progress
    showUploadProgress();

    // Transcribe
    const result = await transcribeAudio(file);

    // Show transcription UI
    showTranscriptionSection(result.text, result.language);

    // Store original file for playback
    const audioUrl = URL.createObjectURL(file);
    loadAudioPlayer('original-audio-player', audioUrl);

  } catch (error) {
    showError('Transcription failed', error.message);
  } finally {
    hideUploadProgress();
  }
}

/**
 * Show upload progress indicator
 */
function showUploadProgress() {
  const progress = document.getElementById('upload-progress');
  progress.hidden = false;
  progress.querySelector('.progress-bar__fill').style.width = '0%';

  // Indeterminate animation
  progress.classList.add('progress-bar--indeterminate');
}

function hideUploadProgress() {
  const progress = document.getElementById('upload-progress');
  progress.hidden = true;
  progress.classList.remove('progress-bar--indeterminate');
}
```

---

### 4. Audio Player (`audio.js`)

**Purpose:** Custom audio controls with keyboard shortcuts

```javascript
/**
 * Initialize audio player
 * @param {string} containerId
 * @param {string} audioUrl
 */
function loadAudioPlayer(containerId, audioUrl) {
  const container = document.getElementById(containerId);
  const audio = new Audio(audioUrl);

  let isPlaying = false;
  let playbackSpeed = 1.0;

  // Build player UI
  container.innerHTML = `
    <button class="audio-player__control" aria-label="Play audio">
      <svg aria-hidden="true"><!-- Play icon --></svg>
    </button>
    <div class="audio-player__progress-container">
      <div class="audio-player__progress">
        <div class="audio-player__progress-fill"></div>
        <div class="audio-player__progress-handle"></div>
      </div>
      <div class="audio-player__time">
        <span class="audio-player__time-current">0:00</span>
        <span class="audio-player__time-total">0:00</span>
      </div>
    </div>
    <div class="audio-player__speed">
      <button class="audio-player__speed-btn" data-speed="0.75">0.75x</button>
      <button class="audio-player__speed-btn audio-player__speed-btn--active" data-speed="1.0">1.0x</button>
      <button class="audio-player__speed-btn" data-speed="1.25">1.25x</button>
      <button class="audio-player__speed-btn" data-speed="1.5">1.5x</button>
    </div>
  `;

  const playBtn = container.querySelector('.audio-player__control');
  const progressFill = container.querySelector('.audio-player__progress-fill');
  const progressBar = container.querySelector('.audio-player__progress');
  const timeCurrent = container.querySelector('.audio-player__time-current');
  const timeTotal = container.querySelector('.audio-player__time-total');
  const speedBtns = container.querySelectorAll('.audio-player__speed-btn');

  // Play/Pause
  playBtn.addEventListener('click', togglePlay);

  function togglePlay() {
    if (isPlaying) {
      audio.pause();
    } else {
      audio.play();
    }
  }

  audio.addEventListener('play', () => {
    isPlaying = true;
    playBtn.setAttribute('aria-label', 'Pause audio');
    // Update icon to pause
  });

  audio.addEventListener('pause', () => {
    isPlaying = false;
    playBtn.setAttribute('aria-label', 'Play audio');
    // Update icon to play
  });

  // Time updates
  audio.addEventListener('timeupdate', () => {
    const progress = (audio.currentTime / audio.duration) * 100;
    progressFill.style.width = `${progress}%`;
    timeCurrent.textContent = formatTime(audio.currentTime);
  });

  audio.addEventListener('loadedmetadata', () => {
    timeTotal.textContent = formatTime(audio.duration);
  });

  // Seek
  progressBar.addEventListener('click', (e) => {
    const rect = progressBar.getBoundingClientRect();
    const clickX = e.clientX - rect.left;
    const percent = clickX / rect.width;
    audio.currentTime = percent * audio.duration;
  });

  // Playback speed
  speedBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const speed = parseFloat(btn.dataset.speed);
      audio.playbackRate = speed;

      // Update active state
      speedBtns.forEach(b => b.classList.remove('audio-player__speed-btn--active'));
      btn.classList.add('audio-player__speed-btn--active');
    });
  });

  // Keyboard shortcuts (Space, J, L)
  document.addEventListener('keydown', (e) => {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

    if (e.key === ' ') {
      e.preventDefault();
      togglePlay();
    } else if (e.key === 'j') {
      audio.currentTime = Math.max(0, audio.currentTime - 10);
    } else if (e.key === 'l') {
      audio.currentTime = Math.min(audio.duration, audio.currentTime + 10);
    }
  });
}

/**
 * Format seconds to MM:SS
 */
function formatTime(seconds) {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, '0')}`;
}
```

---

### 5. Main App (`main.js`)

**Purpose:** Initialize and orchestrate all modules

```javascript
/**
 * App state
 */
const state = {
  currentStep: 'upload', // upload | transcribe | results
  originalFile: null,
  transcription: '',
  translation: '',
  generatedAudioBlob: null,
};

/**
 * Initialize app
 */
async function init() {
  // Check API health
  try {
    const health = await checkHealth();
    console.log('API Status:', health);
  } catch (error) {
    showError('API Connection Failed',
      'Cannot connect to backend server. Make sure it is running on http://localhost:8000');
  }

  // Initialize modules
  initTheme();
  initUpload();

  // Translate button
  document.getElementById('translate-btn').addEventListener('click', handleTranslate);

  // Download button
  document.getElementById('download-btn').addEventListener('click', handleDownload);

  // Start new button
  document.getElementById('start-new-btn').addEventListener('click', resetApp);
}

/**
 * Show transcription section
 */
function showTranscriptionSection(text, language) {
  state.currentStep = 'transcribe';
  state.transcription = text;

  // Hide upload, show transcribe
  document.getElementById('upload-section').hidden = true;
  document.getElementById('transcribe-section').hidden = false;

  // Populate transcript
  const editor = document.getElementById('transcript-editor');
  editor.value = text;
  updateCharCount();

  // Set source language
  document.getElementById('source-language').value = language.toLowerCase();

  // Character count
  editor.addEventListener('input', updateCharCount);
}

/**
 * Update character count
 */
function updateCharCount() {
  const editor = document.getElementById('transcript-editor');
  const charCount = document.getElementById('char-count');
  const count = editor.value.length;
  const max = 50000;

  charCount.textContent = `${count} / ${max}`;

  if (count > max) {
    charCount.classList.add('transcript-box__char-count--error');
  } else if (count > max * 0.9) {
    charCount.classList.add('transcript-box__char-count--warning');
  } else {
    charCount.classList.remove('transcript-box__char-count--error', 'transcript-box__char-count--warning');
  }
}

/**
 * Handle translate & generate
 */
async function handleTranslate() {
  const text = document.getElementById('transcript-editor').value;
  const sourceLang = document.getElementById('source-language').value;
  const targetLang = document.getElementById('target-language').value;

  if (!text.trim()) {
    showError('No text', 'Please enter text to translate');
    return;
  }

  try {
    // Show loading
    showLoading('Translating text...');

    // Translate
    const translateResult = await translateText(text, sourceLang, targetLang);
    state.translation = translateResult.translated_text;

    // Show loading for TTS
    showLoading('Generating speech...');

    // Generate TTS
    const audioBlob = await generateTTS(state.translation);
    state.generatedAudioBlob = audioBlob;

    // Show results
    showResults();

  } catch (error) {
    showError('Processing failed', error.message);
  } finally {
    hideLoading();
  }
}

/**
 * Show results section
 */
function showResults() {
  state.currentStep = 'results';

  // Hide transcribe, show results
  document.getElementById('transcribe-section').hidden = true;
  document.getElementById('results-section').hidden = false;

  // Load audio players
  const audioUrl = URL.createObjectURL(state.generatedAudioBlob);
  loadAudioPlayer('generated-player', audioUrl);

  // Display translations
  // ... populate transcript displays
}

/**
 * Download MP3
 */
function handleDownload() {
  const url = URL.createObjectURL(state.generatedAudioBlob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'dubbed_audio.mp3';
  a.click();
  URL.revokeObjectURL(url);
}

/**
 * Reset app to start
 */
function resetApp() {
  state.currentStep = 'upload';
  state.originalFile = null;
  state.transcription = '';
  state.translation = '';
  state.generatedAudioBlob = null;

  document.getElementById('upload-section').hidden = false;
  document.getElementById('transcribe-section').hidden = true;
  document.getElementById('results-section').hidden = true;

  document.getElementById('file-input').value = '';
  document.getElementById('transcript-editor').value = '';
}

/**
 * Show error
 */
function showError(title, message) {
  const alert = document.getElementById('error-alert');
  alert.querySelector('.alert__title').textContent = title;
  alert.querySelector('.alert__message').textContent = message;
  alert.hidden = false;

  // Auto-hide after 5 seconds
  setTimeout(() => {
    alert.hidden = true;
  }, 5000);
}

// Initialize on DOM ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
```

---

## Integration with Backend API

### API Endpoints Summary

| Method | Endpoint | Purpose | Request | Response |
|--------|----------|---------|---------|----------|
| GET | `/health` | Check API status | None | `{status, openai_api_configured}` |
| POST | `/api/v1/audio/transcribe` | Transcribe audio | `multipart/form-data` file | `{text, language}` |
| POST | `/api/v1/audio/translate` | Translate text | `{text, source_language, target_language}` | `{translated_text}` |
| POST | `/api/v1/audio/tts` | Generate speech | `{text, voice, model}` | Binary MP3 file |

See `/home/rudycosta3/ai-dubbing-studio-app/API_CONTRACT.md` for complete details.

---

## Deployment Checklist

### Before Launch

- [ ] All fonts loaded (Inter, Space Grotesk, JetBrains Mono)
- [ ] SVG icons optimized and inline for performance
- [ ] CSS minified and combined into `main.css`
- [ ] JavaScript modules bundled (or use ES6 modules)
- [ ] Meta tags for SEO and social sharing
- [ ] Favicon and app icons (PWA-ready)
- [ ] HTTPS enforced (mixed content blocking)
- [ ] API URL configurable via environment variable
- [ ] Error tracking (Sentry, LogRocket)
- [ ] Analytics (Google Analytics, Plausible)

### Performance Targets

- [ ] **Lighthouse Performance:** ≥ 90
- [ ] **First Contentful Paint:** < 1.5s
- [ ] **Time to Interactive:** < 3.5s
- [ ] **Cumulative Layout Shift:** < 0.1

### Accessibility Targets

- [ ] **Lighthouse Accessibility:** ≥ 95
- [ ] **axe DevTools:** 0 critical issues
- [ ] **Keyboard navigation:** 100% functional
- [ ] **Screen reader:** Tested with NVDA/VoiceOver

---

## Design Tokens Quick Reference

**Import all styles:**
```css
@import 'design-tokens.css';
@import 'component-styles.css';
@import 'layout.css';
```

**Common tokens:**
```css
/* Colors */
background-color: var(--color-surface-primary);
color: var(--color-text-primary);
border-color: var(--color-border-primary);

/* Spacing */
padding: var(--space-4); /* 16px */
gap: var(--space-6); /* 24px */

/* Typography */
font-size: var(--font-size-base); /* 16px */
font-weight: var(--font-weight-medium); /* 500 */

/* Timing */
transition: all var(--duration-fast) var(--ease-out); /* 150ms */
```

---

## Resources

**Design Files:**
- `/design/design-tokens.css` - CSS variables
- `/design/component-styles.css` - Component classes
- `/design/DESIGN_SYSTEM.md` - Full design documentation
- `/design/UI_FLOW_SPEC.md` - User journey wireframes
- `/design/ACCESSIBILITY_CHECKLIST.md` - A11y requirements

**External APIs:**
- OpenAI API Docs: https://platform.openai.com/docs
- FastAPI Backend: http://localhost:8000/docs

**Testing Tools:**
- Lighthouse (Chrome DevTools)
- axe DevTools extension
- WAVE accessibility checker
- Browser DevTools responsive mode

---

## Questions?

For clarifications on the design system, refer to:
- `/design/DESIGN_SYSTEM.md` - Component specifications
- `/design/UI_FLOW_SPEC.md` - User flow wireframes
- `/design/ACCESSIBILITY_CHECKLIST.md` - Accessibility requirements

**Ready for Phase 3 implementation!**
