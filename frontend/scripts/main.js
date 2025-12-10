/**
 * Main Application - AI Dubbing Studio
 *
 * Orchestrates all modules and manages application state.
 * Handles the complete user workflow: Upload → Transcribe → Translate → TTS → Download
 */

import { apiClient } from './api.js';
import { themeManager } from './theme.js';
import { sessionManager } from './session.js';
import { UploadManager } from './upload.js';
import { loadAudioPlayer } from './audio.js';
import { initVisualEffects } from './visual-effects.js';
import { unlockUI } from './utils/ui-lock.js';

// Managers
import { UIStateManager } from './managers/UIStateManager.js';
import { UIFeedbackManager } from './managers/UIFeedbackManager.js';
import { FileUploadManager } from './managers/FileUploadManager.js';
import { AudioProcessingManager } from './managers/AudioProcessingManager.js';

// Services
import { HealthCheckService } from './services/HealthCheckService.js';

/**
 * Application state
 */
const state = {
  currentStep: 'upload', // 'upload' | 'transcribe' | 'results'
  originalFile: null,
  originalAudioUrl: null,
  transcription: '',
  translation: '',
  generatedAudioBlob: null,
  generatedAudioUrl: null,
  sourceLanguage: 'hebrew',
  targetLanguage: 'russian',
  voice: 'onyx',
  model: 'gpt-4o-mini-tts',
  instructions: '', // Voice style instructions for gpt-4o-mini-tts
  // Audio player instances
  originalPlayer: null,
  originalPlayerResult: null,
  generatedPlayer: null,
};

/**
 * Main Application class - App Coordinator
 */
class DubbingStudioApp {
  constructor() {
    this.initialized = false;

    // Initialize managers
    this.uiFeedbackManager = new UIFeedbackManager();
    this.uiStateManager = new UIStateManager(state, loadAudioPlayer);

    // Visual effects
    this.visualEffects = null;
    this.particleSystem = null;
    this.waveformVisualizer = null;
    this.audioReactiveUI = null;
    this.customCursor = null;

    // Services
    this.healthCheckService = new HealthCheckService(apiClient, this.uiFeedbackManager);

    // Workflow managers
    this.fileUploadManager = null;
    this.audioProcessingManager = null;

    // Upload manager
    this.uploadManager = null;
  }

  /**
   * Initialize application
   */
  async init() {
    if (this.initialized) return;

    console.log('Initializing AI Dubbing Studio...');

    // Check backend health
    await this.healthCheckService.checkBackendHealth();

    // Initialize theme manager
    themeManager.init();

    // Initialize visual effects (Phase 4: Sonic Laboratory)
    this.visualEffects = initVisualEffects();
    if (this.visualEffects) {
      this.particleSystem = this.visualEffects.particles;
      this.waveformVisualizer = this.visualEffects.waveform;
      this.audioReactiveUI = this.visualEffects.audioReactive;
      this.customCursor = this.visualEffects.customCursor;
    }

    // Initialize workflow managers (after visual effects)
    this.fileUploadManager = new FileUploadManager(
      apiClient,
      this.uiStateManager,
      this.uiFeedbackManager,
      state,
      this.waveformVisualizer,
      sessionManager
    );

    this.audioProcessingManager = new AudioProcessingManager(
      apiClient,
      this.uiStateManager,
      this.uiFeedbackManager,
      state,
      this.particleSystem,
      sessionManager
    );

    // Initialize upload manager
    this.setupUpload();

    // Set up event listeners
    this.setupEventListeners();

    // Set up custom event handlers
    this.setupCustomEvents();

    // Restore session if available
    this.restoreSession();

    this.initialized = true;
    console.log('Application initialized successfully');
  }

  /**
   * Set up upload functionality
   */
  setupUpload() {
    const uploadZone = document.getElementById('upload-zone');
    const fileInput = document.getElementById('file-input');

    this.uploadManager = new UploadManager(
      uploadZone,
      fileInput,
      (file) => this.fileUploadManager.handleFileUpload(file)
    );
  }

  /**
   * Set up event listeners
   */
  setupEventListeners() {
    // Transcribe button (starts transcription after file upload)
    const transcribeBtn = document.getElementById('transcribe-btn');
    transcribeBtn?.addEventListener('click', () => this.fileUploadManager.startTranscription());

    // File remove button (removes uploaded file)
    const fileRemoveBtn = document.getElementById('file-preview-remove');
    fileRemoveBtn?.addEventListener('click', () => this.fileUploadManager.removeFile());

    // Translate button
    const translateBtn = document.getElementById('translate-btn');
    translateBtn?.addEventListener('click', () => this.audioProcessingManager.handleTranslate(this.audioReactiveUI));

    // Download button
    const downloadBtn = document.getElementById('download-btn');
    downloadBtn?.addEventListener('click', () => this.audioProcessingManager.handleDownload());

    // Start new button
    const startNewBtn = document.getElementById('start-new-btn');
    startNewBtn?.addEventListener('click', () => this.resetApp());

    // Transcript editor character count
    const transcriptEditor = document.getElementById('transcript-editor');
    transcriptEditor?.addEventListener('input', () => this.uiStateManager.updateCharCount());

    // Error toast close button
    const errorToast = document.getElementById('error-toast');
    const closeBtn = errorToast?.querySelector('.toast__close');
    closeBtn?.addEventListener('click', () => {
      errorToast.classList.add('hidden');
    });

    // Language selectors
    const sourceLangSelect = document.getElementById('source-language');
    sourceLangSelect?.addEventListener('change', (e) => {
      state.sourceLanguage = e.target.value;
    });

    const targetLangSelect = document.getElementById('target-language');
    targetLangSelect?.addEventListener('change', (e) => {
      state.targetLanguage = e.target.value;
    });

    // Voice select
    const voiceSelect = document.getElementById('voice-select');
    voiceSelect?.addEventListener('change', (e) => {
      state.voice = e.target.value;
    });

    // Model select
    const modelSelect = document.getElementById('model-select');
    modelSelect?.addEventListener('change', (e) => {
      state.model = e.target.value;
      this.toggleInstructionsVisibility(e.target.value);
    });

    // Voice instructions
    const instructionsTextarea = document.getElementById('voice-instructions');
    instructionsTextarea?.addEventListener('input', (e) => {
      state.instructions = e.target.value;
    });

    // Initialize instructions visibility based on default model
    this.toggleInstructionsVisibility(state.model);
  }

  /**
   * Toggle visibility of voice instructions field based on selected model
   * @param {string} model - Selected TTS model
   */
  toggleInstructionsVisibility(model) {
    const instructionsGroup = document.getElementById('instructions-group');
    if (instructionsGroup) {
      if (model === 'gpt-4o-mini-tts') {
        instructionsGroup.classList.remove('hidden');
      } else {
        instructionsGroup.classList.add('hidden');
        // Clear instructions when switching to non-supporting model
        state.instructions = '';
        const textarea = document.getElementById('voice-instructions');
        if (textarea) textarea.value = '';
      }
    }
  }

  /**
   * Set up custom event handlers
   */
  setupCustomEvents() {
    // Listen for upload errors
    document.addEventListener('upload-error', (e) => {
      this.uiFeedbackManager.showError(e.detail.message);
    });
  }

  /**
   * Reset application to initial state
   */
  resetApp() {
    console.log('Resetting application...');

    // Clean up visual effects
    if (this.customCursor) {
      this.customCursor.destroy();
      // Reinitialize custom cursor
      const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
      if (!isMobile) {
        this.customCursor.init();
      }
    }

    // Stop any running visual effects
    if (this.particleSystem && this.particleSystem.isRunning) {
      this.particleSystem.stop();
    }
    if (this.waveformVisualizer && this.waveformVisualizer.isPlaying) {
      this.waveformVisualizer.stop();
    }
    if (this.audioReactiveUI && this.audioReactiveUI.isReacting) {
      this.audioReactiveUI.stop();
    }

    // Clean up audio players
    if (state.originalPlayer) {
      state.originalPlayer.destroy();
    }
    if (state.originalPlayerResult) {
      state.originalPlayerResult.destroy();
    }
    if (state.generatedPlayer) {
      state.generatedPlayer.destroy();
    }

    // Revoke object URLs
    if (state.originalAudioUrl) {
      URL.revokeObjectURL(state.originalAudioUrl);
    }
    if (state.generatedAudioUrl) {
      URL.revokeObjectURL(state.generatedAudioUrl);
    }

    // Reset state
    state.currentStep = 'upload';
    state.originalFile = null;
    state.originalAudioUrl = null;
    state.transcription = '';
    state.translation = '';
    state.generatedAudioBlob = null;
    state.generatedAudioUrl = null;
    state.originalPlayer = null;
    state.originalPlayerResult = null;
    state.generatedPlayer = null;

    // Clear session
    sessionManager.clearState();

    // Reset upload manager
    if (this.uploadManager) {
      this.uploadManager.reset();
    }

    // Reset workflow managers
    this.fileUploadManager.reset();
    this.audioProcessingManager.reset();

    // Reset UI state
    this.uiStateManager.reset();

    // Unlock UI and hide feedback
    unlockUI();
    this.uiFeedbackManager.hideLoading();
    this.uiFeedbackManager.hideUploadProgress();

    console.log('Application reset complete');
  }

  /**
   * Restore session from localStorage
   */
  restoreSession() {
    if (!sessionManager.hasState()) {
      return;
    }

    // Check if session is recent (less than 1 hour old)
    const sessionAge = sessionManager.getSessionAge();
    const oneHour = 60 * 60 * 1000;

    if (sessionAge > oneHour) {
      console.log('Session expired, clearing...');
      sessionManager.clearState();
      return;
    }

    console.log('Session found, but not restoring (file upload required)');
    // Note: We could restore transcription/translation, but original audio file
    // cannot be restored from localStorage, so user must re-upload
  }
}

/**
 * Initialize app when DOM is ready
 */
function initApp() {
  const app = new DubbingStudioApp();
  app.init();

  // Expose app instance for debugging
  window.dubbingStudio = app;
}

// Initialize on DOM ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initApp);
} else {
  initApp();
}
