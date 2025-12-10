/**
 * File Upload Manager
 *
 * Orchestrates file upload and transcription workflow.
 * Two-step process: Upload (store file) → Transcribe (process file).
 */
import { lockUI, unlockUI } from '../utils/ui-lock.js';

export class FileUploadManager {
  constructor(apiClient, uiStateManager, uiFeedbackManager, state, waveformVisualizer, sessionManager) {
    this.apiClient = apiClient;
    this.uiStateManager = uiStateManager;
    this.uiFeedbackManager = uiFeedbackManager;
    this.state = state;
    this.waveformVisualizer = waveformVisualizer;
    this.sessionManager = sessionManager;
    this.isTranscribing = false;
  }

  /**
   * Handle file selection (does NOT start transcription)
   * Shows file preview and transcribe button
   * @param {File} file - Uploaded audio file
   */
  async handleFileUpload(file) {
    console.log('File selected:', file.name);

    // Store file in state
    this.state.originalFile = file;
    this.state.originalAudioUrl = URL.createObjectURL(file);

    // Show file preview
    this.showFilePreview(file.name);

    // Show transcribe button
    this.showTranscribeButton();
  }

  /**
   * Show file preview with filename
   * @param {string} filename - Name of the uploaded file
   */
  showFilePreview(filename) {
    const filePreview = document.getElementById('file-preview');
    const filePreviewName = document.getElementById('file-preview-name');

    if (filePreview && filePreviewName) {
      filePreviewName.textContent = filename;
      filePreview.classList.remove('hidden');
    }
  }

  /**
   * Hide file preview
   */
  hideFilePreview() {
    const filePreview = document.getElementById('file-preview');
    if (filePreview) {
      filePreview.classList.add('hidden');
    }
  }

  /**
   * Show transcribe button
   */
  showTranscribeButton() {
    const transcribeBtn = document.getElementById('transcribe-btn');
    if (transcribeBtn) {
      transcribeBtn.classList.remove('hidden');
    }
  }

  /**
   * Hide transcribe button
   */
  hideTranscribeButton() {
    const transcribeBtn = document.getElementById('transcribe-btn');
    if (transcribeBtn) {
      transcribeBtn.classList.add('hidden');
    }
  }

  /**
   * Start transcription process
   * Called when user clicks the Transcribe button
   */
  async startTranscription() {
    // Guard against concurrent transcriptions
    if (this.isTranscribing) {
      console.warn('Transcription already in progress, ignoring duplicate request');
      this.uiFeedbackManager.showError('Transcription already in progress. Please wait.');
      return;
    }

    // Check if file is available
    if (!this.state.originalFile) {
      this.uiFeedbackManager.showError('No file selected. Please upload an audio file first.');
      return;
    }

    // Set guard flag
    this.isTranscribing = true;
    // Lock UI to prevent interaction during transcription
    lockUI('transcribing audio');

    // Hide transcribe button during processing
    this.hideTranscribeButton();

    // Show progress
    this.uiFeedbackManager.showUploadProgress();

    // Start waveform visualizer during transcription
    if (this.waveformVisualizer) {
      const waveformContainer = document.getElementById('waveform-container');
      if (waveformContainer) {
        waveformContainer.style.display = 'block';
      }
      this.waveformVisualizer.start();
    }

    try {
      // Get selected language from dropdown at the moment of transcription
      const languageSelect = document.getElementById('audio-language');
      const selectedLanguage = languageSelect?.value || null;

      console.log('Transcribing with language:', selectedLanguage || 'auto-detect');

      // Transcribe audio with optional language hint
      const result = await this.apiClient.transcribeAudio(this.state.originalFile, selectedLanguage);

      console.log('Transcription result:', result);

      this.state.transcription = result.text;
      this.state.sourceLanguage = result.language?.toLowerCase() || 'hebrew';

      // Save to session
      this.sessionManager.saveState('transcription', result.text);
      this.sessionManager.saveState('sourceLanguage', this.state.sourceLanguage);

      // Hide file preview after successful transcription
      this.hideFilePreview();

      // Show transcription section
      this.uiStateManager.showTranscriptionSection();

      // Hide upload progress
      this.uiFeedbackManager.hideUploadProgress();

      // Stop waveform visualizer after transcription completes
      if (this.waveformVisualizer) {
        this.waveformVisualizer.stop();
        const waveformContainer = document.getElementById('waveform-container');
        if (waveformContainer) {
          waveformContainer.style.display = 'none';
        }
      }

    } catch (error) {
      console.error('Transcription failed:', error);
      this.uiFeedbackManager.hideUploadProgress();
      this.uiFeedbackManager.showError(`Transcription failed: ${error.message}`);

      // Show transcribe button again on error so user can retry
      this.showTranscribeButton();

      // Stop waveform visualizer on error
      if (this.waveformVisualizer) {
        this.waveformVisualizer.stop();
        const waveformContainer = document.getElementById('waveform-container');
        if (waveformContainer) {
          waveformContainer.style.display = 'none';
        }
      }
    } finally {
      // Always reset guard flag and unlock UI
      this.isTranscribing = false;
      unlockUI();
    }
  }

  /**
   * Remove selected file (called when user clicks remove button)
   */
  removeFile() {
    // Clean up object URL
    if (this.state.originalAudioUrl) {
      URL.revokeObjectURL(this.state.originalAudioUrl);
    }

    // Clear state
    this.state.originalFile = null;
    this.state.originalAudioUrl = null;

    // Hide preview and button
    this.hideFilePreview();
    this.hideTranscribeButton();

    console.log('File removed');
  }

  /**
   * Reset upload state
   */
  reset() {
    this.isTranscribing = false;
    this.removeFile();
  }
}
