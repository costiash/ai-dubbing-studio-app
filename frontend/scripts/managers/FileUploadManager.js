/**
 * File Upload Manager
 *
 * Orchestrates file upload and transcription workflow.
 * Single responsibility: Upload → Transcribe → Show transcription.
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
    this.isUploading = false;
  }

  /**
   * Handle file upload and transcription
   * @param {File} file - Uploaded audio file
   */
  async handleFileUpload(file) {
    // CRITICAL: Prevent concurrent uploads (race condition guard)
    if (this.isUploading) {
      console.warn('Upload already in progress, ignoring duplicate request');
      this.uiFeedbackManager.showError('Upload already in progress. Please wait.');
      return;
    }

    console.log('File selected:', file.name);

    // Set guard flag
    this.isUploading = true;
    // Lock UI to prevent interaction during upload
    lockUI('uploading and transcribing');

    this.state.originalFile = file;
    this.state.originalAudioUrl = URL.createObjectURL(file);

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
      // Transcribe audio
      const result = await this.apiClient.transcribeAudio(file);

      console.log('Transcription result:', result);

      this.state.transcription = result.text;
      this.state.sourceLanguage = result.language?.toLowerCase() || 'hebrew';

      // Save to session
      this.sessionManager.saveState('transcription', result.text);
      this.sessionManager.saveState('sourceLanguage', this.state.sourceLanguage);

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
      this.isUploading = false;
      unlockUI();
    }
  }

  /**
   * Reset upload state
   */
  reset() {
    this.isUploading = false;
  }
}
